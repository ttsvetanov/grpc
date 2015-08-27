#! python

import grpc


class GameEditor(grpc.Server):
    def __init__(self, game):
        super(GameEditor, self).__init__()
        self.game_inst = game

    def test(self):
        print 'test'

    def set_speed(self, new_speed):
        try:
            self.game_inst.state.weight.speed = new_speed
        except AttributeError:
            print "AttributeError"


if __name__ == '__main__':
    ge = GameEditor()
    ge.start()
