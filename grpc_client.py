#! python2
#-*- coding: utf-8 -*-

import logging
import select
import pickle
import threading

import config
import connection
import service


class GrpcClient(object):
    def __init__(self):
        self.__server_proxy = None
        self.__conn = connection.Connection(config.CLIENT_BUFFER_SIZE)
        self.__conn_lock = threading.Lock()
        self.__service = service.Service()
        self.__connected = False

    @property
    def proxy(self):
        return self.__server_proxy

    def __del__(self):
        self.shutdown()

    def connect(self, server_address=config.DEFAULT_SERVER_ADDRESS):
        if not self.__connected:
            self.__connected = self.__conn.connect(server_address)
            if self.__connected:
                self.__server_proxy = self.__conn.sync_request(service.ACTION_GETROOT)
                t = threading.Thread(target=self.__handle_request_forever)
                t.start()

    def __handle_request_forever(self):
        while self.__connected:
            self.__service.handle_request(self.__conn)

    def shutdown(self):
        if self.__connected:
            self.__conn.send_shutdown()
            self.__conn.shutdown()
            self.__server_proxy = None
            self.__connected = False

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
