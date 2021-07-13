# -*- coding: utf-8 -*-
import os
import time
from logging.handlers import RotatingFileHandler
import logging

import inspect

dir = os.path.dirname(__file__) + '/../log'

handlers = None


def createHandlers():
    logLevels = handlers.keys()

    for level in logLevels:
        path = os.path.abspath(handlers[level])
        handlers[level] = RotatingFileHandler(path, maxBytes=10000, backupCount=2, encoding='utf-8')


# 加载模块时创建全局变量

# createHandlers()


class TNLog(object):

    def printfNow(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def __init__(self, name='', level=logging.NOTSET):
        self.__loggers = {}
        global handlers
        handlers = {
            logging.INFO: os.path.join(dir, name + '_info.log'),

            logging.ERROR: os.path.join(dir, name + '_error.log'),
        }

        createHandlers()

        logLevels = handlers.keys()

        for level in logLevels:
            logger = logging.getLogger(str(level))

            # 如果不指定level，获得的handler似乎是同一个handler?

            logger.addHandler(handlers[level])

            logger.setLevel(level)

            self.__loggers.update({level: logger})

    def getLogMessage(self, level, message):
        frame, filename, lineNo, functionName, code, unknowField = inspect.stack()[2]

        '''日志格式：[时间] [类型] [记录代码] 信息'''

        return "[%s] [%s] [%s - %s - %s] %s" % (self.printfNow(), level, filename, lineNo, functionName, message)

    def info(self, message):
        message = self.getLogMessage("info", message)

        self.__loggers[logging.INFO].info(message)

    def error(self, message):
        message = self.getLogMessage("error", message)

        self.__loggers[logging.ERROR].error(message)


if __name__ == "__main__":
    logger = TNLog('广东')

    logger.info("info")
    logger.error("error")
