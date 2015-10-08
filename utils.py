# !python2
# -*- coding: utf-8 -*-

import threading
import weakref
import types


class CountDict(object):
    def __init__(self):
        self.__lock = threading.Lock()
        self.__dict = {}

    def __repr__(self):
        return repr(self.__dict)

    def __str___(self):
        return self.__repr__()

    def __setitem__(self, key, value):
        if key != id(value):
            raise ValueError('key must be id(value)')
        self.__lock.acquire()
        try:
            if key in self.__dict:
                self.__dict[key][1] += 1
            elif (isinstance(value, types.FunctionType)
                    or isinstance(value, types.MethodType)
                    or isinstance(value, types.UnboundMethodType)):
                ref_value = value
                self.__dict[key] = [False, 1, value]   # [isweak, count, value]
                print 'Ref strong type: ', type(value)
            else:
                try:
                    ref_value = weakref.ref(value)
                    self.__dict[key] = [True, 1, ref_value]
                except TypeError:
                    print 'Ref strong type: ', type(value)
                    self.__dict[key] = [False, 1, value]
        finally:
            self.__lock.release()

    def __getitem__(self, key):
        if self.__dict[key][0]:
            return self.__dict[key][2]()
        else:
            return self.__dict[key][2]

    def __delitem__(self, key):
        self.__lock.acquire()
        try:
            if key in self.__dict:
                self.__dict[key][1] -= 1
                if self.__dict[key][1] == 0:
                    del self.__dict[key]
            else:
                raise KeyError(key)
        finally:
            self.__lock.release()

    def clear(self):
        self.__lock.acquire()
        try:
            self.__dict.clear()
        finally:
            self.__lock.release()

    def add(self, obj):
        self[id(obj)] = obj
