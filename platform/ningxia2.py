from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
import urllib.request as ur
import os.path as osp
import os
import json
import re
from logging.handlers import RotatingFileHandler
import logging
import inspect


dir = os.path.dirname(__file__)
dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

handlers = {
            logging.INFO: os.path.join(dir, 'log/ningxia_info.log'),

            logging.ERROR: os.path.join(dir, 'log/ningxia_error.log'),
            }


def createHandlers():
    logLevels = handlers.keys()

    for level in logLevels:
        path = os.path.abspath(handlers[level])
        handlers[level] = RotatingFileHandler(path, maxBytes=10000, backupCount=2, encoding='utf-8')

createHandlers()

class TNLog(object):

    def printfNow(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def __init__(self, level=logging.NOTSET):
        self.__loggers = {}

        logLevels = handlers.keys()

        for level in logLevels:
            logger = logging.getLogger(str(level))

            # 如果不指定level，获得的handler似乎是同一个handler?

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

    def warning(self, message):
        message = self.getLogMessage("warning", message)

        self.__loggers[logging.WARNING].warning(message)

    def debug(self, message):
        message = self.getLogMessage("debug", message)

        self.__loggers[logging.DEBUG].debug(message)

    def critical(self, message):
        message = self.getLogMessage("critical", message)

        self.__loggers[logging.CRITICAL].critical(message)


logger = TNLog()


#存入json文件
def list_to_json(doc_list, file_name):
    '''

    Args:
        doc_list: 存放文件属性信息的列表
        file_name: 存入文件名

    Returns: 无

    '''
    for i in range(len(doc_list)):
        if i == 0:
            js = json.dumps(doc_list[i], ensure_ascii=False)
            f = open(file_name, 'w', encoding='utf-8')
            f.write(js + '\n')
            f.close()
        else:
            js = json.dumps(doc_list[i], ensure_ascii=False)
            f = open(file_name, 'a', encoding='utf-8')
            f.write(js + '\n')
            f.close()


#下载文件
def download_file(driver, first_name, item):
    '''

    Args:
        driver: 谷歌浏览器驱动
        first_name: 文件名称的第一段
        item: 包含文件名称第二段的html

    Returns: 文件名称

    '''
    a = driver.find_element_by_xpath("//a[@title='下载']")
    driver.execute_script("arguments[0].click();", a)
    time.sleep(0.1)
    b = driver.find_element_by_xpath("//*[text()='{}']".format('CSV'))
    driver.execute_script("arguments[0].click();", b)
    time.sleep(0.1)
    c = driver.find_element_by_xpath("//div[@class='doneDodnload btn']")
    driver.execute_script("arguments[0].click();", c)
    time.sleep(0.1)
    second_name = item.find(name='span', attrs={'id': id}).text
    name = first_name + second_name + '.csv'
    logger.info("开始下载 " + name + " 文件")
    time.sleep(0.7)
    os.rename('./宁夏数据/宁夏数据.csv', './宁夏数据/{}'.format(name))
    logger.info("下载完成")
    return name


#创建包含文件信息的字典
def get_dict(name, topic, time_span, data_info):
    '''

    Args:
        name: 文件名称
        theme: 文件主题
        time_span: 文件包含信息的时间跨度
        data_info: 存放文件属性信息的列表

    Returns: 无

    '''
    data_dict = {}
    data_dict['name'] = name
    data_dict['theme'] = topic
    data_dict['info'] = {}
    data_dict['info']['time_span'] = time_span
    data_info.append(data_dict)


def ningxia2(url_path, base_url, save_path):
    headers = {'USER-AGENT': 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'}
    add_url_list = ['A0101', 'A0102', 'A0103']
    time_span_list = ['月度', '季度', '年度']

    #download_dir_csv = r''
    options = webdriver.ChromeOptions()
    out_path = save_path  # 是你想指定的路径
    prefs = {'download.default_directory': out_path, "profile.default_content_setting_values.automatic_downloads":1}
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(chrome_options=options)
    time.sleep(3)
    driver.get(url_path)
    logger.info("请登录，登录后按任意键继续")
    input('登录后继续')
    data_info = []
    for add_url, time_span in zip(add_url_list, time_span_list):
        driver.get(base_url + add_url)
        first_name = add_url
        driver.switch_to.window(driver.window_handles[-1])
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        level1 = soup.find_all(name='li', attrs={'class':'level1'})
        #print(level1)
        for level1_item in level1:
            try:
                topic = level1_item.find('a').get('title')
                id = level1_item.get('id') + '_span'
                logger.info('开始爬取' + topic + '主题数据')
                print(topic)
                #driver.find_element_by_xpath("//*[text()='{}']".format('价格指数')).click()
                driver.find_element_by_id(id).click()
                time.sleep(1)
                #print(level1_item)
            except:
                continue
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            level2 = soup.find('li', id=level1_item.get('id')).find_all(name='li', attrs={'class':'level2'})
            for level2_item in level2:
                id = level2_item.get('id') + '_span'
                id_click = driver.find_element_by_id(id)
                driver.execute_script("arguments[0].click();", id_click)
                time.sleep(0.5)
                print(level2_item.a.get('title'))
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                level2_item = soup.find('li', id=level2_item.get('id'))
                #print(level2_item)
                level3 = level2_item.find_all(name='li', attrs={'class':'level3'})
                #print(level3)
                if level3 != []:
                    for level3_item in level3:
                        id = level3_item.get('id') + '_span'
                        id_click = driver.find_element_by_id(id)
                        driver.execute_script("arguments[0].click();", id_click)
                        name = download_file(driver, first_name, level3_item)
                        get_dict(name, topic, time_span, data_info)

                else:
                    name = download_file(driver, first_name, level2_item)
                    get_dict(name, topic, time_span, data_info)

    list_to_json(data_info, os.path.join(dir, '宁夏2.json'))
    driver.close()


if __name__ == '__main__':
    url_path = 'http://nxdata.com.cn/'
    base_url = 'http://nxdata.com.cn/easyquery.htm?cn='
    save_path = os.path.join(dir, '宁夏')
    ningxia2(url_path, base_url, save_path)
    logger.info("数据爬取完成")