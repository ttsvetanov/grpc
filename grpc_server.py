#! python2

import SimpleXMLRPCServer
import os
import logging
from Queue import *
from threading import Thread


DEFAULT_SERVER_PORT = 10009
logging.basicConfig(filename=os.path.join(os.getcwd(), 'grpc_log.txt'), level=logging.DEBUG)


class Server(object):
    def __init__(self, port=DEFAULT_SERVER_PORT):
        self.__server = SimpleXMLRPCServer.SimpleXMLRPCServer(("localhost", port), allow_none=True)
        self.__server.register_introspection_functions()
        self.__server.register_instance(self)
        self.request_records = Queue()

    def _dispatch(self, *args):
        request = Request(args)
        self.request_records.put(request)

    def start(self, isThreading = True):
        if isThreading:
            try:
                t = Thread(name='SimpleXMLRPCServer_Thread', target=self.__server.serve_forever)
                t.start()
            except Exception, e:
                logging.error("%s : %s", type(e), e)
                raise
        else:
            self.__server.serve_forever()

    def shutdown(self):
        self.__server.shutdown()

    def get_next_request(self):
        try:
            first_item = self.request_records.get(False)
        except Empty:
            first_item = None
        finally:
            return first_item

    def call_once(self):
        ''' return value: True for success, False for failed'''
        request = self.get_next_request()
        if request:
            try:
                func = getattr(self, request.name)
            except AttributeError, e:
                logging.error("call_once: getattr failed, %s : %s", type(e), e)
                return False
            try:
                func(*request.args)
            except:
                logging.error("call_once: call failed.")
                return False
            return True
        else:
            return False

    def call_all(self):
        while not self.request_records.empty():
            self.call_once()

class Request:
    def __init__(self, request_info):
        self.name = request_info[0]
        self.args = request_info[1]

if __name__ == '__main__':
    server = Server()
    server.start(False)
