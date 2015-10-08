# !python2
# -*- coding: utf-8 -*-

from config import config
import sys


local_netref_attrs = frozenset([
    '____conn__', '____oid__', '__cmp__', '__del__', '__delattr__',
    '__dir__', '__getattr__', '__getattribute__', '__hash__',
    '__init__', '__metaclass__', '__module__', '__new__', '__reduce__',
    '__reduce_ex__', '__repr__', '__setattr__', '__slots__', '__str__',
    '__weakref__', '__dict__',  '__members__', '__methods__',
    '____cache_attr__', '____need_reply__', '____attr_cache__',
    'grpc_clear_attr_cache'
    ])


class NetRef(object):
    # __slots__ = ["____conn__", "____oid__"]

    def __init__(self, conn, oid, cache_attr=False, need_reply=True):
        self.____conn__ = conn
        self.____oid__ = oid
        self.____cache_attr__ = cache_attr
        self.____need_reply__ = need_reply
        self.____attr_cache__ = {}

    def __del__(self):
        self.____conn__.sync_request(config.action.delete, self)

    '''
    def __getattribute__(self, name):
        if name in local_netref_attrs:
            if name == '__class__' or name == '__doc__':
                return self.__getattr__(name)
            elif name == '__members__':
                return self.__dir__()
            return object.__getattribute__(self, name)
        else:
            return self.__getattr__(name)
    '''

    def __getattr__(self, name):
        if name == '__members__':
            return self.__dir__()
        value = self.____conn__.sync_request(
            config.action.getattr, (self, name))
        if self.____cache_attr__:
            self.____attr_cache__[name] = value
            if isinstance(value, NetRef):
                value.____cache_attr__ = self.____cache_attr__
                value.____need_reply__ = self.____need_reply__
        return value

    def __setattr__(self, name, value):
        if name in local_netref_attrs:
            object.__setattr__(self, name, value)
        else:
            if self.____cache_attr__:
                self.____attr_cache__[name] = value
                if isinstance(value, NetRef):
                    value.____cache_attr__ = self.____cache_attr__
                    value.____need_reply__ = self.____need_reply__
            self.____conn__.sync_request(
                config.action.setattr, (self, name, value))

    def __delattr__(self, name):
        if name in local_netref_attrs:
            object.__delattr__(name)
        else:
            try:
                del self.____attr_cache__[name]
            finally:
                self.____conn__.sync_request(
                    config.action.delattr, (self, name))

    def grpc_clear_attr_cache(self):
        self.____attr_cache__ = {}

    def __str__(self):
        return self.____conn__.sync_request(config.action.str, self)

    def __repr__(self):
        return self.____conn__.sync_request(config.action.repr, self)

    def __call__(self, *args, **kwargs):
        need_reply = kwargs.pop("grpc_need_reply", self.____need_reply__)
        return self.____conn__.sync_request(
            config.action.call, (self, args, kwargs), need_reply)

    def __dir__(self):
        rlist = self.____conn__.sync_request(config.action.dir, self)
        return eval(repr(rlist))

    def __cmp__(self, other):
        return self.____conn__.sync_request(config.action.cmp, (self, other))

    def __hash__(self):
        return self.____conn__.sync_request(config.action.hash, self)

    def __contains__(self, item):
        return self.____conn__.sync_request(
            config.action.contains, (self, item))

    def __delitem__(self, key):
        return self.____conn__.sync_request(config.action.delitem, (self, key))

    def __getitem__(self, key):
        return self.____conn__.sync_request(config.action.getitem, (self, key))

    def __iter__(self):
        return self.____conn__.sync_request(config.action.iter, self)

    def __len__(self):
        return self.____conn__.sync_request(config.action.len, self)

    def __setitem__(self, key, value):
        return self.____conn__.sync_request(
            config.action.setitem, (self, key, value))

    def next(self):
        res = self.____conn__.sync_request(config.action.next, self)
        if isinstance(res, StopIteration):
            raise res
        return res


def class_factory(clsname, modname):
    """Creates a netref class proxying the given class

    :param clsname: the class's name
    :param modname: the class's module name

    :returns: a netref class
    """
    clsname = str(clsname)
    modname = str(modname)
    ns = {"__slots__": ()}
    ns["__module__"] = modname
    if modname in sys.modules and hasattr(sys.modules[modname], clsname):
        ns["__class__"] = getattr(sys.modules[modname], clsname)
    else:
        # to be resolved by the instance
        ns["__class__"] = None
    return type(clsname, (NetRef,), ns)
