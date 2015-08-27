#! python

import types


class Test:
    def __init__(self):
        self.a = 1
        self.b = 2
        self.c = 3

    def foo(self):
        print 'foo'

    def bar(self):
        print 'bar'

    def print_sth(self, string):
        print string

    def add(self):
        return self.a + self.b + self.c

    @classmethod
    def clsm(cls):
        print cls

    @staticmethod
    def sttcm():
        print "staticmethod"


if __name__ == "__main__":
    print type(int.__add__)      # wrapper_descriptor
    print type((1).__add__)      # method-wrapper
    print type(iter([]))         # listiterator
    print type(iter(()))         # tupleiterator
    print type(iter(set()))      # setiterator
