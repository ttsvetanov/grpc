#! /usr/bin/python2

import rpyc


if __name__ == "__main__":
    c = rpyc.classic.connect(host = "localhost", port = 10009)
    c.execute("print 'hello'")
