#! python2

import logging
import config
import select
import pickle
from netref import NetRef
import connection


class GrpcClient(object):
    def __init__(self):
        self.__server_proxy = None
        self.conn = connection.Connection(config.CLIENT_BUFFER_SIZE)

    @property
    def server_proxy(self):
        if not self.__server_proxy:
            server_proxy_id = self.conn.sync_request(connection.ACTION_GETSERVERPROXY)
            if server_proxy_id:
                self.__server_proxy = NetRef(self.conn, server_proxy_id)
        return self.__server_proxy

    def __del__(self):
        self.shutdown()

    def connect(self, server_address=config.DEFAULT_SERVER_ADDRESS):
        res = self.conn.connect(server_address)

    def shutdown(self):
        self.conn.send_shutdown()
        self.conn.shutdown()

'''
if __name__ == '__main__':
    client = GrpcClient()
    client.try_to_connect()
    client.sock.sendall('test')
    ready = select.select([client.sock], [], [], 5)
    if ready[0]:
        data = client.sock.recv(config.CLIENT_BUFFER_SIZE)
        print data
    client.shutdown()
    '''
