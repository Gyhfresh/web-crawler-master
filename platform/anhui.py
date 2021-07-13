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
            logging.INFO: os.path.join(dir, 'log\\anhui_info.log'),
            logging.ERROR: os.path.join(dir, 'log\\anhui_error.log')
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

def anhui(url_path,save_path):
    logger.info('开始爬取安徽政务数据平台')
    url = url_path
    driver = webdriver.Chrome()
    driver.get(url)
    page=4
    login = input('按任意键继续')  #登录、切换数据目录（和dataArea对应），分资源页爬取

    jsontemp=[]
    for i in range(1,page+1):
        logger.info('page'+str(i))
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        data = soup.find_all('div', attrs={'class': "dataresources"})
        data = str(data)
        partern_name = re.compile(r'target="_blank" title="(.*?)\n', re.S)
        name = re.findall(partern_name, data)
        partern_topic = re.compile(r'<span class="n3">数据领域： (.*?) </span>', re.S)
        topic = re.findall(partern_topic, data)
        partern_desc = re.compile(r'<span class="zy" title="(.*?)">资源摘要', re.S)
        desc = re.findall(partern_desc, data)
        partern_time = re.compile(r'<span class="n1">更新时间：(.*?)</span>', re.S)
        time_gx = re.findall(partern_time, data)
        print(name)
        logger.info(name)
        for index in range(len(name)):
            temp = dict()
            temp['name']=name[index]
            temp['topic'] = topic[index]
            temp['info']=dict()
            temp['info']['desc'] = desc[index]
            temp['info']['time'] = time_gx[index]
            logger.info(temp)
            if name[index] not in jsontemp:
                jsontemp.append(name[index])
                json_str = json.dumps(temp, ensure_ascii=False)
                with open(save_path, 'a', encoding='utf-8') as f:
                    f.write(json_str)
                    f.write('\n')
        partern_id = re.compile(r'<a class="title" href="/site/tpl/90\?resourceId=(.*?)&amp', re.S)
        id = re.findall(partern_id, data)
        childrenurl = []
        urlroot1 = 'http://www.mas.gov.cn/site/tpl/90?resourceId='
        urlroot2 = '&p_isPage=1&p_pageSize=8&p_pageIndex=1&p_dataArea=2&p_providerOrgan=&p_dateFormat=yyyy-MM-dd&p_length=34&p_orderBy='
        for num in range(len(id)):
            childrenurl.append(urlroot1 + id[num] + urlroot2)
        for index, childurl in enumerate(childrenurl):  ##一个数据的页面直接手点了
            driver.execute_script("window.open('{}')".format(childurl))  # 打开子页面
            driver.switch_to.window(driver.window_handles[-1])  # 切换到子页面
            time.sleep(2)
            if i >= 1:
                try:
                    driver.find_element_by_xpath("//*[text()='下载']").click()  # 点击下载
                    time.sleep(5)
                    try:
                        download = '.csv'
                        driver.find_element_by_partial_link_text(download).click()  # 点击下载
                        time.sleep(5)
                    except:
                        logger.error('无csv')
                    try:
                        download = '.xls'
                        driver.find_element_by_partial_link_text(download).click()  # 点击下载
                        time.sleep(5)
                    except:
                        logger.error('无xls')
                    try:
                        download = '.json'
                        driver.find_element_by_partial_link_text(download).click()  # 点击下载
                        time.sleep(5)
                    except:
                        logger.error('无json')
                except:
                    logger.error('无文件')

            driver.close()  # 关闭页面
            driver.switch_to.window(driver.window_handles[0])  # 返回主页面
            time.sleep(2)
        try:
            driver.find_element_by_xpath("//*[text()='下一页']").click()
            time.sleep(10)
        except:
            driver.find_element_by_xpath("//*[text()='下一页']").click()
            time.sleep(10)

if __name__=='__main__':
    createHandlers()
    logger = TNLog()
    url_path='http://www.mas.gov.cn/site/tpl/72'
    save_path='../info/anhui.json'
    anhui(url_path,save_path)



