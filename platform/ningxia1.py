from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
import urllib.request as ur
import os.path as osp
import os
import json
import re
import inspect
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

#删除路径中所有文件
def del_file(path_data):
    '''

    Args:
        path_data: 文件夹路径

    Returns: 无

    '''
    for i in os.listdir(path_data):
        file_data = path_data + "\\" + i
        if os.path.isfile(file_data) == True:
            os.remove(file_data)
        else:
            del_file(file_data)


#点击文件时间
def click_time(time_soup, driver):
    '''

    Args:
        time_soup: 包含文件时间的html标签
        driver: 浏览器驱动

    Returns: 文件时间

    '''
    timee = time_soup.text
    d = driver.find_element_by_xpath("//*[text()='{}']".format(timee))
    print(timee)
    driver.execute_script("arguments[0].click();", d)
    time.sleep(0.2)
    return timee


#获取选择时间的html标签
def get_time_list(driver):
    '''

    Args:
        driver: 浏览器标签

    Returns: 包含文件时间列表的html标签

    '''
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    time_list = soup.find(name='div', attrs={'class': 'dtList'}).find_all('li')
    return  time_list


#创建文件信息的字典
def get_data_dict(name, topic, time_span, timee):
    '''

    Args:
        name: 文件名称
        topic: 文件主题
        time_span: 文件包含信息的时间跨度
        timee: 文件时间

    Returns: 存放文件信息的字典

    '''
    data_dict = {}
    data_dict['name'] = name
    data_dict['theme'] = topic
    data_dict['info'] = {}
    data_dict['info']['time_span'] = time_span
    data_dict['info']['time'] = timee
    return data_dict


#写入json文件
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



def download_file(driver, first_name, level_item, timee, area):
    '''
    下载文件
    Args:
        driver: 浏览器驱动
        first_name: 文件名称的第一段
        level_item: 包含文件名称第二段的html
        timee: 文件时间
        area: 文件相关地区

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
    second_name = level_item.find(name='span', attrs={'id': id}).text
    name = first_name + second_name + timee + '_' + area + '.csv'
    logger.info("开始下载 " + name + " 文件")
    time.sleep(0.7)
    os.rename(download_dir_xls + '/宁夏数据.csv', download_dir_xls + '/{}'.format(name))
    logger.info("下载完成")
    return name


def ningxia1(url_path, base_url, save_path):
    headers = {'USER-AGENT': 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'}
    url = url_path
    add_url_list = ['D0100', 'D0101', 'D0102']
    time_span_list = ['月度', '季度', '年度']
    download_dir_xls = save_path
    options = webdriver.ChromeOptions()
    prefs = {'download.default_directory': download_dir_xls, "profile.default_content_setting_values.automatic_downloads":1}
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(chrome_options=options)
    del_file(download_dir_xls)
    time.sleep(3)
    driver.get(url)
    logger.info("请登录，登录后按任意键继续")
    input('登录后继续')
    data_info = []
    for add_url, time_span in zip(add_url_list, time_span_list):
        logger.info("开始爬取时间跨度为" + time_span + "的数据")
        driver.get(base_url + add_url)
        first_name = add_url
        driver.switch_to.window(driver.window_handles[-1])
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        level1 = soup.find_all(name='li', attrs={'class':'level1'})
        area_click = driver.find_element_by_xpath("//span[text()='地区']")
        driver.execute_script("arguments[0].click();", area_click)
        time.sleep(0.7)
        area_click = driver.find_element_by_xpath("//span[text()='宁夏回族自治区']")
        driver.execute_script("arguments[0].click();", area_click)
        time.sleep(0.7)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        level2_area = soup.find_all(name='li', attrs={'class': 'level2'})
        for area_item in level2_area:
            area = area_item.find('a').get('title')
            print(area)
            if area != '全部市区':
                logger.info("开始爬取 " + area + " 数据")
                id = area_item.get('id') + '_span'
                id_click = driver.find_element_by_id(id)
                driver.execute_script("arguments[0].click();", id_click)
                time.sleep(0.5)

            for level1_item in level1:
                try:
                    topic = level1_item.find('a').get('title')
                    id = level1_item.get('id') + '_span'
                    print(topic)
                    logger.info('开始爬取' + topic + '主题数据')
                    id_click = driver.find_element_by_id(id)
                    driver.execute_script("arguments[0].click();", id_click)
                    time.sleep(1)
                except:
                    logger.error("加载错误")
                    continue
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                level2 = soup.find('li', id=level1_item.get('id')).find_all(name='li', attrs={'class':'level2'})
                if level2 != []:
                    for level2_item in level2:
                        id = level2_item.get('id') + '_span'
                        id_click = driver.find_element_by_id(id)
                        driver.execute_script("arguments[0].click();", id_click)
                        time.sleep(0.3)
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
                                driver.find_element_by_css_selector('div.dtHtml>div').click()
                                time_list = get_time_list(driver)
                                for time_soup in time_list:
                                    node = time_soup.get('node')
                                    sort = eval(node)['sort']
                                    if sort == '1':
                                        timee = click_time(time_soup, driver)
                                        name = download_file(driver, first_name, level3_item, timee, area)
                                        data_dict = get_data_dict(name, topic, time_span, timee)
                                        data_info.append(data_dict)
                                        print(data_dict)

                        else:
                            driver.find_element_by_css_selector('div.dtHtml>div').click()
                            time_list = get_time_list(driver)
                            for time_soup in time_list:
                                node = time_soup.get('node')
                                sort = eval(node)['sort']
                                if sort == '1':
                                    timee = click_time(time_soup, driver)
                                    name = download_file(driver, first_name, level2_item, timee, area)
                                    data_dict = get_data_dict(name, topic, time_span, timee)
                                    data_info.append(data_dict)
                                    print(data_dict)
                else:
                    driver.find_element_by_css_selector('div.dtHtml>div').click()
                    time_list = get_time_list(driver)
                    for time_soup in time_list:
                        node = time_soup.get('node')
                        sort = eval(node)['sort']
                        if sort == '1':
                            timee = click_time(time_soup, driver)
                            name = download_file(driver, first_name, level1_item, timee, area)

                            data_dict = get_data_dict(name, topic, time_span, timee)
                            data_info.append(data_dict)
                            print(data_dict)
    list_to_json(data_info, os.path.join(dir, '宁夏.json'))
    driver.close()

if __name__ == '__main__':
    url_path = 'http://nxdata.com.cn/'
    base_url = 'http://nxdata.com.cn/easyquery.htm?cn='
    save_path = os.path.join(dir, '宁夏')
    ningxia1(url_path, base_url, save_path)
    logger.info("数据爬取完成")
