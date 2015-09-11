#! python2
#-*- coding: utf-8 -*-

import select
import socket
import pickle
import traceback
import threading
import Queue

import config
import netref
import utils


# MSG_TYPE
MSG_REQUEST = 1
MSG_REPLY = 2
MSG_EXCEPTION = 3
MSG_SHUTDOWN = 4
msg_str = ('msg type str', 'request', 'reply', 'exception', 'shutdown')


# obj label
LABEL_VALUE = 1
LABEL_TUPLE = 2
LABEL_LOCAL_REF = 3
LABEL_REMOTE_REF = 4
LABEL_NOTIMPLEMENTED = 5
LABEL_ELLIPSIS = 6
LABEL_LIST = 7
LABEL_DICT = 8

simple_types = frozenset([type(None), int, long, bool, float, str, unicode, complex])


class Package(object):
    def __init__(self, msg, seq, action, data):
        self.msg = msg
        self.seq = seq
        self.action = action
        self.data = data

    def __cmp__(self, other):
        if self.seq < other.seq:
            return -1
        elif self.seq == other.seq:
            return 0
        return 1

    def unpack(self):
        return self.msg, self.seq, self.action, self.data

class Connection(object):
    ''' connection object based on socket, contains
    some functions that both server and client will use'''

    def __init__(self, buffer_size):
        self.__sock = None
        self.__buffer_size = buffer_size
        self.__seq_num = 1      # next request's sequence number
        self.__connected_lock = threading.Lock() # thread(shutdown) and thread(recv_forever)
        self.__connected = False

        self.__local_objects = utils.CountDict()
        self.__proxy_cache = {}
        self.__netref_classes_cache = {}

        self.__requests = Queue.Queue() # thread(service.handle_request) and thread(recv_forever)
        self.__replies_lock = threading.Lock()  # thread(sync_req) and thread(recv_forever)
        self.__replies = {}
        self.__reply_arrive = threading.Event()

    def __del__(self):
        self.shutdown()

    # network control
    # start
    # ...
    def accept(self, server_sock):
        client_sock, address = server_sock.accept()
        self.__sock = client_sock
        self.connected = True
        self.__start_recv()
        return address

    def connect(self, server_address):
        if self.connected:
            self.shutdown()
        while True:
            try:
                print 'connecting'
                self.__sock = socket.create_connection(server_address, timeout=1)
                if self.__sock:
                    self.connected = True
                    self.__start_recv()
                    break
            except socket.timeout:
                print 'timeout'
            except:
                traceback.print_exc()
                raise
        return self.connected

    def __start_recv(self):
        self.__recv_thread = threading.Thread(target=self.__recv_forever)
        self.__recv_thread.start()

    def __recv_forever(self):
        while True:
            res = self.recv(0)
            if res is not None:
                pkg = Package(*res)
                msg_type, seq_num, action_type, data = res
                if msg_type == MSG_REQUEST:
                    self.__requests.put(pkg)
                elif msg_type == MSG_REPLY:
                    self.__replies_lock.acquire()
                    try:
                        self.__replies[seq_num] = pkg
                        self.__reply_arrive.set()
                    finally:
                        self.__replies_lock.release()
                elif msg_type == MSG_SHUTDOWN:
                    self.shutdown(True)
                    return
            if not self.connected:
                break

    def shutdown(self, in_thread = False, flag = socket.SHUT_RDWR):
        if self.connected:
            self.connected = False
            if not in_thread:
                self.__recv_thread.join()
            self.__sock.shutdown(flag)
            self.__local_objects.clear()
            self.__proxy_cache = {}
            self.__netref_classes_cache = {}
            self.__sock = None
            self.__seq_num = 1
            self.__recv_thread = None
            self.__requests = Queue.Queue()
            self.__replies = {}
    # ...
    # end
    # network control

    # send functions
    # start
    # ...
    def send_request(self, action_type, data):
        res = self.__send(MSG_REQUEST, self.__seq_num, action_type, data)
        if res > 0:
            self.__seq_num += 1
        return res

    def send_reply(self, seq_num, action_type, data):
        return self.__send(MSG_REPLY, seq_num, action_type, data)

    def send_shutdown(self):
        try:
            return self.__send(MSG_SHUTDOWN, 0, 0, 0)
        except socket.error:
            return -1

    def send_exception(self, data):
        pass

    def __send(self, msg_type, seq_num, action_type, data):
        if self.connected == False:
            return -1
        pickled_data = pickle.dumps((msg_type, seq_num, action_type,
            self.__box(data)))
        self.__sock.sendall(pickled_data)
        return seq_num

    def __box(self, obj):
        if type(obj) in simple_types:
            return LABEL_VALUE, obj
        elif obj is NotImplemented:     # pickle cannot dump NotImplemented
            return LABEL_NOTIMPLEMENTED, None
        elif obj is Ellipsis:           # pickle cannot dump Ellipsis
            return LABEL_ELLIPSIS, None
        elif type(obj) is tuple:
            return LABEL_TUPLE, tuple(self.__box(item) for item in obj)
        elif isinstance(obj, netref.NetRef) and obj.____conn__ is self:
            return LABEL_LOCAL_REF, obj.____oid__
        else:
            self.__local_objects.add(obj)
            try:
                cls = obj.__class__
            except:
                cls = type(obj)
            return LABEL_REMOTE_REF, (id(obj), cls.__name__, cls.__module__)
    # ...
    # end
    # send functions
        
    # recv functions
    # start
    # ...
    def recv(self, timeout = -1.0):
        if self.connected == False:
            return None
        if timeout < 0:
            ready = select.select([self.__sock], [], []);
        else:
            ready = select.select([self.__sock], [], [], timeout);
        if ready[0]:
            pickled_data = self.__sock.recv(self.__buffer_size)
            # 接收全部数据
            ready = select.select([self.__sock], [], [], 0)
            while ready[0]:
                rest_data = self.__sock.recv(self.__buffer_size)
                if rest_data is None:
                    break
                pickled_data = "".join([pickled_data, rest_data])
                ready = select.select([self.__sock], [self.__sock], [], 0)
            msg_type, seq_num, action_type, data = pickle.loads(pickled_data)
            try:
                unboxed_data = self.__unbox(data)
                return msg_type, seq_num, action_type, unboxed_data
            except KeyError:
                # send 'object has been del'
                pass
        return None

    def __unbox(self, package):
        label, value = package
        if label == LABEL_VALUE:
            return value
        elif label == LABEL_TUPLE:
            return tuple(self.__unbox(item) for item in value)
        elif label == LABEL_NOTIMPLEMENTED:
            return NotImplemented
        elif label == LABEL_ELLIPSIS:
            return Ellipsis
        elif label == LABEL_LOCAL_REF:
            try:
                obj = self.__local_objects[value]
            except KeyError:
                raise
            else:
                return obj
        elif label == LABEL_REMOTE_REF:
            oid, clsname, modname = value
            if oid in self.__proxy_cache:
                return self.__proxy_cache[oid]
            else:
                proxy = self.__netref_factory(oid, clsname, modname)
                self.__proxy_cache[oid] = proxy
                return proxy
        else:
            raise ValueError("invalid label {}".format(label))

    def __netref_factory(self, oid, clsname, modname):
        typeinfo = (clsname, modname)
        cls = netref.class_factory(clsname, modname)
        self.__netref_classes_cache[typeinfo] = cls
        return cls(self, oid)
    # ...
    # end
    # recv functions

    # useful functions
    # start
    # ...
    def get_request(self):
        if not self.connected:
            return None
        try:
            pkg = self.__requests.get(block=False)
        except Queue.Empty:
            return None
        return pkg.unpack()
    
    def get_reply(self, seq):
        if not self.connected:
            return None
        self.__replies_lock.acquire()
        try:
            res = self.__replies[seq]
            del self.__replies[seq]
            return res.unpack()
        except KeyError:
            return None
        finally:
            self.__replies_lock.release()

    def sync_request(self, action_type, data=None):
        if not self.connected:
            return None
        seq_num = self.send_request(action_type, data)
        if seq_num < 0:
            return None
        while True:
            reply = self.get_reply(seq_num)
            if reply is None:
                self.__reply_arrive.wait()
            else:
                msg_type, seq_num, action_type, data = reply
                return data

    @property
    def connected(self):
        self.__connected_lock.acquire()
        try:
            return self.__connected
        finally:
            self.__connected_lock.release()

    @connected.setter
    def connected(self, value):
        self.__connected_lock.acquire()
        try:
            self.__connected = value
        finally:
            self.__connected_lock.release()

    def del_local_object(self, obj):
        del self.__local_objects[id(obj)]
    # ...
    # end
    # useful functions
