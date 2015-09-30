#! python2
#-*- coding: utf-8 -*-

import logging
import socket
import threading
import traceback
import select
try:
    import queue as Queue
except:
    import Queue

from config import config
import connection


class ModuleNamespace(object):
    #__slots__ = ["__getmodule", "__cache"]
    def __init__(self, getmodule):
        self.__getmodule = getmodule
        self.__cache = {}
    def __getitem__(self, name):
        if type(name) is tuple:
            name = ".".join(name)
        if name not in self.__cache or self.__cache[name] is None:
            self.__cache[name] = self.__getmodule(name)
        return self.__cache[name]
    def __getattr__(self, name):
        return self[name]


class GrpcServer(object):
    def __init__(self, server_port = config.server.port):
        self.__server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__server_sock.bind(('localhost', server_port))
        self.__server_sock.listen(5)
        self.modules = ModuleNamespace(self.__get_module)
        self.__conns = []
        self.__conns_lock = threading.Lock()
        self.__serve = False
        self.__serve_thread = threading.Thread(target=self.__serve_forever)

        self.test = 2
        self.d = {}
        self.l = []

    def __del__(self):
        self.shutdown()

    def foo(self):
        print 'foo'
        return 'foo'

    def p(self, arg):
        print arg

    def start(self):
        self.__serve_thread.start()

    def __serve_forever(self):
        if self.__serve == False:
            self.__serve = True
            while self.__serve:
                ready = select.select([self.__server_sock], [], [], 0.5)
                if ready[0]:
                    conn = connection.Connection(config.server.buf_size)
                    client_addr = conn.accept(self.__server_sock)
                    print 'Hello, ', client_addr
                    self.__conns_lock.acquire()
                    try:
                        self.__conns.append(conn)
                    finally:
                        self.__conns_lock.release()

    def shutdown(self):
        if self.__serve == True:
            self.__serve = False

            self.__conns_lock.acquire()
            try:
                for conn in self.__conns:
                    conn.shutdown()
                self.__conns = []
            finally:
                self.__conns_lock.release()
            self.__serve_thread.join()
            self.__server_sock.close()

    def handle_request(self):
        for conn in self.__conns:
            if not conn.connected:
                self.__del_conn(conn)
                continue
            self.__handle_request_for_conn(conn)
            
    def __del_conn(self, conn):
        self.__conns_lock.acquire()
        try:
            self.__conns.remove(conn)
        except ValueError:
            pass
        finally:
            self.__conns_lock.release()
        print 'Bye, ', conn

    def __handle_request_for_conn(self, conn):
        while True:
            request = None
            try:
                request = conn.requests_cache.get_nowait()[1]
            except Queue.Empty:
                return None
            msg_type, seq_num, action_type, data = request
            print config.msg_str[msg_type], seq_num, config.action_str[action_type]
            try:
                print data
            except:
                pass
            res = None
            if msg_type == config.msg.request:
                need_reply, data = data
                res = self.__dispatch_request(conn, action_type, data)
                if not need_reply:
                    return None
            if isinstance(res, Exception):
                conn.send_exception(seq_num, res)
            else:
                conn.send_reply(seq_num, action_type, res)

    def __dispatch_request(self, conn, action_type, data):
        res = None
        if action_type == config.action.getattr:
            res = self.__handle_getattr(data)
        elif action_type == config.action.setattr:
            res = self.__handle_setattr(data)
        elif action_type == config.action.delattr:
            res = self.__handle_delattr(data)
        elif action_type == config.action.str:
            res = self.__handle_str(data)
        elif action_type == config.action.repr:
            res = self.__handle_repr(data)
        elif action_type == config.action.serverproxy:
            res = self.__handle_serverproxy(data)
        elif action_type == config.action.call:
            res = self.__handle_call(data)
        elif action_type == config.action.dir:
            res = self.__handle_dir(data)
        elif action_type == config.action.cmp:
            res = self.__handle_cmp(data)
        elif action_type == config.action.hash:
            res = self.__handle_hash(data)
        elif action_type == config.action.delete:
            res = self.__handle_del(conn, data)
        elif action_type == config.action.contains:
            res = self.__handle_contains(data)
        elif action_type == config.action.delitem:
            res = self.__handle_delitem(data)
        elif action_type == config.action.getitem:
            res = self.__handle_getitem(data)
        elif action_type == config.action.iter:
            res = self.__handle_iter(data)
        elif action_type == config.action.len:
            res = self.__handle_len(data)
        elif action_type == config.action.setitem:
            res = self.__handle_setitem(data)
        elif action_type == config.action.next:
            res = self.__handle_next(data)
        return res

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

    def __handle_serverproxy(self, data):
        return self

    def __handle_call(self, data):
        func, args, kwargs = data
        res = None
        try:
            res = func(*args, **kwargs)
            return res
        except Exception as e:
            logging.error("__handle_call error. function:{}".format(str(func)))
            traceback.print_exc()
            return e

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

    def __handle_del(self, conn, data):
        obj = data
        return conn.del_local_object(obj)

    def __handle_contains(self, data):
        obj, item = data
        return obj.__contains__(item)

    def __handle_delitem(self, data):
        obj, key = data
        return obj.__delitem__(key)

    def __handle_getitem(self, data):
        obj, key = data
        return obj.__getitem__(key)

    def __handle_iter(self, data):
        obj = data
        return obj.__iter__()

    def __handle_len(self, data):
        obj = data
        return obj.__len__()

    def __handle_setitem(self, data):
        obj, key, value = data
        return obj.__setitem__(key, value)

    def __handle_next(self, data):
        obj = data
        try:
            return obj.next()
        except StopIteration as e:
            return e

    def __get_module(self, name):
        return __import__(name, None, None, '*')

    def eval(self, text):
        return eval(text)

    def execute(self, text):
        exec text

