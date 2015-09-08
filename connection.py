#! python2
#-*- coding: utf-8 -*-

import select
import socket
import config
import netref
import pickle
import weakref
import traceback


# MSG_TYPE
MSG_REQUEST = 1
MSG_REPLY = 2
MSG_EXCEPTION = 3
MSG_SHUTDOWN = 4
msg_str = ('msg type str', 'request', 'reply', 'exception', 'shutdown')

# Action_Type
ACTION_GETATTR = 1
ACTION_SETATTR = 2
ACTION_DELATTR = 3
ACTION_STR = 4
ACTION_REPR = 5
ACTION_CALL = 6
ACTION_GETSERVERPROXY = 7
ACTION_DIR = 8
ACTION_CMP = 9
ACTION_HASH = 10
action_str = ('action type str', 'getattr', 'setattr', 'delattr', 
        'str', 'repr', 'call', 'server_proxy', 'dir', 'cmp', 'hash')

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


class Connection(object):
    ''' connection object based on socket, contains
    some functions that both server and client will use'''

    def __init__(self, buffer_size):
        self.__sock = None
        self.__buffer_size = buffer_size
        self.__seq_num = 1      # next request's sequence number
        self.__connected = False

        self.__local_objects = {}  # on server
        self.__proxy_cache = {}    # on client
        self.__netref_classes_cache = {}  # on client

    def __del__(self):
        self.shutdown()

    # network control
    # start
    # ...
    def accept(self, server_sock):
        client_sock, address = server_sock.accept()
        self.__sock = client_sock
        self.__connected = True
        return self.__connected

    def connect(self, server_address):
        if self.__connected:
            return self.__connected
        while True:
            try:
                print 'connecting'
                self.__sock = socket.create_connection(server_address, timeout=1)
                if self.__sock:
                    self.__connected = True
                    break
            except socket.timeout:
                print 'timeout'
            except:
                traceback.print_exc()
                raise
        return self.__connected

    def shutdown(self, flag = socket.SHUT_RDWR):
        if self.__connected:
            self.__sock.shutdown(flag)
            self.local_object = {}
            self.__proxy_cache = {}
            self.__netref_classes_cache = {}
            self.__sock = None
            self.__seq_num = 1
            self.__connected = False
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
        return self.__send(MSG_SHUTDOWN, 0, 0, 0)

    def send_exception(self, data):
        pass

    def __send(self, msg_type, seq_num, action_type, data):
        if self.__connected == False:
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
        elif type(obj) is list:
            return LABEL_LIST, tuple(self.__box(item) for item in obj)
        elif type(obj) is dict:
            return LABEL_DICT, tuple(self.__box(item) for item in obj.items())
        elif isinstance(obj, netref.NetRef) and obj.____conn__ is self:
            return LABEL_LOCAL_REF, obj.____oid__
        else:
            self.__local_objects[id(obj)] = obj
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
        if self.__connected == False:
            return None
        if timeout < 0:
            ready = select.select([self.__sock], [], []);
        else:
            ready = select.select([self.__sock], [], [], timeout);
        if ready[0]:
            pickled_data = self.__sock.recv(self.__buffer_size)
            # 接收全部数据
            # socket 关闭后，ready[0]==[rlist], ready[1]==[]
            # 未关闭的socket, ready[0]==[rlist], ready[1]==[wlist]
            ready = select.select([self.__sock], [self.__sock], [], 0)
            while ready[0] and ready[1]:
                print 're recv'
                print ready
                pickled_data = "".join([pickled_data, self.__sock.recv(self.__buffer_size)])
                ready = select.select([self.__sock], [self.__sock], [], 0)

            msg_type, seq_num, action_type, data = pickle.loads(pickled_data)
            try:
                unboxed_data = self.__unbox(data)
                if msg_type == MSG_SHUTDOWN:
                    self.shutdown()
                    print 'connection shutdown'
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
        elif label == LABEL_LIST:
            return list(self.__unbox(item) for item in value)
        elif label == LABEL_DICT:
            return dict(self.__unbox(item) for item in value)
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
    def sync_request(self, action_type, data=None):
        seq_num = self.send_request(action_type, data)
        if seq_num < 0:
            return None
        msg_type, recv_seq_num, action_type, recv_data = self.recv()
        if msg_type == MSG_REPLY and recv_seq_num == seq_num:
            return recv_data
        return None

    @property
    def connected(self):
        return self.__connected
    # ...
    # end
    # useful functions
