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
            return self.__cp.get(self.__sec_name, name)
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
print 'config created'

_LOG_FILE = os.path.join(os.getcwd(), config.server.log_file)
_LOG_LEVEL = logging.DEBUG
logging.basicConfig(filename=_LOG_FILE, level=_LOG_LEVEL)
