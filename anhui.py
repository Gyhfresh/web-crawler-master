# -*- coding:utf-8 -*-
from selenium import webdriver
import re
from bs4 import BeautifulSoup
import time
import json
from utilis import *
import os.path as osp

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/70.0.3538.110 Safari/537.36'}

##领域/不限
url = 'http://sjkf.xuancheng.gov.cn/open-data-web/data/list.do?pageIndex=2'
urlroot1 = 'https://data.sh.gov.cn/view/detail/index.html?type=cp&&id='


driver = webdriver.Chrome()
driver.get(url)

page=12  #总页数page
login = input('按任意键继续')  #登录

jsontemp=[]
for i in range(1,page+1):
    print('page'+str(i))
    ##获取分页面信息：分页面网址，json字段
    html = driver.page_source
    # print(html)
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find_all('div', attrs={'id': "listContent"})
    data = str(data)
    # print(data)
    partern_name = re.compile(r'<div class="text ell" data-bind="click:showDetail">(.*?)</div>', re.S)
    name = re.findall(partern_name, data)
    partern_topic = re.compile(r'<div class="content-item ell" title="所属领域：(.*?)">', re.S)
    topic = re.findall(partern_topic, data)
    partern_desc = re.compile(r'<div class="content-item ell" title="摘要描述：(.*?)">', re.S)
    desc = re.findall(partern_desc, data)
    partern_time = re.compile(r'<div class="content-item ell" title="更新时间：(.*?)">', re.S)
    time_gx = re.findall(partern_time, data)
    print('name')
    print(name)
    for index in range(len(name)):
        temp = dict()
        temp['name']=name[index]
        temp['topic'] = topic[index]
        temp['info']=dict()
        temp['info']['desc'] = desc[index]
        temp['info']['time'] = time_gx[index]
        print('temp'+str(index))
        print(temp)
        if name[index] not in jsontemp:
            jsontemp.append(name[index])
            json_str = json.dumps(temp, ensure_ascii=False)
            with open('demo/anhui_before.json', 'a', encoding='utf-8') as f:
                f.write(json_str)
                f.write('\n')
    #可能出现找不到元素
    try:
        driver.find_element_by_xpath("//*[text()='下一页']").click()
        time.sleep(10)
    except:
        driver.find_element_by_xpath("//*[text()='下一页']").click()
        time.sleep(10)
    print(len(jsontemp))




