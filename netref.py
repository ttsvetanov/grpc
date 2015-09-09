#! python2
#-*- coding: utf-8 -*-

import connection
import types
import inspect
import sys


local_netref_attrs = frozenset([
    '____conn__', '____oid__', '__class__', '__cmp__', '__del__', '__delattr__',
    '__dir__', '__doc__', '__getattr__', '__getattribute__', '__hash__',
    '__init__', '__metaclass__', '__module__', '__new__', '__reduce__',
    '__reduce_ex__', '__repr__', '__setattr__', '__slots__', '__str__',
    '__weakref__', '__dict__',  '__members__', '__methods__',
    ])


class NetRef(object):
    #__slots__ = ["____conn__", "____oid__"]
    
    def __init__(self, conn, oid):
        self.____conn__ = conn
        self.____oid__ = oid

    def __del__(self):
        print 'del'
        self.____conn__.sync_request(connection.ACTION_DEL, self)

    def __getattribute__(self, name):
        if name in local_netref_attrs:
            if name == '__class__' or name == '__doc__':
                return self.__getattr__(name)
            elif name == '__members__':
                return self.__dir__()
            return object.__getattribute__(self, name)
        else:
            return self.__getattr__(name)

    def __getattr__(self, name):
        return self.____conn__.sync_request(connection.ACTION_GETATTR, (self, name))

    def __setattr__(self, name, value):
        if name in local_netref_attrs:
            object.__setattr__(self, name, value)
        else:
            self.____conn__.sync_request(connection.ACTION_SETATTR, (self, name, value))

    def __delattr__(self, name):
        if name in local_netref_attrs:
            object.__delattr__(name)
        else:
            self.____conn__.sync_request(connection.ACTION_DELATTR, (self, name))
        
    def __str__(self):
        return self.____conn__.sync_request(connection.ACTION_STR, self)

    def __repr__(self):
        return self.____conn__.sync_request(connection.ACTION_REPR, self)

    def __call__(self, *args, **kwargs):
        return self.____conn__.sync_request(connection.ACTION_CALL, (self, args, kwargs))

    def __dir__(self):
        return list(self.____conn__.sync_request(connection.ACTION_DIR, self))

    def __cmp__(self, other):
        return self.____conn__.sync_request(connection.ACTION_CMP, (self, other))

    def __hash__(self):
        return self.____conn__.sync_request(connection.ACTION_HASH, self)


def class_factory(clsname, modname):
    """Creates a netref class proxying the given class
    
    :param clsname: the class's name
    :param modname: the class's module name
    
    :returns: a netref class
    """
    clsname = str(clsname)
    modname = str(modname)
    ns = {"__slots__" : ()}
    ns["__module__"] = modname
    if modname in sys.modules and hasattr(sys.modules[modname], clsname):
        ns["__class__"] = getattr(sys.modules[modname], clsname)
    else:
        # to be resolved by the instance
        ns["__class__"] = None
    return type(clsname, (NetRef,), ns)
