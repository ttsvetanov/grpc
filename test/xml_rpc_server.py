#! python

import SimpleXMLRPCServer


class Modifier:
    def test(self):
        print "test"

    def add(self, a, b, c):
        return a + b + c


if __name__ == '__main__':
    server = SimpleXMLRPCServer.SimpleXMLRPCServer(('localhost', 8888), allow_none=True)
    server.register_instance(Modifier())
    server.serve_forever()
