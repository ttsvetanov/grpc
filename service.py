#! python2
#-*- coding: utf-8 -*-

import logging
import connection
import config
import traceback
import netref

# Action_Type
ACTION_GETATTR = 1
ACTION_SETATTR = 2
ACTION_DELATTR = 3
ACTION_STR = 4
ACTION_REPR = 5
ACTION_CALL = 6
ACTION_GETROOT = 7
ACTION_DIR = 8
ACTION_CMP = 9
ACTION_HASH = 10
ACTION_DEL = 11
action_str = ('action type str', 'getattr', 'setattr', 'delattr', 
        'str', 'repr', 'call', 'getroot', 'dir', 'cmp', 'hash', 'del')


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


class Service(object):
    def __init__(self):
        self.modules = ModuleNamespace(self.__get_module)
        self.test = 2
        self.d = {}
        self.l = []
        pass

    def p(self, *args, **kwargs):
        print args
        print kwargs

    def foo(self):
        print 'foo'
        return 'foo'

    def handle_request(self, conn):
        res = conn.get_request()    # not block
        if res is None:
            return res
        msg_type, seq_num, action_type, data = res
        print (connection.msg_str[msg_type], seq_num,
                action_str[action_type], data)
        res = None
        if msg_type == connection.MSG_REQUEST:
            if action_type == ACTION_GETATTR:
                res = self.__handle_getattr(data)
            elif action_type == ACTION_SETATTR:
                res = self.__handle_setattr(data)
            elif action_type == ACTION_DELATTR:
                res = self.__handle_delattr(data)
            elif action_type == ACTION_STR:
                res = self.__handle_str(data)
            elif action_type == ACTION_REPR:
                res = self.__handle_repr(data)
            elif action_type == ACTION_GETROOT:
                res = self.__handle_get_root(data)
            elif action_type == ACTION_CALL:
                res = self.__handle_call(data)
            elif action_type == ACTION_DIR:
                res = self.__handle_dir(data)
            elif action_type == ACTION_CMP:
                res = self.__handle_cmp(data)
            elif action_type == ACTION_HASH:
                res = self.__handle_hash(data)
            elif action_type == ACTION_DEL:
                res = self.__handle_del(conn, data)
        conn.send_reply(seq_num, action_type, res)
        return msg_type

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

    def __handle_get_root(self, data):
        return self

    def __handle_call(self, data):
        func, args, kwargs = data
        res = None
        print func
        print args
        print kwargs
        print isinstance(func, netref.NetRef)
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

    def __handle_del(self, conn, data):
        obj = data
        return conn.del_local_object(obj)

    def __get_module(self, name):
        return __import__(name, None, None, '*')

    def eval(self, text):
        return eval(text)

    def execute(self, text):
        exec text
