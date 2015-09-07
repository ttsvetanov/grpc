#! python2
#-*- coding: utf-8 -*-

import logging
import socket
import config
import connection
import threading
import traceback

# server mode
ACTIVE_MODE = 1
PASSIVE_MODE = 2

class ModuleNamespace(object):
    __slots__ = ["__getmodule", "__cache", "__weakref__"]
    def __init__(self, getmodule):
        self.__getmodule = getmodule
        self.__cache = {}
    def __getitem__(self, name):
        if type(name) is tuple:
            name = ".".join(name)
        print name, name not in self.__cache
        if name not in self.__cache or self.__cache[name] is None:
            self.__cache[name] = self.__getmodule(name)
            print self.__cache[name]
        return self.__cache[name]
    def __getattr__(self, name):
        print 'getattr__', name
        return self[name]


class GrpcServer(object):
    def __init__(self, server_port = config.DEFAULT_SERVER_PORT):
        self.__server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_sock.bind(('localhost', server_port))
        self.__server_sock.listen(5)
        self.modules = ModuleNamespace(self.__get_module)
        self.__mode = ACTIVE_MODE
        self.__conns = []
        self.__conns_lock = threading.Lock()
        self.__serve = False

        self.test = 2

    def foo(self):
        print 'foo'
        return 'foo'

    def serve_forever(self, mode=ACTIVE_MODE):
        if self.__serve == False:
            self.__mode = mode
            self.__serve = True
            if self.__mode == ACTIVE_MODE:
                t = threading.Thread(target=self.__handle_request_active)
                t.start()
            while self.__serve:
                conn = connection.Connection(config.SERVER_BUFFER_SIZE)
                if conn.accept(self.__server_sock):
                    self.__conns_lock.acquire()
                    self.__conns.append(conn)
                    self.__conns_lock.release()

    def shutdown(self):
        if self.__serve == True:
            self.__serve = False
            self.__conns_lock.acquire()
            for conn in self.__conns:
                conn.send_shutdown()
                conn.shutdown()
            self.__conns.clear()
            self.__conns_lock.release()

    def __handle_request_active(self):
        while self.__serve:
            self.handle_request()

    def handle_request(self):
        self.__conns_lock.acquire()
        for i in range(len(self.__conns)):
            self.__handle_request_once(i)
        self.__conns_lock.release()

    def __handle_request_once(self, index):
        conn = self.__conns[index]
        wait = -1 if self.__mode == ACTIVE_MODE else 0
        res = conn.recv(timeout=wait)
        if res is None:
            return res
        msg_type, seq_num, action_type, data = res
        print (connection.msg_str[msg_type], seq_num,
                connection.action_str[action_type], data)
        res = None
        if msg_type == connection.MSG_REQUEST:
            if action_type == connection.ACTION_GETATTR:
                res = self.__handle_getattr(data)
            elif action_type == connection.ACTION_SETATTR:
                res = self.__handle_setattr(data)
            elif action_type == connection.ACTION_DELATTR:
                res = self.__handle_delattr(data)
            elif action_type == connection.ACTION_STR:
                res = self.__handle_str(data)
            elif action_type == connection.ACTION_REPR:
                res = self.__handle_repr(data)
            elif action_type == connection.ACTION_GETSERVERPROXY:
                res = self.__handle_get_server_proxy(data)
            elif action_type == connection.ACTION_CALL:
                res = self.__handle_call(data)
            elif action_type == connection.ACTION_DIR:
                res = self.__handle_dir(data)
            elif action_type == connection.ACTION_CMP:
                res = self.__handle_cmp(data)
            elif action_type == connection.ACTION_HASH:
                res = self.__handle_hash(data)
        elif msg_type == connection.MSG_SHUTDOWN:
            self.__conns.pop(index)
        conn.send_reply(seq_num, action_type, res)

    def __handle_getattr(self, data):
        obj, attr_name = data
        try:
            attr = getattr(obj, attr_name)
            return attr
        except:
            traceback.print_exc()
        return None

    def __handle_setattr(self, data):
        obj, attr_name, value = data
        setattr(obj, attr_name, value)

    def __handle_delattr(self, data):
        obj, attr_name = data
        delattr(boj, attr_name)

    def __handle_str(self, data):
        obj = data
        return str(obj)

    def __handle_repr(self, data):
        obj = data
        return repr(obj)

    def __handle_get_server_proxy(self, data):
        return self

    def __handle_call(self, data):
        func, args, kwargs = data
        res = None
        try:
            res = func(*args, **kwargs)
        except:
            logging.error("__handle_call error. function:{}".format(str(func)))
            traceback.print_exc()
        return res

    def __handle_dir(self, data):
        obj = data
        return dir(obj)

    def __handle_cmp(self, data):
        obj, other = data
        try:
            return type(obj).__cmp__(obj, other)
        except (AttributeError, TypeError):
            return NotImplemented

    def __handle_hash(self, data):
        obj = data
        return hash(obj)

    def __get_module(self, name):
        return __import__(name, None, None, '*')

    def eval(self, text):
        return eval(text)

    def execute(self, text):
        exec text


if __name__ == '__main__':
    server = GrpcServer()
    server.serve_forever()
