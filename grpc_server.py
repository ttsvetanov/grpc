#! python2

import logging
import SocketServer
import config
import pickle


class GrpcServerHandler(SocketServer.StreamRequestHandler):
    def __init__(self, *args):
        self.local_objects = {}
        self.modules = None
        self.test = 2
        SocketServer.StreamRequestHandler.__init__(self, *args)

    def handle(self):
        while True:
            data = self.request.recv(config.SERVER_BUFFER_SIZE)
            print 'server:::'
            oid, name = pickle.loads(data)
            if name == 'server':
                attr = self
                attr_oid = id(attr)
            else:
                attr = getattr(self.local_objects[oid], name)
                attr_oid = id(attr)
            self.local_objects[attr_oid] = attr
            self.request.sendall(pickle.dumps((attr_oid, str(attr))))


class GrpcServer(SocketServer.ThreadingTCPServer, object):
    __server = None
    def __new__(cls, *args, **kwargs):
        if not cls.__server:
            cls.__server = super(GrpcServer, cls).__new__(cls, *args, **kwargs)
        return cls.__server
    
    def __init__(self, server_address=('', config.DEFAULT_SERVER_PORT),
            handler=GrpcServerHandler):
        SocketServer.ThreadingTCPServer.__init__(self, server_address, GrpcServerHandler)

if __name__ == '__main__':
    server = GrpcServer()
    server.serve_forever()
