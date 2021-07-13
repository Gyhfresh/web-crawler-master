# -*- coding: utf-8 -*-
# @Time    : 2021/6/9 10:45
# @Author  : leizehua
# @FileName: env_constant.py
import os


class EnvConstant:
    """
    常量类，保存使用的常量
    """
    # 项目路径
    PROJECT_PATH = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]

    # 运行环境整体配置文件
    # 使用os.path获取绝对路径
    CONFIG_PATH = PROJECT_PATH + "/config/config.ini"

    # log配置文件，使用os.path获取配置
    LOG_CFG_FILE_NAME = PROJECT_PATH + "/config/log.ini"

    LOG_INFO_LOGGER_NAME = 'infoLogger'
    LOG_ERROR_LOGGER_NAME = 'errorLogger'
