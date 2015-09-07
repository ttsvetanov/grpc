#! python2
#-*- coding: utf-8 -*-

import logging
import socket
import config
import connection
import threading


class ModuleNamespace(object):
    __slots__ = ["__getmodule", "__cache", "__weakref__"]
    def __init__(self, getmodule):
        self.__getmodule = getmodule
        self.__cache = {}
    def __getitem__(self, name):
        if type(name) is tuple:
            name = ".".join(name)
        if name not in self.__cache:
            self.__cache[name] = self.__getmodule(name)
        return self.__cache[name]
    def __getattr__(self, name):
        return self[name]


class GrpcServer(object):
    def __init__(self, server_port = config.DEFAULT_SERVER_PORT):
        self.test = 2
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind(('localhost', server_port))
        self.server_sock.listen(5)
        self.modules = ModuleNamespace(self.get_module)

    def foo(self):
        print 'foo'
        return 'foo'

    def serve_forever(self):
        while True:
            conn = connection.Connection(config.SERVER_BUFFER_SIZE)
            if conn.accept(self.server_sock):
                t = threading.Thread(target=self.handle_request, args=(conn,))
                t.start()

    def handle_request(self, conn):
        while True:
            msg_type, seq_num, action_type, data = conn.recv()
            print (connection.msg_str[msg_type], seq_num,
                    connection.action_str[action_type], data)
            res = None
            if msg_type == connection.MSG_REQUEST:
                if action_type == connection.ACTION_GETATTR:
                    res = self.handle_getattr(data)
                elif action_type == connection.ACTION_SETATTR:
                    res = self.handle_setattr(data)
                elif action_type == connection.ACTION_DELATTR:
                    res = self.handle_delattr(data)
                elif action_type == connection.ACTION_STR:
                    res = self.handle_str(data)
                elif action_type == connection.ACTION_REPR:
                    res = self.handle_repr(data)
                elif action_type == connection.ACTION_GETSERVERPROXY:
                    res = self.handle_get_server_proxy(data)
                elif action_type == connection.ACTION_CALL:
                    res = self.handle_call(data)
                elif action_type == connection.ACTION_DIR:
                    res = self.handle_dir(data)
            elif msg_type == connection.MSG_SHUTDOWN:
                conn.shutdown()
                del conn
                break
            conn.send_reply(seq_num, action_type, res)

    def handle_getattr(self, data):
        obj, attr_name = data
        if hasattr(obj, attr_name):
            attr = getattr(obj, attr_name)
            return attr
        else:
            print 'Cannot find attr: {}'.format(attr_name)
        return None

    def handle_setattr(self, data):
        obj, attr_name, value = data
        setattr(obj, attr_name, value)

    def handle_delattr(self, data):
        obj, attr_name = data
        delattr(boj, attr_name)

    def handle_str(self, data):
        obj = data
        return str(obj)

    def handle_repr(self, data):
        obj = data
        return repr(obj)

    def handle_get_server_proxy(self, data):
        return self

    def handle_call(self, data):
        func, args, kwargs = data
        res = None
        try:
            res = func(*args, **kwargs)
        except:
            logging.error("handle_call error. function:{}".format(str(func)))
        return res

    def handle_dir(self, data):
        obj = data
        return dir(obj)

    def handle_cmp(self, data):
        obj, other = data
        try:
            return type(obj).__cmp__(obj, other)
        except (AttributeError, TypeError):
            return NotImplemented

    def handle_hash(self, data):
        obj = data
        return hash(obj)

    def get_module(self, name):
        return __import__(name, None, None, '*')

    def eval(self, text):
        return eval(text)

    def execute(self, text):
        exec text


if __name__ == '__main__':
    server = GrpcServer()
    server.serve_forever()
