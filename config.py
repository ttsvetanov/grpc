#! python2

import os
import logging


DEFAULT_SERVER_PORT = 10009

LOG_FILE = os.path.join(os.getcwd(), 'grpc_log.txt')
LOG_LEVEL = logging.DEBUG
logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL)

SERVER_BUFFER_SIZE = 1024
CLIENT_BUFFER_SIZE = 1024
