# !python2
# -*- coding: utf-8 -*-

from grpc_server import GrpcServer


class Player(object):
    pass

class Game(object):
    def __init__(self):
        self.num = 2
        self.dct = {}
        self.lst = []
        self.player = Player()

    def foo(self):
        print 'foo'
        return 'foo'

    def pnt(self, arg):
        print arg

    def run(self):
        server = GrpcServer()
        server.game = self
        server.start()
        try:
            while True:
                server.handle_request()
        except KeyboardInterrupt:
            server.shutdown()


if __name__ == '__main__':
    game = Game()
    game.run()
