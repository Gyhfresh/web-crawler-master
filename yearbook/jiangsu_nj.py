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
            logging.INFO: os.path.join(dir, 'log\jiangsu_nj_info.log'),
            logging.ERROR: os.path.join(dir, 'log\iangsu_nj_error.log')
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

def jiangsu_nj(url_path,save_path):
    logger.info('开始爬取江苏年鉴')
    url = url_path
    driver = webdriver.Chrome()
    driver.get(url)
    login = input('按任意键继续')

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find_all('tbody')
    data = str(data)
    partern_topic = re.compile(r'<td onclick="location\.href.*?">(.*?)</td>', re.S)
    topic = re.findall(partern_topic, data)
    copyt=[]
    for t in topic:
        if t not in copyt:
            copyt.append(t)
            childrenurl=[]
            click_name = t
            click_button = driver.find_element_by_xpath("//*[text()='{}']".format(click_name))
            click_button.click()
            time.sleep(1)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            data0 = soup.find_all('tbody')
            data0 = str(data0)
            partern_url = re.compile(r'class="style9"><a href="(.*?)" target="_blank">', re.S)
            later_url = re.findall(partern_url, data0)
            urlroot = 'http://tj.jiangsu.gov.cn/2020/'
            for l in later_url:
                childrenurl.append(urlroot+l)
            copy=[]
            for index, childurl in enumerate(childrenurl):
                if childurl not in copy and  'xls' not in childurl:
                    copy.append(childurl)
                    temp = dict()
                    try:
                        driver.execute_script("window.open('{}')".format(childurl))  # 打开子页面
                        driver.switch_to.window(driver.window_handles[-1])  # 切换到子页面
                        time.sleep(1)
                        html = driver.page_source
                        table = pd.read_html(html)
                        html_data = pd.DataFrame(table[0])
                        print(html_data[0][0])
                        logger.info(html_data[0][0])
                        temp['name'] = html_data[0][0]+ '2015'
                        temp['topic'] = t
                        temp['info'] = dict()
                        print(temp)
                        logger.info(temp)

                        driver.close()  # 关闭页面
                        driver.switch_to.window(driver.window_handles[0])  # 返回主页面

                        if temp['name']!='简 要  说 明2015' and temp['name']!= '主要统计指标解释2015' and temp['name']!= '编辑人员2015':
                            file = '..\\files\\'+temp['name'] + '.csv'
                            html_data.to_csv(file, encoding='utf_8_sig', index=False)
                            json_str = json.dumps(temp, ensure_ascii=False)
                            with open(save_path, 'a', encoding='utf-8') as f:
                                f.write(json_str)
                                f.write('\n')
                    except:
                        driver.close()  # 关闭页面
                        driver.switch_to.window(driver.window_handles[0])
                        logger.info('页面错误')
                else:
                    pass

if __name__=='__main__':
    createHandlers()
    logger = TNLog()
    url_path='http://tj.jiangsu.gov.cn/2020/indexc.htm'
    save_path='../info/jiangsu_nj.json'
    jiangsu_nj(url_path,save_path)

