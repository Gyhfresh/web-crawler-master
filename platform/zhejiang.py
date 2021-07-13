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
from selenium.webdriver.common.action_chains import ActionChains


dir = os.path.dirname(os.path.dirname(__file__))
handlers = {
            logging.INFO: os.path.join(dir, 'log\\zhejiang_info.log'),
            logging.ERROR: os.path.join(dir, 'log\\zhejiang_error.log')
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
def zhejiang(url_path,save_path):
    logger.info('开始爬取浙江政务数据平台')
    url =  url_path
    driver = webdriver.Chrome()
    driver.get(url)
    page=90  #总页数page
    login = input('按任意键继续')  #登录
    for i in range(1,page+1):
        print('page'+str(i))
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        data = soup.find_all('div', attrs={'class': "search_result_left"})
        data = str(data)
        partern_name = re.compile(r'display:inline-block;">(.*?)</a>', re.S)
        name = re.findall(partern_name, data)
        partern_url = re.compile(r'<a href="../(.*?)" style=', re.S)
        later_url = re.findall(partern_url, data)
        partern_desc = re.compile(r'<p class="search_result_left_stit">(.*?)</p>', re.S)
        desc = re.findall(partern_desc, data)
        childrenurl = []
        urlroot = 'http://data.zjzwfw.gov.cn/jdop_front/'
        for l in later_url:
            childrenurl.append(urlroot+l)
        for index,childurl in enumerate(childrenurl):
            partern_id = re.compile(r'iid=(.*?)&amp', re.S)
            id = re.findall(partern_id, childurl)
            temp = dict()
            driver.execute_script("window.open('{}')".format(childurl))  #打开子页面
            driver.switch_to.window(driver.window_handles[-1])  #切换到子页面
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            data = soup.find_all('div', attrs={'class': "box1"})
            data = str(data)
            partern_all = re.compile(r'<td>(.*?)</td>', re.S)
            all = re.findall(partern_all, data)
            temp['name']=name[index]
            temp['topic'] = all[15]
            temp['info']=dict()
            temp['info']['id'] = id[0]
            temp['info']['desc'] = desc[index]
            temp['info']['label']=all[3]
            temp['info']['time_gx'] = all[35]
            temp['info']['time'] = all[37]
            logger.info(temp)
            print(temp)
            if i>=1:
                try:
                    driver.find_element_by_xpath("//*[text()='XLS']").click() #点击下载
                    time.sleep(2)
                except:
                    logger.error('无XLS')

                try:
                    driver.find_element_by_xpath("//*[text()='CSV']").click()
                    time.sleep(2)
                except:
                    logger.error('无CSV')

                try:
                    driver.find_element_by_xpath("//*[text()='JSON']").click()
                    time.sleep(2)
                except:
                    logger.error('无JSON')

                try:
                    driver.find_element_by_xpath("//*[text()='XML']").click()
                    time.sleep(2)
                except:
                    logger.error('无XML')

                try:
                    driver.find_element_by_xpath("//*[text()='RDF']").click()
                    time.sleep(2)
                except:
                    logger.error('无RDF')

            driver.close() #关闭页面
            driver.switch_to.window(driver.window_handles[0]) #返回主页面
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
    url_path='http://data.zjzwfw.gov.cn/jdop_front/channal/data_public.do?domainId=&deptId='
    save_path='../info/zhejiang.json'
    zhejiang(url_path,save_path)




