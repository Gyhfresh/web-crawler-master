from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
import urllib.request as ur
import os.path as osp
import json
import re
from logging.handlers import RotatingFileHandler
import logging
import inspect
import os


dir = os.path.dirname(__file__)
dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

handlers = {
            logging.INFO: os.path.join(dir, 'log/hongkong_info.log'),

            logging.ERROR: os.path.join(dir, 'log/hongkong_error.log'),
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

#写入json文件
def list_to_json(doc_list, file_name):
    '''

    Args:
        doc_list: 包含文件属性信息的列表
        file_name: json文件名称

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


#规范化文件名称
def norm_name(name):
    '''
    规范化文件名称
    Args:
        name: 规范化前文件名称

    Returns: 文件名称

    '''
    name = "".join(name.split())
    name = re.sub(r"|[\\/:*?\"<>| ]+", "", name)
    return name


#获取下拉页面信息
def get_page(new_url, download_dir_csv, headers):
    logger.info("打开该页面所有下拉信息")
    for i in range(1, 30):
        page_url = new_url + '?page=' + str(i)
        try:
            source = requests.get(page_url, headers=headers).text
            page_soup = BeautifulSoup(source, 'html.parser')
            if page_soup.find(name='div', attrs={'class':'dataset-item'}) == None:
                break
            else:
                page_item_list = page_soup.find_all(name='h3', attrs={'class':'dataset-heading'})
                for item in page_item_list:
                    data_url = base_url + item.a.get('href')
                    try:
                        data_html = requests.get(data_url, headers=headers).text
                        data_soup = BeautifulSoup(data_html, 'html.parser')
                        info = get_info(data_soup)
                        logger.info("获取" + info['page_name'] + "页面信息")
                        resource = data_soup.find(name='div', attrs={'class': 'data-resource-list'})
                        resource_item = resource.find_all(name='div', attrs={'class': 'row item'})
                        last_name = ''
                        i = 0
                        for item in resource_item:
                            try:
                                file_url = item.get('data-resource-url')
                                last_name = get_file(file_url, item, info, last_name, i, info['page_name'], download_dir_csv)
                            except:
                                continue
                    except:
                        continue
        except:
            logger.error("该页面为空")
            continue



def get_file(file_url, item, info, last_name, i, page_name, download_dir_csv):
    '''
    获取文件
    Args:
        file_url: 下载文件的url
        item: 包含文件信息的html标签
        info: 文件其他信息的字典
        last_name: 文件名称的最后一段
        i: 用于同一网页相同文件名的区分的数字
        page_name: 网页名称

    Returns: html中保存的未经处理的文件名称

    '''
    if item.get('data-resource-format') == 'CSV':
        req = ur.Request(url=file_url, headers=headers)
        r = ur.urlopen(req)
        data = r.read()
        name = item.get('data-resource-title-sc')
        last = name
        if name == last_name:
            i += 1
            name = name + '_' + str(i)
        name = page_name + '_' +name
        name = norm_name(name)
        if '简' in name[-10:-2] or '簡' in name[-10:-2]:
            print(name)
            logger.info("开始下载 " + name + ".csv 文件")
            with open(download_dir_csv + '/' + name + '.csv', 'wb') as f:
                f.write(data)
            date = item.get('data-resource-last-update-date')
            data_dict = {}
            data_dict['name'] = name + '.csv'
            data_dict['theme'] = topic
            data_dict['info'] = info
            data_dict['info']['date'] = date
            print(data_dict)
            data_info.append(data_dict)
            data_info_sub.append(data_dict)
        #time.sleep(0.3)
    return last


#获取其他信息
def get_info(data_soup):
    '''

    Args:
        data_soup: 包含文件其他信息的html标签

    Returns:

    '''
    info = {}
    page_name = data_soup.find(name='h1', attrs={'class':'header-label'}).text
    info['page_name'] = page_name
    department = data_soup.find(name='a', attrs={'class':'provider-label'}).text
    info['department'] = department
    update_frq = data_soup.find(name='span', attrs={'class':'update-frequency-area'}).text
    info['update_frq'] = update_frq
    return info


def hongkong(url_path, base_url, save_path):
    logger.info("开始爬取香港资料一线通数据")
    base_url = base_url
    headers = {'USER-AGENT': 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'}
    url = url_path

    download_dir_csv = save_path
    driver = webdriver.Chrome()
    driver.get(url)
    html = driver.page_source

    #print(html)
    #input('继续')
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find(name='div', attrs={'class':'carousel-inner browse-slider'})
    flex_row = content.find_all('a')
    #print(flex_row)
    data_info = []

    for item in flex_row:
        data_info_sub = []
        topic = item.find('div').text
        print(topic)
        logger.info('开始爬取' + topic + '主题数据')
        add_url = item.get('href')
        #print(add_url)
        new_url = base_url + add_url
        logger.info("获取" + new_url + "页面数据")
        get_page(new_url, download_dir_csv, headers)
        json_dir = 'data_info_' + topic + '.json'
        #list_to_json(data_info_sub, json_dir)

    list_to_json(data_info, os.path.join(dir, '香港.json'))
    #print(len(data_info))
    driver.close()

if __name__ == '__main__':
    url_path = 'https://data.gov.hk/sc/'
    base_url = 'https://data.gov.hk'
    save_path = os.path.join(dir, '香港')
    print(save_path)
    hongkong(url_path, base_url, save_path)
    logger.info("数据爬取完成")