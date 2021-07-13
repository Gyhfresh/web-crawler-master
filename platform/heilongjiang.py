# -*- coding:utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import re
import json
import os
import time
import logging
import inspect
from logging.handlers import RotatingFileHandler


dir = os.path.dirname(os.path.dirname(__file__))
handlers = {
            logging.INFO: os.path.join(dir, 'log\\heilongjiang_info.log'),
            logging.ERROR: os.path.join(dir, 'log\\heilongjiang_error.log')
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

def clean(string):
    string1=string.replace("\n", "")
    string2=string1.replace("\t", "")
    string3 = string2.replace(" ", "")
    return string3

def kong(string):
    if string=='':
        return 'none'
    else:
        return string

def heilongjiang(url_path,save_path):
    logger.info('开始爬取黑龙江政务数据平台')
    url = url_path
    driver = webdriver.Chrome()
    driver.get(url)
    page=177  #总页数page
    login = input('按任意键继续')  #登录
    driver.find_element_by_xpath("//*[text()='数据集']").click()
    time.sleep(5)

    for i in range(1,page+1):
        print('page'+str(i))
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        data = soup.find_all('div', attrs={'class': "m-cata-list"})
        data = str(data)
        partern_id = re.compile(r'class="item-title"> <a href="catalogDetail.htm\?cata_id=(.*?)" target="_blank">', re.S)
        id = re.findall(partern_id, data)
        childrenurl = []
        urlroot1 = 'http://data.harbin.gov.cn/odweb/catalog/catalogDetail.htm?cata_id='
        for num in range(len(id)):
            childrenurl.append(urlroot1+id[num])
        for index,childurl in enumerate(childrenurl):
            temp = dict()
            driver.execute_script("window.open('{}')".format(childurl))  #打开子页面
            driver.switch_to.window(driver.window_handles[-1])  #切换到子页面
            time.sleep(2)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            data = soup.find_all('div', attrs={'class': "info-body"})
            data = str(data)
            partern_all = re.compile(r'<div class="info-body">(.*?)</div>', re.S)
            all = re.findall(partern_all, data)
            temp['name']=all[0]
            temp['topic'] = all[2]
            temp['info']=dict()
            temp['info']['desc'] = all[10]
            temp['info']['label'] = kong(all[9])
            temp['info']['time_gx'] = clean(all[3])
            temp['info']['time'] = clean(all[8])
            print(temp)
            logger.info(temp)
            if i>=1:
                try:
                    driver.find_element_by_xpath("//*[text()='文件下载']").click()  # 点击下载
                    time.sleep(5)
                    try:
                        driver.find_element_by_xpath("//*[text()='下载']").click()  # 点击下载
                        time.sleep(5)
                    except:
                        logger.error('无XLSX')

                    try:
                        driver.find_element_by_xpath("//li[text()='XML']").click()  # 点击下载
                        time.sleep(5)
                        try:
                            driver.find_element_by_link_text('下载').click()
                            time.sleep(2)
                        except:
                            logger.error('无XML')
                    except:
                        logger.error("服务器异常")

                    try:
                        driver.find_element_by_xpath("//li[text()='JSON']").click()  # 点击下载
                        time.sleep(5)
                        try:
                            driver.find_element_by_link_text('下载').click()
                            time.sleep(2)
                        except:
                            logger.error('无JSON')
                    except:
                        logger.error("服务器异常")

                    try:
                        driver.find_element_by_xpath("//li[text()='CSV']").click()  # 点击下载
                        time.sleep(5)
                        try:
                            driver.find_element_by_link_text('下载').click()
                            time.sleep(2)
                        except:
                            logger.error('无CSV')
                    except:
                        logger.error("服务器异常")

                    try:
                        driver.find_element_by_xpath("//li[text()='JSON']").click()  # 点击下载
                        time.sleep(5)
                        try:
                            driver.find_element_by_link_text('下载').click()
                            time.sleep(2)
                        except:
                            logger.error('无JSON')
                    except:
                        logger.error("服务器异常")
                except:
                    logger.error("服务器异常")

            driver.close() #关闭页面
            driver.switch_to.window(driver.window_handles[0]) #返回主页面
            time.sleep(2)
            if i >= 1:
                json_str = json.dumps(temp, ensure_ascii=False)
                with open(save_path, 'a', encoding='utf-8') as f:
                    f.write(json_str)
                    f.write('\n')

        #可能出现找不到元素
        try:
            driver.find_element_by_xpath("//*[text()='下一页']").click()
            time.sleep(5)
        except:
            driver.find_element_by_xpath("//*[text()='下一页']").click()
            time.sleep(5)

if __name__=='__main__':
    createHandlers()
    logger = TNLog()
    url_path='http://data.harbin.gov.cn/odweb/catalog/index.htm'
    save_path='../info/heilongjiang.json'
    heilongjiang(url_path,save_path)


