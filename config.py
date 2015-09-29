#! python2
#-*- coding: utf-8 -*-

import os
import sys
import logging

_msg = {'request':1, 'reply':2, 'exception':3, 'shutdown':4}
_action = {'getattr':1, 'setattr':2, 'delattr':3, 'str':4, 'repr':5, 'call':6,
'serverproxy':7, 'dir':8, 'cmp':9, 'hash':10, 'delete':11, 'contains':12,
'delitem':13, 'getitem':14, 'iter':15, 'len':16, 'setitem':17, 'next':18}
_label = {'value':1, 'tuple':2, 'local_ref':3, 'remote_ref':4, 'notimplemented':5,
'ellipsis':6, 'list':7, 'dict':8}
_server = {'addr':'localhost', 'port':10009, 'buf_size':1024,
'log_file':'grpc_server_log.txt'}
_client = {'buf_size':1024, 'log_file':'grpc_client_log.txt'}
_sections = {'msg':_msg, 'action':_action, 'label':_label, 'server':_server,
'client':_client}

class Section(object):
    def __init__(self, name):
        for option in _sections[name]:
            setattr(self, option, _sections[name][option])

class Config(object):
    def __init__(self):
        for name in _sections:
            setattr(self, name, Section(name))

config = Config()
config.msg_str = ('msg_str', 'Request', 'Reply', 'Exception', 'Shutdown')
config.action_str = ('action_str', 'getattr', 'setattr', 'delattr', 'str',
            'repr', 'call', 'serverproxy', 'dir', 'cmp', 'hash', 'del', 'contains',
            'delitem', 'getitem', 'iter', 'len', 'setitem', 'next')

_LOG_FILE = os.path.join(os.getcwd(), config.server.log_file)
_LOG_LEVEL = logging.DEBUG
logging.basicConfig(filename=_LOG_FILE, level=_LOG_LEVEL)
