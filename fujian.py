# -*- coding:utf-8 -*-
from selenium import webdriver
import re
from bs4 import BeautifulSoup
import time
import json
from utilis import *
import os.path as osp
from selenium.webdriver.common.action_chains import ActionChains

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


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/70.0.3538.110 Safari/537.36'}

##领域/不限
url = 'https://data.fujian.gov.cn/oportal/catalog/index?fileFormat=1&openType=1&page=1'
urlroot1 = 'https://data.fujian.gov.cn/oportal/catalog/'


driver = webdriver.Chrome()
driver.get(url)

page=2  #总页数page
login = input('按任意键继续')  #登录

url = 'https://data.fujian.gov.cn/oportal/catalog/index?domainId=sub-9&fileFormat=1&openType=1&page=1'
driver.get(url) #重新定位页面  领域有问题 建议分页爬 修改总页数

for i in range(1,page+1):
    print('page'+str(i))
    ##获取分页面信息：分页面网址，json字段
    html = driver.page_source
    # print(html)
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find_all('div', attrs={'class': "bottom-content"})
    data = str(data)
    # print(data)
    partern_name = re.compile(r'target="_blank" title="">(.*?)</a>', re.S)
    name = re.findall(partern_name, data)
    partern_id = re.compile(r'<a href="/oportal/catalog/(.*?)" target="_blank" ', re.S)
    id = re.findall(partern_id, data)
    partern_topic = re.compile(r'<span class="blue education">(.*?)</span>', re.S)
    topic = re.findall(partern_topic, data)
    print('name')
    print(name)
    print('id')
    print(id)
    # print('topic')
    # print(topic)
    childrenurl = []
    for num in range(len(id)):
        childrenurl.append(urlroot1+id[num])
    print('childrenurl')
    print(childrenurl)
    for index,childurl in enumerate(childrenurl):
        temp = dict()
        driver.execute_script("window.open('{}')".format(childurl))  #打开子页面
        driver.switch_to.window(driver.window_handles[-1])  #切换到子页面
        time.sleep(2)
        ##获取页面信息
        html = driver.page_source
        # print(html)
        soup = BeautifulSoup(html, 'html.parser')
        # print(soup)
        data = soup.find_all('div', attrs={'class': "panel-body"})
        data = str(data)
        # print(data)
        partern_all = re.compile(r'<td>(.*?)</td>', re.S)
        all = re.findall(partern_all, data)
        # print(all)

        temp['name']=name[index]
        temp['topic'] = clean(topic[index])
        temp['info']=dict()

        partern_desc = re.compile(r'<td colspan="3">([^\n].*?)</td>', re.S)
        desc = re.findall(partern_desc, data)
        temp['info']['desc'] = desc[0]
        temp['info']['label'] = clean(all[3])
        temp['info']['time_pl'] = clean(all[9])
        temp['info']['time_gx'] = clean(all[7])
        temp['info']['time'] = clean(all[5])

        print('temp'+str(index))
        print(childurl)
        print(temp)
        if i>=1:
            driver.find_element_by_xpath("//*[text()='数据下载']").click()  # 点击下载
            time.sleep(5)
            driver.find_element_by_xpath("//*[text()='全选']").click()  # 点击下载
            time.sleep(5)
            driver.find_element_by_xpath("//*[text()='批量下载']").click() #点击下载
            time.sleep(5)

        driver.close() #关闭页面
        driver.switch_to.window(driver.window_handles[0]) #返回主页面
        time.sleep(2)
        if i >= 1:
            json_str = json.dumps(temp, ensure_ascii=False)
            with open('demo/fujian_before.json', 'a', encoding='utf-8') as f:
                f.write(json_str)
                f.write('\n')

    #可能出现找不到元素
    try:
        driver.find_element_by_xpath("//*[text()='下一页']").click()
        time.sleep(5)
    except:
        driver.find_element_by_xpath("//*[text()='下一页']").click()
        time.sleep(5)




