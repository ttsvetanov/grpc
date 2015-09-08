#! python2
#-*- coding: utf-8 -*-

import threading


class CountDict(object):
    def __init__(self):
        self.__lock = threading.Lock()
        self.__dict = {}

    def __repr__(self):
        return repf(self._dict)

    def __str___(self):
        return self.__repr__()

    def __setitem__(self, key, value):
        if key != id(value):
            raise ValueError, 'key must be id(value)'
        self.__lock.acquire()
        try:
            if self.__dict.has_key(key):
                self.__dict[key][1] += 1
            else:
                self.__dict[key] = [value, 1]
        finally:
            self.__lock.release()

    def __getitem__(self, key):
        self.__lock.acquire()
        try:
            return self.__dict[key][0]
        finally:
            self.__lock.release()

    def __delitem__(self, key):
        self.__lock.acquire()
        try:
            if self.__dict.has_key(key):
                self.__dict[key][1] -= 1
                if self.__dict[key][1] == 0:
                    del self.__dict[key]
            else:
                raise KeyError, key
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
