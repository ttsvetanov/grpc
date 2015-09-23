#! python2
#-*- coding: utf-8 -*-

import os
import logging
import ConfigParser

class Section(object):
    def __init__(self, cp, name):
        self.__cp = cp
        self.__sec_name = name

    def __getattribute__(self, name):
        if name == '_Section__cp' or name == '_Section__sec_name':
            return object.__getattribute__(self, name)
        if name in self.__cp.options(self.__sec_name):
            value = self.__cp.get(self.__sec_name, name)
            try:
                return int(value)
            except ValueError:
                return value
        else:
            return object.__getattribute__(self, name)

class Config(object):
    def __init__(self):
        self.__cp = ConfigParser.ConfigParser()
        self.__cp.read("config.ini")

    def __getattribute__(self, name):
        if name == '_Config__cp':
            return object.__getattribute__(self, name)
        if name in self.__cp.sections():
            return Section(self.__cp, name)
        else:
            return object.__getattribute__(self, name)

config = Config()
config.msg_str = ('msg_str', 'Request', 'Reply', 'Exception', 'Shutdown')
config.action_str = ('action_str', 'getattr', 'setattr', 'delattr', 'str',
            'repr', 'call', 'serverproxy', 'dir', 'cmp', 'hash', 'del', 'contains',
            'delitem', 'getitem', 'iter', 'len', 'setitem', 'next')

_LOG_FILE = os.path.join(os.getcwd(), config.server.log_file)
_LOG_LEVEL = logging.DEBUG
logging.basicConfig(filename=_LOG_FILE, level=_LOG_LEVEL)
