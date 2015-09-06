#! python2

import connection


local_netref_attrs = frozenset([
    '____conn__', '____oid__', '__class__', '__cmp__', '__del__', '__delattr__',
    '__dir__', '__doc__', '__getattr__', '__getattribute__', '__hash__',
    '__init__', '__metaclass__', '__module__', '__new__', '__reduce__',
    '__reduce_ex__', '__repr__', '__setattr__', '__slots__', '__str__',
    '__weakref__', '__dict__',  '__members__', '__methods__',
    ])

class NetRef(object):
    __slots__ = ["____conn__", "____oid__"]
    
    def __init__(self, conn, oid):
        self.____conn__ = conn
        self.____oid__ = oid

    def __getattribute__(self, name):
        if name in local_netref_attrs:
            if name == '__class__' or name == '__doc__':
                return self.__getattr__(name)
            elif name == '__members__' or name == '__dir__':
                return self.__getattr__('__dir__')
            return object.__getattribute__(self, name)
        else:
            return self.__getattr__(name)

    def __getattr__(self, name):
        attr_oid = self.____conn__.sync_request(connection.ACTION_GETATTR,
                (self.____oid__, name))
        return NetRef(self.____conn__, attr_oid)
        
    def __str__(self):
        res = self.____conn__.sync_request(connection.ACTION_STR, self.____oid__)
        return res
