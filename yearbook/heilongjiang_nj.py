 # -*- coding:utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import json
import os
import time
import logging
import inspect
from logging.handlers import RotatingFileHandler


dir = os.path.dirname(os.path.dirname(__file__))
handlers = {
            logging.INFO: os.path.join(dir, 'log\heilongjiang_nj_info.log'),
            logging.ERROR: os.path.join(dir, 'log\heilongjiang_nj_error.log')
            }
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/70.0.3538.110 Safari/537.36'}

class TNLog(object):

    def printfNow(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def __init__(self, level=logging.NOTSET):
        self.__loggers = {}
        logLevels = handlers.keys()
        for level in logLevels:
            logger = logging.getLogger(str(level))
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

def createHandlers():
    logLevels = handlers.keys()

    for level in logLevels:
        path = os.path.abspath(handlers[level])
        handlers[level] = RotatingFileHandler(path, maxBytes=10000, backupCount=2, encoding='utf-8')

def heilongjiang_nj(url_path,save_path):
    logger.info('开始爬取黑龙江年鉴')
    url = url_path
    driver = webdriver.Chrome()
    driver.get(url)
    login = input('按任意键继续')  #点击excel模式

    driver.switch_to.frame(1)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find_all('ul')
    data = str(data)
    partern_topic = re.compile(r'<li id="foldheader">(.*?)</li>', re.S)
    topic = re.findall(partern_topic, data)
    partern_name = re.compile(r'<a href="html/.*?xls">([0-9].*?)</a></li>', re.S)
    name = re.findall(partern_name, data)
    temp=dict()
    for n in name:
        partern_id = re.compile(r'([0-9]+)-[0-9]+ ', re.S)
        id = re.findall(partern_id, n)
        try:
            if id[0] in temp:
                if n not in temp[id[0]]:
                    temp[id[0]].append(n)
            else:
                temp[id[0]]=[n]
        except:
            logger.error('不爬取附录')

    for index,t in enumerate(topic[1:-1]):
        print(t)
        logger.info(t)
        click_name=t
        click_button = driver.find_element_by_xpath("//*[text()='{}']".format(click_name))
        click_button.click()
        time.sleep(2)
        for file in temp[str(index+1)]:
            click_name = file
            try:
                click_button = driver.find_element_by_xpath("//*[text()='{}']".format(click_name))
                click_button.click()
                time.sleep(2)
            except:
                err=str(t)+'无文件'
                logger.error(err)
            table=dict()
            table['name'] = file
            table['topic'] = t
            table['info'] = dict()
            print(table)
            logger.info(table)
            json_str = json.dumps(table, ensure_ascii=False)

            with open(save_path, 'a', encoding='utf-8') as f:
                f.write(json_str)
                f.write('\n')

if __name__=='__main__':
    createHandlers()
    logger = TNLog()
    url_path='http://tjj.hlj.gov.cn/app/tongjnj/2020/zk/indexch.htm'
    save_path='../info/heilongjiang_nj.json'
    heilongjiang_nj(url_path,save_path)
