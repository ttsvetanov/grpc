#! python2
#-*- coding: utf-8 -*-

import logging
import socket
import threading
import traceback
import select

import config
import connection
import service


class GrpcServer(object):
    def __init__(self, server_port = config.DEFAULT_SERVER_PORT):
        self.__server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__server_sock.bind(('localhost', server_port))
        self.__server_sock.listen(5)
        self.__conns = []
        self.__conns_lock = threading.Lock() # thread(serve_forever) and thread(handle_request)
        self.__serve = False
        self.__service = service.Service()

    def __del__(self):
        self.shutdown()

    def serve_forever(self):
        if self.__serve == False:
            self.__serve = True
            while self.__serve:
                ready = select.select([self.__server_sock], [], [], 0.5)
                for s in ready[0]:
                    if s is self.__server_sock:
                        conn = connection.Connection(config.SERVER_BUFFER_SIZE)
                        client_addr = conn.accept(self.__server_sock)
                        print 'Hello, ', client_addr
                        self.__conns_lock.acquire()
                        try:
                            self.__conns.append(conn)
                        finally:
                            self.__conns_lock.release()

    def shutdown(self):
        if self.__serve == True:
            self.__serve = False
            self.__conns_lock.acquire()
            try:
                for conn in self.__conns:
                    conn.send_shutdown()
                    conn.shutdown()
                self.__conns = []
            finally:
                self.__conns_lock.release()

    def handle_request(self):
        self.__conns_lock.acquire()
        try:
            for conn in self.__conns:
                res = self.__service.handle_request(conn)
                if not conn.connected:
                    print 'Bye, ', conn
                    self.__conns.remove(conn)
        finally:
            self.__conns_lock.release()


if __name__ == '__main__':
    import sys 
    server = GrpcServer()
    t = threading.Thread(target=server.serve_forever)
    t.start()
    while True:
        server.handle_request()
