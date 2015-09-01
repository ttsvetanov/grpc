#! python2

import logging
import socket
import config
import select
import pickle
from netref import NetRef

class GrpcClient(object):
    def __init__(self):
        self.server_proxy = None
        self.sock = None
        self.connected = False

    def try_to_connect(self, server_address=('localhost', config.DEFAULT_SERVER_PORT),
            try_times = -1, delay = 1):
        while try_times != 0:
            try_times -= 1
            try:
                print 'trying to connect server...'
                self.sock = socket.create_connection(server_address, timeout=delay)
                if self.sock:
                    self.connected = True
                    print 'connected!'
                    self.server_proxy = self.get_server_proxy();
                    break
            except socket.timeout:
                print 'timeout'
        return self.connected

    def get_server_proxy(self):
        return self.getattr_from_server('0', 'server')

    def shutdown(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.connected = False

    def getattr_from_server(self, oid, name):
        if not self.connected:
            return None
        self.sock.sendall(pickle.dumps((oid, name)))
        ready = select.select([self.sock], [], [], 5)
        if ready[0]:
            data = self.sock.recv(config.CLIENT_BUFFER_SIZE)
            attr_oid, attr_str = pickle.loads(data)
            return NetRef(self, attr_oid)
        else:
            return None

if __name__ == '__main__':
    client = GrpcClient()
    client.try_to_connect()
    client.sock.sendall('test')
    ready = select.select([client.sock], [], [], 5)
    if ready[0]:
        data = client.sock.recv(config.CLIENT_BUFFER_SIZE)
        print data
    client.shutdown()
