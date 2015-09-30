#! python2
#-*- coding: utf-8 -*-

import select
import socket
import pickle
import traceback
import collections
import types
import threading
try:
    import queue as Queue
except:
    import Queue

import netref
import utils
from config import config


simple_types = frozenset([type(None), int, long, bool, float, str, unicode, complex])


class Connection(object):
    ''' connection object based on socket, contains
    some functions that both server and client will use'''

    def __init__(self, buffer_size):
        self.__sock = None
        self.__buffer_size = buffer_size
        self.__seq_num = 1      # next request's sequence number
        self.__connected = False

        self.__local_objects = utils.CountDict()  # on server
        self.requests_cache = Queue.PriorityQueue()     # on server

        self.__proxy_cache = {}    # on client
        self.__netref_classes_cache = {}  # on client
        self.replies_cache = Queue.PriorityQueue()   # on client

    def __del__(self):
        self.shutdown()

    # network control
    # start
    # ...
    def accept(self, server_sock):
        client_sock, address = server_sock.accept()
        self.__sock = client_sock
        self.__connected = True
        self.__recv_thread = threading.Thread(target=self.__recv_forever)
        self.__recv_thread.start()
        return address

    def connect(self, server_address):
        if self.__connected:
            self.shutdown()
        while True:
            try:
                print 'connecting'
                self.__sock = socket.create_connection(server_address, timeout=1)
                if self.__sock:
                    self.__connected = True
                    print 'connected'
                    self.__recv_thread = threading.Thread(target=self.__recv_forever)
                    self.__recv_thread.start()
                    break
            except socket.timeout:
                print 'timeout'
            except:
                traceback.print_exc()
                raise
        return self.__connected

    def shutdown(self, flag = socket.SHUT_RDWR):
        if self.__connected:
            try:
                self.send_shutdown()
                self.__connected = False
                if hasattr(self, '_Connection__recv_thread'):
                    self.__recv_thread.join()
                    print 'joined'
                self.__sock.shutdown(flag)
            except:
                pass
            self.__local_objects.clear()
            self.__proxy_cache = {}
            self.__netref_classes_cache = {}
            self.__sock = None
            self.__seq_num = 1
    # ...
    # end
    # network control

    # send functions
    # start
    # ...
    def send_request(self, action_type, data):
        boxed_data = self.__box_request(data)
        res = self.__send(config.msg.request, self.__seq_num, action_type, boxed_data)
        if res > 0:
            self.__seq_num += 1
        else:
            self.shutdown()
        return res

    def send_reply(self, seq_num, action_type, data):
        boxed_data = self.__box_reply(data)
        res = self.__send(config.msg.reply, seq_num, action_type, boxed_data)
        if res > 0:
            return res
        self.shutdown()
        return -1

    def send_shutdown(self):
        try:
            return self.__send(config.msg.shutdown, 0, 0, 0)
        except socket.error:
            return -1

    def send_exception(self, seq_num, data):
        res = self.__send(config.msg.exception, seq_num, 0, data)
        if res > 0:
            return res
        self.shutdown()
        return -1

    def __send(self, msg_type, seq_num, action_type, boxed_data):
        if self.__connected == False:
            return -1
        try:
            pickled_data = pickle.dumps((msg_type, seq_num, action_type, boxed_data))
        except:
            print 'data cannot be pickled'
            raise
        data_size = len(pickled_data)
        if data_size > 99999999:
            raise ValueError, 'data size is too large'
        try:
            self.__sock.sendall(str(data_size).zfill(8) + pickled_data)
        except socket.error:
            print 'socket error, shutdown'
            return -1
        return seq_num

    def __box_request(self, obj):
        if obj is NotImplemented:     # pickle cannot dump NotImplemented
            return config.label.notimplemented, None
        elif obj is Ellipsis:           # pickle cannot dump Ellipsis
            return config.label.ellipsis, None
        elif type(obj) is tuple:
            return config.label.tuple, tuple(self.__box_request(item) for item in obj)
        elif type(obj) is list:
            return config.label.list, tuple(self.__box_request(item) for item in obj)
        elif type(obj) is dict:
            return config.label.dict, tuple(self.__box_request(item) for item in obj.items())
        elif isinstance(obj, netref.NetRef) and obj.____conn__ is self:
            return config.label.local_ref, obj.____oid__
        else:
            return config.label.value, obj

    def __box_reply(self, obj):
        if type(obj) in simple_types:
            return config.label.value, obj
        elif obj is NotImplemented:     # pickle cannot dump NotImplemented
            return config.label.notimplemented, None
        elif obj is Ellipsis:           # pickle cannot dump Ellipsis
            return config.label.ellipsis, None
        elif type(obj) is tuple:
            return config.label.tuple, tuple(self.__box_reply(item) for item in obj)
        else:
            self.__local_objects.add(obj)
            try:
                cls = obj.__class__
            except:
                cls = type(obj)
            return config.label.remote_ref, (id(obj), cls.__name__, cls.__module__)
    # ...
    # end
    # send functions
        
    # recv functions
    # start
    # ...
    def recv(self, timeout = None):
        if self.__connected == False:
            return None
        data_size = 0
        recvd_size = 0

        # get data size
        ready = select.select([self.__sock], [], [], timeout);
        if ready[0]:
            data_size = self.__sock.recv(8)
            if not data_size:   # peer closed
                self.shutdown()
                return None
            else:
                data_size = int(data_size)
        else:
            return None

        # get data
        pickled_data = ""
        while data_size > recvd_size:
            ready = select.select([self.__sock], [], [], 1.0);
            if ready[0]:
                rest_data = self.__sock.recv(data_size - recvd_size)
                if not rest_data:   # peer closed
                    self.shutdown()
                    return None
                recvd_size += len(rest_data)
                pickled_data = "".join([pickled_data, rest_data])
                
        # unbox data
        msg_type, seq_num, action_type, data = pickle.loads(pickled_data)
        try:
            unboxed_data = None
            if msg_type == config.msg.request:
                unboxed_data = self.__unbox(data, True)
            elif msg_type == config.msg.reply:
                unboxed_data = self.__unbox(data, False)
            elif msg_type == config.msg.exception:
                unboxed_data = data
            elif msg_type == config.msg.shutdown:
                self.shutdown()
            return msg_type, seq_num, action_type, unboxed_data
        except KeyError:
            # send 'object has been del'
            pass
        return None

    def __unbox(self, package, unpick_dl):
        label, value = package
        if label == config.label.value:
            return value
        elif label == config.label.tuple:
            return tuple(self.__unbox(item, unpick_dl) for item in value)
        elif label == config.label.list and unpick_dl:
            return list(self.__unbox(item, unpick_dl) for item in value)
        elif label == config.label.dict and unpick_dl:
            return dict(self.__unbox(item, unpick_dl) for item in value)
        elif label == config.label.notimplemented:
            return NotImplemented
        elif label == config.label.ellipsis:
            return Ellipsis
        elif label == config.label.local_ref:
            try:
                obj = self.__local_objects[value]
            except KeyError:
                raise
            else:
                return obj
        elif label == config.label.remote_ref:
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

    def __recv_forever(self):
        while self.__connected:
            res = self.recv()
            if res is None:
                return res
            msg_type, seq_num, action_type, data = res
            if msg_type == config.msg.request:
                self.requests_cache.put((seq_num, res))
            elif msg_type == config.msg.reply:
                self.replies_cache.put((seq_num, res))
            elif msg_type == config.msg.exception:
                self.replies_cache.put((seq_num, res))

    # ...
    # end
    # recv functions

    # useful functions
    # start
    # ...
    def sync_request(self, action_type, data=None, need_reply=True):
        data = (need_reply, data)
        seq_num = self.send_request(action_type, data)
        if seq_num < 0 or not need_reply:
            return None
        while True:
            if self.replies_cache.empty():
                continue
            msg_type, recv_seq_num, action_type, recv_data = self.replies_cache.get()[1]
            if seq_num < recv_seq_num:
                self.replies_cache.put((recv_seq_num, (msg_type, recv_seq_num, action_type, recv_data)))
                print seq_num, recv_seq_num
                continue
            if seq_num > recv_seq_num:
                continue
            if msg_type == config.msg.reply:
                return recv_data
            if msg_type == config.msg.exception:
                if isinstance(recv_data, Exception):
                    return recv_data
                elif isinstance(recv_data, types.StringType):
                    return Exception(recv_data)
            return None

    @property
    def connected(self):
        return self.__connected

    def del_local_object(self, obj):
        del self.__local_objects[id(obj)]
    # ...
    # end
    # useful functions
