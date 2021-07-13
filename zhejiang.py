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
url = 'http://data.zjzwfw.gov.cn/jdop_front/channal/data_public.do?domainId=&deptId='  ##domainId=领域/全部
urlroot = 'http://data.zjzwfw.gov.cn/jdop_front/'

driver = webdriver.Chrome()
driver.get(url)

page=90  #总页数page
login = input('按任意键继续')  #登录

for i in range(1,page+1):
    print('page'+str(i))
    ##获取分页面信息：分页面网址，json字段
    html = driver.page_source
    # print(html)
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find_all('div', attrs={'class': "search_result_left"})
    data = str(data)
    # print(data)
    partern_name = re.compile(r'display:inline-block;">(.*?)</a>', re.S)
    name = re.findall(partern_name, data)
    partern_url = re.compile(r'<a href="../(.*?)" style=', re.S)
    later_url = re.findall(partern_url, data)
    partern_desc = re.compile(r'<p class="search_result_left_stit">(.*?)</p>', re.S)
    desc = re.findall(partern_desc, data)
    print('name')
    print(name)
    # print(later_url)
    print('desc')
    print(desc)
    childrenurl = []
    for l in later_url:
        childrenurl.append(urlroot+l)
    print('childrenurl')
    print(childrenurl)

    for index,childurl in enumerate(childrenurl):
        partern_id = re.compile(r'iid=(.*?)&amp', re.S)
        id = re.findall(partern_id, childurl)
        temp = dict()
        driver.execute_script("window.open('{}')".format(childurl))  #打开子页面
        driver.switch_to.window(driver.window_handles[-1])  #切换到子页面
        ##获取页面信息
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        data = soup.find_all('div', attrs={'class': "box1"})
        data = str(data)
        # print(data)
        partern_all = re.compile(r'<td>(.*?)</td>', re.S)
        all = re.findall(partern_all, data)
        temp['name']=name[index]
        temp['topic'] = all[15]
        temp['info']=dict()
        temp['info']['id'] = id[0]
        temp['info']['desc'] = desc[index]
        temp['info']['label']=all[3]
        temp['info']['time_gx'] = all[35]
        temp['info']['time'] = all[37]
        print('temp'+str(index))
        print(childurl)
        print(temp)
        if i>=1:
            try:
                driver.find_element_by_xpath("//*[text()='XLS']").click() #点击下载
                time.sleep(2)
            except:
                print('无XLS')

            try:
                driver.find_element_by_xpath("//*[text()='CSV']").click()
                time.sleep(2)
            except:
                print('无CSV')

            try:
                driver.find_element_by_xpath("//*[text()='JSON']").click()
                time.sleep(2)
            except:
                print('无JSON')

            try:
                driver.find_element_by_xpath("//*[text()='XML']").click()
                time.sleep(2)
            except:
                print('无XML')

            try:
                driver.find_element_by_xpath("//*[text()='RDF']").click()
                time.sleep(2)
            except:
                print('无RDF')

        driver.close() #关闭页面
        driver.switch_to.window(driver.window_handles[0]) #返回主页面
        if i >= 2:
            json_str = json.dumps(temp, ensure_ascii=False)
            with open('demo/zhejiang_before.json', 'a', encoding='utf-8') as f:
                f.write(json_str)
                f.write('\n')

    #可能出现找不到元素
    try:
        driver.find_element_by_xpath("//*[text()='下一页']").click()
        time.sleep(5)
    except:
        driver.find_element_by_xpath("//*[text()='下一页']").click()
        time.sleep(5)




