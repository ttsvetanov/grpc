#! python2

from grpc_server import Server
from grpc_server import Request

class Caller:
    def __init__(self, server=None):
        if server:
            self.__server = server
        else:
            self.__server = Server()

