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
            logging.INFO: os.path.join(dir, 'log\\shanghai_info.log'),
            logging.ERROR: os.path.join(dir, 'log\\shanghai_error.log')
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
def shanghai(url_path,save_path):
    logger.info('开始爬取上海政务数据平台')
    url = url_path
    driver = webdriver.Chrome()
    driver.get(url)
    page=220  #总页数page
    login = input('按任意键继续')  #登录 点一下数据资源切换掉登录页面
    driver.find_element_by_xpath("//*[text()='数据产品']").click() ##切到数据产品页面
    time.sleep(5)

    for i in range(1,page+1):
        print('page'+str(i))
        ##获取分页面信息：分页面网址，json字段
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        data = soup.find_all('div', attrs={'class': "result-item-wrap"})
        data = str(data)
        partern_name = re.compile(r'title="(.*?)">', re.S)
        name = re.findall(partern_name, data)
        partern_id = re.compile(r'<h3 class="fl title canClick" data-id="(.*?)" data-type', re.S)
        id = re.findall(partern_id, data)
        childrenurl = []
        urlroot1 = 'https://data.sh.gov.cn/view/detail/index.html?type=cp&&id='
        urlroot2 = '&&dataset_name='
        if len(name)==len(id): ##判断页面url是否全部解析
            for num in range(len(name)):
                childrenurl.append(urlroot1+id[num]+urlroot2+name[num])
            for index,childurl in enumerate(childrenurl):
                temp = dict()
                driver.execute_script("window.open('{}')".format(childurl))  #打开子页面
                driver.switch_to.window(driver.window_handles[-1])  #切换到子页面
                time.sleep(2)
                ##获取页面信息
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                data = soup.find_all('table', attrs={'class': "layui-table result-table chanpin-table"})
                data = str(data)
                partern_all = re.compile(r'<td>(.*?)</td>', re.S)
                all = re.findall(partern_all, data)
                if len(all)<12: ##判断页面信息是否解析
                    logger.error("页面解析错误")
                else:
                    temp['name']=name[index]
                    temp['topic'] = all[4]
                    temp['info']=dict()
                    temp['info']['apply'] = all[1]
                    temp['info']['desc'] = all[0]
                    temp['info']['label'] = all[3]
                    temp['info']['country_topic'] = all[5]
                    temp['info']['time_pl'] = all[9]
                    temp['info']['time_gx'] = all[11]
                    temp['info']['time'] = all[10]
                    data = soup.find_all('ul', attrs={'class': "data-download"})
                    data = str(data)
                    # print(data)
                    partern_dename = re.compile(r'<span class="filename">1、(.*?)</span>', re.S)
                    dename = re.findall(partern_dename, data)
                    if len(dename)>=1:
                        temp['info']['dename'] = dename[0]
                    else:
                        temp['info']['dename'] = '格式错误'
                    print(temp)
                    logger.info(temp)
                    if i>=1:
                        try:
                            driver.find_element_by_xpath("//*[text()='xlsx']").click() #点击下载
                            time.sleep(2)
                        except:
                            logger.error('无xlsx')
                        try:
                            driver.find_element_by_xpath("//*[text()='csv']").click()
                            time.sleep(2)
                        except:
                            logger.error('无csv')
                        try:
                            driver.find_element_by_xpath("//*[text()='xls']").click()
                            time.sleep(2)
                        except:
                            logger.error('无xls')
                        try:
                            driver.find_element_by_xpath("//*[text()='json']").click()
                            time.sleep(2)
                        except:
                            logger.error('无json')
                    driver.close() #关闭页面
                    driver.switch_to.window(driver.window_handles[0]) #返回主页面
                    time.sleep(2)
                    if i >= 1:
                        json_str = json.dumps(temp, ensure_ascii=False)
                        with open(save_path, 'a', encoding='utf-8') as f:
                            f.write(json_str)
                            f.write('\n')
        else:
            logger.error('页面url解析错误')

        try:
            driver.find_element_by_xpath("//*[text()='下一页']").click()
            time.sleep(5)
        except:
            driver.find_element_by_xpath("//*[text()='下一页']").click()
            time.sleep(5)


if __name__=='__main__':
    createHandlers()
    logger = TNLog()
    url_path='https://data.sh.gov.cn/view/data-resource/index.html'
    save_path='../info/shanghai.json'
    shanghai(url_path,save_path)



