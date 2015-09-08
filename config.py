#! python2
#-*- coding: utf-8 -*-

import os
import logging


DEFAULT_SERVER_PORT = 10009
DEFAULT_SERVER_ADDRESS = ('localhost', DEFAULT_SERVER_PORT)

LOG_FILE = os.path.join(os.getcwd(), 'grpc_log.txt')
LOG_LEVEL = logging.DEBUG
logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL)

SERVER_BUFFER_SIZE = 10000
CLIENT_BUFFER_SIZE = 10000
