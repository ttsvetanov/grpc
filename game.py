# !python2
# -*- coding: utf-8 -*-

from grpc_server import GrpcServer


def gameRun():
    server = GrpcServer()
    server.start()
    while True:
        server.handle_request()

if __name__ == '__main__':
    gameRun()
