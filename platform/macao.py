import time
import urllib.request as ur
from selenium import webdriver
from bs4 import BeautifulSoup
import os
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from logging.handlers import RotatingFileHandler
import logging
import inspect


dir = os.path.dirname(__file__)
dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

handlers = {
            logging.INFO: os.path.join(dir, 'log/macao_info.log'),

            logging.ERROR: os.path.join(dir, 'log/macao_error.log'),
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


def info_dict(name, theme, sub_theme, time, data_info):
    data_info_dict = {}
    data_info_dict['name'] = name
    data_info_dict['theme'] = theme
    data_info_dict['info'] = {}
    data_info_dict['info']['sub_theme'] = sub_theme
    data_info_dict['info']['time'] = time
    print(data_info_dict)
    data_info.append(data_info_dict)



def norm_name(name):
    name = "".join(name.split())
    name = re.sub(r"|[\\/:*?\"<>| ]+", "", name)
    return name


#删除路径中所有文件
def del_file(path_data):
    '''
    删除路径中所有文件
    Args:
        path_data: 文件夹路径

    Returns:

    '''
    time.sleep(2)
    for i in os.listdir(path_data):
        file_data = path_data + "\\" + i
        if os.path.isfile(file_data) == True:
            os.remove(file_data)
        else:
            del_file(file_data)


def aomen(base_url, base_url2, save_path):
    logger.info('开始爬取澳门统计暨普查局数据')
    download_dir_xls = save_path
    options = webdriver.ChromeOptions()
    prefs = {'download.default_directory': download_dir_xls, "profile.default_content_setting_values.automatic_downloads":1}
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(chrome_options=options)
    headers = {'USER-AGENT': 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'}

    del_file(download_dir_xls)
    data_info = []
    for i in range(1, 10):
        url = base_url + str(i)

        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="chart-0-title"]'))
        )
        #time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        topic = soup.find('a', attrs={'class':'side-menu__item__link'}).get('title')
        logger.info('开始爬取' + topic + '主题数据')
        sub_topic_soup = soup.find('ul', attrs={'class':'side-menu-sub'}).find_all('li')

        for j in range(1, len(sub_topic_soup)+1):
            if j <10:
                sub_url = url + '0' + str(j)
            else:
                sub_url = url + str(j)
            #print(sub_url)
            driver.get(sub_url)
            try:
                driver.find_elements_by_css_selector("div[class='cell cell__more']>button>span.more")[0].click()
                driver.find_elements_by_css_selector("div[class='cell cell__more']>button>span.more")[1].click()
            except:
                pass
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            publication_soup = soup.find('section', id='publication-container')
            sub_topic = soup.find('h1').text
            logger.info('开始爬取' + sub_topic + '子主题数据')
            print(sub_topic)
            button_soup = publication_soup.find_all('button', attrs={'data-count':'1'}) + publication_soup.find_all('button', attrs={'data-count':'2'})
            time.sleep(0.1)
            for button_item in button_soup:
                data_id = button_item.get('data-id')
                id_click = driver.find_element_by_xpath("//button[@data-id='{}']".format(data_id))
                try:
                    driver.execute_script("arguments[0].click();", id_click)
                    time.sleep(0.2)
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    file_soup = soup.find_all('a', attrs={'class':'file-link'})
                    a = 0
                    for file_item in file_soup:
                        if '表' in file_item.get('title'):
                            a += 1
                            name = soup.find('div', attrs={'class':'file-title'}).text + str(a) + '.xls'
                            name = norm_name(name)
                            print(name)
                            logger.info("开始下载 " + name + " 文件")
                            timee = soup.find('a', attrs={'class':'file-link'}).get('title').split()[0]
                            file_url = file_item.get('href')
                            req = ur.Request(url=file_url, headers=headers)
                            r = ur.urlopen(req)
                            data = r.read()
                            with open(download_dir_xls + '/' + name, 'wb') as f:
                                f.write(data)
                                f.close()
                            info_dict(name, topic, sub_topic, timee, data_info)
                            print(len(data_info))
                        time.sleep(0.2)
                except:
                    logger.error("该文件不存在")
                    continue

            key_indicator_soup = soup.find('section', id='key-indicator')
            file_soup = key_indicator_soup.find_all('a', attrs={'target':'_blank'})
            for file_item in file_soup:
                add_url = file_item.get('href')
                name = file_item.text
                name = norm_name(name) + '.xlsx'
                print(name)
                xls_url = base_url2 + add_url
                driver.get(xls_url)
                driver.switch_to.window(driver.window_handles[-1])
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//a[@class="nav__link"]'))
                )
                #print(driver.page_source)
                #time.sleep(0.2)
                if BeautifulSoup(driver.page_source, 'html.parser').find('p').text[:4] == '更新日期':
                    timee = BeautifulSoup(driver.page_source, 'html.parser').find('p').text[5:]
                else:
                    timee = ''
                down_click = driver.find_element_by_css_selector("a[title='汇出']>i")
                driver.execute_script("arguments[0].click();", down_click)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[text()='显示备注栏']"))
                )
                down_click = driver.find_element_by_xpath("//*[text()='显示备注栏']")
                driver.execute_script("arguments[0].click();", down_click)
                logger.info("开始下载 " + name + " 文件")
                while (True):
                    try:
                        if os.path.exists('./澳门/{}'.format(name)):
                            time.sleep(0.2)
                            os.remove('./澳门/dsec.xlsx')
                            break
                        else:
                            os.rename('./澳门/dsec.xlsx', './澳门/{}'.format(name))
                            info_dict(name, topic, sub_topic, timee, data_info)
                            time.sleep(0.1)
                            print(len(data_info))
                            break
                    except:
                        time.sleep(0.1)

            key_indicator_soup = soup.find('section', id='report')
            file_soup = key_indicator_soup.find_all('a', attrs={'target': '_blank'})
            for file_item in file_soup:
                add_url = file_item.get('href')
                if add_url[:4] == 'http':
                    name = file_item.text
                    name = norm_name(name) + '.pdf'
                    xls_url = add_url
                    file_url = file_item.get('href')
                    req = ur.Request(url=file_url, headers=headers)
                    r = ur.urlopen(req)
                    data = r.read()
                    logger.info("开始下载 " + name + " 文件")
                    timee = ''
                    with open(download_dir_xls + '/' + name, 'wb') as f:
                        f.write(data)
                        f.close()
                    info_dict(name, topic, sub_topic, timee, data_info)
                    print(len(data_info))
                else:
                    xls_url = base_url2 + add_url
                    #print(xls_url)
                    driver.get(xls_url)
                    name = file_item.text
                    name = norm_name(name) + '.xlsx'
                    print(name)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//a[@class="nav__link"]'))
                    )
                    # print(driver.page_source)
                    #time.sleep(0.2)
                    if BeautifulSoup(driver.page_source, 'html.parser').find('p').text[:4] == '更新日期':
                        timee = BeautifulSoup(driver.page_source, 'html.parser').find('p').text[5:]
                    else:
                        timee = ''
                    down_click = driver.find_element_by_css_selector("a[title='汇出']>i")
                    driver.execute_script("arguments[0].click();", down_click)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//*[text()='显示备注栏']"))
                    )
                    down_click = driver.find_element_by_xpath("//*[text()='显示备注栏']")
                    driver.execute_script("arguments[0].click();", down_click)
                    logger.info("开始下载 " + name + " 文件")
                    while (True):
                        try:
                            if os.path.exists('./澳门/{}'.format(name)):
                                time.sleep(0.2)
                                os.remove('./澳门/dsec.xlsx')
                                break
                            else:
                                os.rename('./澳门/dsec.xlsx', './澳门/{}'.format(name))
                                info_dict(name, topic, sub_topic, timee, data_info)
                                time.sleep(0.1)
                                print(len(data_info))
                                break
                        except:
                            time.sleep(0.1)
                            #print(1)
    list_to_json(data_info, os.path.join(dir, '澳门.json'))
    driver.close()

if __name__ == '__main__':
    base_url = 'https://www.dsec.gov.mo/zh-CN/Statistic?id='
    base_url2 = 'https://www.dsec.gov.mo'
    save_path = os.path.join(dir, '澳门')
    aomen(base_url, base_url2, save_path)
    logger.info("数据爬取完成")