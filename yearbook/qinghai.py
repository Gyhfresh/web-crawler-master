from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
import urllib.request as ur
import os.path as osp
import json
from logging.handlers import RotatingFileHandler
import logging
import inspect
import os


dir = os.path.dirname(__file__)
dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

handlers = {
            logging.INFO: os.path.join(dir, 'log/qinghai_nj_info.log'),

            logging.ERROR: os.path.join(dir, 'log/qinghai_nj_error.log'),
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
        doc_list: 包含文件属性信息的列表
        file_name: 存入json文件的名称

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


def qinghai(save_path):
    #base_url = 'http://tjj.qinghai.gov.cn/nj/2020/'
    headers = {'USER-AGENT': 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'}
    #url = 'http://tjj.qinghai.gov.cn/nj/2018/indexch.htm'
    logger.info("开始爬取青海省统计年鉴数据")
    download_dir = save_path
    driver = webdriver.Chrome()
    data_info = []
    for year in range(10, 21):
        base_url = 'http://tjj.qinghai.gov.cn/nj/20{}/'.format(str(year))
        url = 'http://tjj.qinghai.gov.cn/nj/20{}/indexch.htm'.format(str(year))
        print(url)
        logger.info("开始爬取" + "20" + str(year) + "统计年鉴")
        driver.get(url)
        driver.switch_to.frame('contents')#打开#document里的内容
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        tr = soup.find_all('tr')
        foldheader = tr[-1].find_all('li', id='foldheader')
        foldinglist = tr[-1].find_all('ul', id='foldinglist')

        i = 0
        for cata, content in zip(foldheader[1:], foldinglist[1:]):
            title = cata.text.strip().split(' ')
            topic = title[-1]
            logger.info('开始爬取' + topic + '主题数据')
            sections = content.find_all('a')
            for section in sections:
                if section.get('href') == None:
                    continue
                add_url = section.get('href').replace('.htm', '.xls')
                url = base_url + add_url
                name2 = section.text.strip().split(' ')[-1]
                name = ''.join(section.text.strip().split(' ')[1:])
                if not '续' in section.text:
                    main_name = name
                else:
                    name = main_name + '_' + name2

                if section.text.strip() == '主要统计指标解释':
                    continue
                else:
                    try:
                        req = ur.Request(url=url, headers=headers)
                        r = ur.urlopen(req)
                        data = r.read()

                        name = name + '_' + '20' + str(year) + '.xls'
                        if len(name) <= 18:
                            continue
                        print(name)
                        logger.info("开始下载 " + name + " 文件")
                        with open(download_dir + '/' + name, 'wb') as f:
                            f.write(data)
                        i += 1
                        time.sleep(0.1)
                        data_info_dict = {}
                        data_info_dict['name'] = name
                        data_info_dict['theme'] = topic
                        data_info_dict['info'] = {}
                        data_info_dict['info']['time'] = '20' + str(year)
                        print(data_info_dict)
                        data_info.append(data_info_dict)
                    except:
                        logger.error("下载失败")
                        continue


    list_to_json(data_info, os.path.join(dir, '青海统计年鉴.json'))
    driver.close()

if __name__ == '__main__':
    save_path = os.path.join(dir, '青海')
    qinghai(save_path)
    logger.info("数据爬取完成")