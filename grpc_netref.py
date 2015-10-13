# !python2
# -*- coding: utf-8 -*-

from grpc_config import config
import sys

_local_netRef_attrs = ('____conn__', '____oid__')

class NetRef(object):

    def __init__(self, conn, oid):
        self.____conn__ = conn
        self.____oid__ = oid

    def __del__(self):
        self.____conn__.sync_request(config.action.delete, self)

    def __getattribute__(self, name):
        if name in _local_netRef_attrs:
            return object.__getattribute__(self, name)
        else:
            raise AttributeError()  # call __getattr__

    def __getattr__(self, name):
        if name == '__members__':
            return dir(self)
        return self.____conn__.sync_request(
            config.action.getattr, (self, name))

    def __setattr__(self, name, value):
        if name in _local_netRef_attrs:
            object.__setattr__(self, name, value)
        else:
            self.____conn__.sync_request(
                config.action.setattr, (self, name, value))

    def __delattr__(self, name):
        self.____conn__.sync_request(
            config.action.delattr, (self, name))

    def __str__(self):
        return self.____conn__.sync_request(config.action.str, self)

    def __repr__(self):
        return self.____conn__.sync_request(config.action.repr, self)

    def __call__(self, *args, **kwargs):
        need_reply = kwargs.pop("grpc_need_reply", True)
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


'''
def class_factory(clsname, modname):
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
    '''
