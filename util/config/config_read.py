# -*- coding: utf-8 -*-
# @Time    : 2020/4/27 17:21
# @Author  : leizehua
# @FileName: config_read.py

from configparser import ConfigParser


class ReadConfig:
    def __init__(self, path):
        self.cfg = ConfigParser()
        self.cfg.read(path)

    def get_section(self):
        sections = self.cfg.sections()
        return sections

    def get_options(self, section):
        options = self.cfg.options(section=section)
        return options

    def get_all_key_value(self, section):
        all_key_value = self.cfg.items(section=section)
        return all_key_value

    def get_key_value(self, section, option):
        option_value = self.cfg.get(section=section, option=option)
        return option_value

    def get_all_values(self, section):
        values_list = []
        key_value_tuples = self.get_all_key_value(section)
        for item in key_value_tuples:
            values_list.append(item[1])
        return values_list
