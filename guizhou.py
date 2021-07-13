# -*- coding: utf-8 -*- 

import sys
# sys.path.append('.')
# sys.path.append('../')
# sys.path.append('../../')
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
from guizhou.utilis import *
import os.path as osp

# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                          'AppleWebKit/537.36 (KHTML, like Gecko) '
#                          'Chrome/70.0.3538.110 Safari/537.36'}
# download_dir = r'C:\Users\边策\Downloads'
from guizhou.config_crawler import *
print(headers)

base_url = 'http://www.scdata.net.cn/odweb/catalog/'
url = 'http://data.guizhou.gov.cn/data-catalog'
driver = webdriver.Chrome()
driver.get(url)
login = input('按任意键继续')
html = driver.page_source


current_page = 2
soup = BeautifulSoup(html, 'html.parser')
# soup.find_all('a', attrs={'style': 'cursor:pointer'})
# page_num = int(soup.find('ul',attrs = {'class':'el-pager'}).find_all('li')[-1].text）  #获得pagenum
# item = soup.find_all('li',attrs = {'class':'data-item'})

# item = soup.find_all('li',attrs = {'class':'data-item'})[1].find('h4', attrs = {'class':'header-title'}).text
# driver.find_element_by_xpath("//*[text()=' 铜仁市涉企行政事业性收费目录清单 ']").click()
driver.find_elements_by_xpath("//input[@class='el-input__inner']")
from selenium.webdriver.common.keys import Keys
a = driver.find_element_by_xpath("//input[@class='el-input__inner'][@type='number']")
a.click()
a.clear()
a.send_keys('{}'.format(current_page))
a.send_keys(Keys.ENTER)

item = soup.find_all('li',attrs = {'class':'data-item'})
topic_name = item[0].find('span',attrs = {'class':'type'}).text #教育文化
text_name = item[0].find('h4', attrs = {'class':'header-title'}).text
driver.find_element_by_xpath("//*[text()='{}']".format(text_name)).click()


#解析数据信息
html_data = driver.page_source

Soup_data = BeautifulSoup(html_data, 'html.parser')
data_info = Soup_data.find('div',attrs = {'class':'info-main'})
keys_list =  data_info.find_all('h4',attrs = {'class':'name'})
values_list = data_info.find_all('span',attrs = {'class':'value'})
for keys,values in zip(keys_list,values_list):
    print(keys.text.replace('：',''),":",values.text.strip())

#解析下载信息
down_info = Soup_data.find('div',attrs = {'class':'el-tab-pane'})
title_list = down_info.find_all('h4',attrs = {'class':'title'})
content_list = down_info.find_all('p',attrs = {'class':'content'})
driver.find_element_by_xpath("//div[@class='info-wrap']//div[@class='top']//button[2]").click()#下载
for keys,values in zip(title_list,content_list):
    print(keys.text.replace('：',''),":",values.text.strip())
