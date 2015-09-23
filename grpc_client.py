#! python2
#-*- coding: utf-8 -*-

import logging
import select
import pickle

from config import config
import connection


class GrpcClient(object):
    def __init__(self):
        self.__server_proxy = None
        self.__conn = connection.Connection(config.client.buf_size)

    @property
    def server_proxy(self):
        if self.__server_proxy is None:
            self.__server_proxy = self.__conn.sync_request(config.action.serverproxy)
        return self.__server_proxy

    @property
    def connected(self):
        return self.__conn.connected

    def __del__(self):
        self.shutdown()

    def connect(self, server_address=(config.server.addr, config.server.port)):
        res = self.__conn.connect(server_address)
        self.__server_proxy = None

    def shutdown(self):
        self.__conn.send_shutdown()
        self.__conn.shutdown()
        self.__server_proxy = None

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
