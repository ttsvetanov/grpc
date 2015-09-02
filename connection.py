#! python2

import select
import socket
import config
import pickle


# MSG_TYPE
MSG_REQUEST = 1
MSG_REPLY = 2
MSG_EXCEPTION = 3
MSG_SHUTDOWN = 4

# Action_Type
ACTION_GETATTR = 1
ACTION_SETATTR = 2
ACTION_DELATTR = 3
ACTION_STR = 4
ACTION_REPR = 5
ACTION_CALL = 6
ACTION_GETSERVERPROXY = 7


class Connection(object):
    def __init__(self, buffer_size):
        self.__sock = None
        self.__buffer_size = buffer_size
        self.__seq_num = 1      # next request's sequence number
        self.connected = False

    def __del__(self):
        self.shutdown()

    def accept(self, server_sock):
        client_sock, address = server_sock.accept()
        self.__sock = client_sock
        self.connected = True
        return self.connected

    def connect(self, server_address):
        while True:
            try:
                print 'connecting'
                self.__sock = socket.create_connection(server_address, timeout=1)
                if self.__sock:
                    self.connected = True
                    break
            except socket.timeout:
                print 'timeout'
            except:
                raise
        return self.connected

    def shutdown(self, flag = socket.SHUT_RDWR):
        if self.connected:
            self.__sock.shutdown(flag)
            self.connected = False

    def send_request(self, action_type, data):
        res = self.send(MSG_REQUEST, self.__seq_num, action_type, data)
        if res > 0:
            self.__seq_num += 1
        return res

    def send_reply(self, seq_num, action_type, data):
        return self.send(MSG_REPLY, seq_num, action_type, data)

    def send_shutdown(self):
        return self.send(MSG_SHUTDOWN, 1, 0, None)

    def send_exception(self, data):
        pass

    def send(self, msg_type, seq_num, action_type, data):
        if not self.connected:
            return -1
        pickled_data = pickle.dumps((msg_type, seq_num, action_type, data))
        self.__sock.sendall(pickled_data)
        return seq_num
        
    def recv(self, timeout = -1.0):
        if not self.connected:
            return None
        if timeout < 0:
            ready = select.select([self.__sock], [], []);
        else:
            ready = select.select([self.__sock], [], [], timeout);
        if ready[0]:
            pickled_data = self.__sock.recv(self.__buffer_size)
            return pickle.loads(pickled_data)
        return None

    def sync_request(self, action_type, data=None):
        seq_num = self.send_request(action_type, data)
        if seq_num < 0:
            return None
        msg_type, recv_seq_num, action_type, recv_data = self.recv()
        if msg_type == MSG_REPLY and recv_seq_num == seq_num:
            return recv_data
        return None
