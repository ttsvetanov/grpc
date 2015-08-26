#! /usr/bin/python2

import rpyc
from rpyc.utils.server import ThreadedServer


class SquishService(rpyc.SlaveService):
    def on_connect(self):
        super(SquishService, self).on_connect()
        print "connect!!"

    def test(self):
        print "test"

    def exposed_test(self):
        print "exposed_test"

    def set_speed(self, new_speed):
        try:
            SquishServer.game_inst.state.weight.speed = new_speed
            print SquishServer.game_inst.state.weight.speed
        except AttributeError:
            print "AttributeError"
            pass


class SquishServer(ThreadedServer):
    def __init__(self, game):
        SquishServer.game_inst = game
        super(SquishServer, self).__init__(SquishService, hostname = "localhost", port = 10009)


if __name__ == "__main__":
    s = SquishServer(None)
    s.start()
