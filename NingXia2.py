from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
import urllib.request as ur
import os.path as osp
import os
import json
import re


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
    time.sleep(0.7)
    os.rename('./宁夏数据/宁夏数据.csv', './宁夏数据/{}'.format(name))
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


base_url = 'http://nxdata.com.cn/easyquery.htm?cn='
headers = {'USER-AGENT': 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'}
url = 'http://nxdata.com.cn/'
add_url_list = ['A0101', 'A0102', 'A0103']
time_span_list = ['月度', '季度', '年度']

#download_dir_csv = r''
options = webdriver.ChromeOptions()
out_path = r'D:\YangChenyang\项目\中国移动项目\宁夏\宁夏数据'  # 是你想指定的路径
prefs = {'download.default_directory': out_path, "profile.default_content_setting_values.automatic_downloads":1}
options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(chrome_options=options)
time.sleep(3)
driver.get(url)
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

list_to_json(data_info, 'data_info.json')
driver.close()
