#! python2

import SimpleXMLRPCServer
import thread


class SquishServer:
    def __init__(self, game):
        self.game_inst = game
        server = SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", 8888), allow_none = True)
        server.register_instance(self)
        thread.start_new_thread(server.serve_forever, ())

    def test(self):
        print "test"

    def set_speed(self, new_speed):
        try:
            self.game_inst.state.weight.speed = new_speed
        except AttributeError:
            print "AttributeError"



if __name__ == "__main__":
    pass
