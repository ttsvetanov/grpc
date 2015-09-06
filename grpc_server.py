#! python2

import logging
import socket
import config
import connection
import threading


class GrpcServer(object):
    def __init__(self, server_port = config.DEFAULT_SERVER_PORT):
        self.modules = None
        self.test = 2
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind(('localhost', server_port))
        self.server_sock.listen(5)

    def serve_forever(self):
        while True:
            conn = connection.Connection(config.SERVER_BUFFER_SIZE)
            if conn.accept(self.server_sock):
                t = threading.Thread(target=self.handle_request, args=(conn,))
                t.start()

    def handle_request(self, conn):
        while True:
            msg_type, seq_num, action_type, data = conn.recv()
            res = None
            if msg_type == connection.MSG_REQUEST:
                if action_type == connection.ACTION_GETATTR:
                    res = self.handle_getattr(conn, data)
                elif action_type == connection.ACTION_STR:
                    res = self.handle_str(conn, data)
                elif action_type == connection.ACTION_GETSERVERPROXY:
                    res = self.handle_get_server_proxy(data)
            elif msg_type == connection.MSG_SHUTDOWN:
                conn.shutdown()
                del conn
                break
            if res:
                conn.send_reply(seq_num, action_type, res)

    def handle_getattr(self, conn, data):
        oid, attr_name = data
        attr = getattr(conn.local_objects[oid], attr_name)
        return attr

    def handle_str(self, conn, data):
        oid = data
        return str(conn.local_objects[oid])

    def handle_get_server_proxy(self, data):
        return self

if __name__ == '__main__':
    server = GrpcServer()
    server.serve_forever()
