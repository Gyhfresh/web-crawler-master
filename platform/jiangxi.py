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
            logging.INFO: os.path.join(dir, 'log\\jiangxi_info.log'),
            logging.ERROR: os.path.join(dir, 'log\\jiangxi_error.log')
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
def jiangxi(url_path,save_path):
    logger.info('开始爬取江西政务数据平台')

    url = url_path
    driver = webdriver.Chrome()
    driver.get(url)
    page=25  #总页数page
    login = input('按任意键继续')  #重新打开一个页面，登录显示400错误，则关闭该，回原页面点击刷新显示登陆成功，若显示令牌错误则服务器坏了

    jsontemp=[]
    for i in range(1,page+1):

        print('page'+str(i))
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        # print(soup)
        data = soup.find_all('div', attrs={'class': "items items-hover"})
        data = str(data)
        # print(data)

        partern_id = re.compile(r'<a href="//data.jiangxi.gov.cn/(.*?)" target="_blank" title', re.S)
        id = re.findall(partern_id, data)
        childrenurl = []
        urlroot = 'https://data.jiangxi.gov.cn/'
        for num in range(len(id)):
            childrenurl.append(urlroot + id[num] )

        for index, childurl in enumerate(childrenurl):
            driver.execute_script("window.open('{}')".format(childurl))  # 打开子页面
            driver.switch_to.window(driver.window_handles[-1])  # 切换到子页面
            time.sleep(2)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            data = soup.find_all('div', attrs={'class': "up"})
            data = str(data)
            partern_name = re.compile(r'<input id="obj_name" type="hidden" value="(.*?)"/>', re.S)
            name = re.findall(partern_name, data)
            partern_topic = re.compile(r'所属主题：(.*?)</li>', re.S)
            topic = re.findall(partern_topic, data)
            partern_time = re.compile(r'<li style="width:200px">发布日期：(.*?)</li>', re.S)
            time_gx = re.findall(partern_time, data)
            temp = dict()
            temp['name']=name[0]
            temp['topic'] = topic[0]
            temp['info']=dict()
            temp['info']['time'] = time_gx[0]
            print(temp)
            logger.info(temp)
            if name[0] not in jsontemp:
                jsontemp.append(name[0])
                json_str = json.dumps(temp, ensure_ascii=False)
                with open(save_path, 'a', encoding='utf-8') as f:
                    f.write(json_str)
                    f.write('\n')
            if i >= 1:
                try:
                    mouse=driver.find_element_by_id("dl")
                    ActionChains(driver).move_to_element(mouse).perform()
                    driver.find_element_by_link_text('json').click()  # 点击下载
                    time.sleep(5)
                    driver.find_element_by_link_text('csv').click()  # 点击下载
                    time.sleep(5)
                    driver.find_element_by_link_text('xls').click()  # 点击下载
                    time.sleep(5)
                except:
                    logger.error('无文件')


            driver.close()  # 关闭页面
            driver.switch_to.window(driver.window_handles[0])  # 返回主页面
            time.sleep(2)
        #可能出现找不到元素
        try:
            driver.find_element_by_xpath("//*[text()='下一页 »']").click()
            time.sleep(10)
        except:
            driver.find_element_by_xpath("//*[text()='下一页 »']").click()
            time.sleep(10)


if __name__=='__main__':
    createHandlers()
    logger = TNLog()
    url_path='https://data.jiangxi.gov.cn/node/2.jspx'
    save_path='../info/jiangxi.json'
    jiangxi(url_path,save_path)
