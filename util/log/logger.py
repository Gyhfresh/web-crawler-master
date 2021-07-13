# -*- coding: utf-8 -*-
# @FileName: logger.py
import configparser
import logging
import logging.handlers
from logging.config import fileConfig

from constant.env_constant import EnvConstant


class Logger:
    """
    log管理类，对logging进行封装，实现：
    info与error类型的log可以按照不同格式输出
    log输出到不同文件，且文件可定时切换到新文件
    log配置来自于外侧配置文件
    除error级别的数据输出到error文件中外，其它级别的log都输出到info文件
    """
    __logger_info = None
    __logger_error = None
    __is_logger_init = False

    @classmethod
    def __init_logger(cls):
        if cls.__is_logger_init:
            return

        parser = configparser.ConfigParser()
        parser.read(EnvConstant.LOG_CFG_FILE_NAME)
        parser.set('handler_errorHandler', 'args', "('%s/log/error.log','D', 1, 0, 'utf-8')"
                   % EnvConstant.PROJECT_PATH.replace("\\", "/"))
        parser.set('handler_infoHandler', 'args', "('%s/log/info.log','D', 1, 0, 'utf-8')"
                   % EnvConstant.PROJECT_PATH.replace("\\", "/"))
        parser.write(open(EnvConstant.LOG_CFG_FILE_NAME, 'w'))

        fileConfig(EnvConstant.LOG_CFG_FILE_NAME)
        cls.__logger_info = logging.getLogger(EnvConstant.LOG_INFO_LOGGER_NAME)
        cls.__logger_error = logging.getLogger(EnvConstant.LOG_ERROR_LOGGER_NAME)
        cls.__is_logger_init = True

    @classmethod
    def get_logger_error(cls):
        cls.__init_logger()
        return cls.__logger_error

    @classmethod
    def get_logger_info(cls):
        cls.__init_logger()
        return cls.__logger_info


logger_info = Logger.get_logger_info()
logger_error = Logger.get_logger_error()
