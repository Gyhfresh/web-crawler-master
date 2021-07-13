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
    return string2

def kong(string):
    if string=='':
        return 'none'
    else:
        return string


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/70.0.3538.110 Safari/537.36'}

##领域/不限
url = 'http://data.harbin.gov.cn/odweb/catalog/index.htm'
urlroot1 = 'http://data.harbin.gov.cn/odweb/catalog/catalogDetail.htm?cata_id='


driver = webdriver.Chrome()
driver.get(url)

page=189  #总页数page
login = input('按任意键继续')  #登录

driver.find_element_by_xpath("//*[text()='数据集']").click() ##切到数据集
time.sleep(5)

for i in range(1,page+1):
    print('page'+str(i))
    ##获取分页面信息：分页面网址，json字段
    html = driver.page_source
    # print(html)
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find_all('div', attrs={'class': "m-cata-list"})
    data = str(data)
    # print(data)
    partern_id = re.compile(r'class="item-title"> <a href="catalogDetail.htm\?cata_id=(.*?)" target="_blank">', re.S)
    id = re.findall(partern_id, data)
    print('id')
    print(id)
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
        data = soup.find_all('div', attrs={'class': "info-body"})
        data = str(data)
        # print(data)
        partern_all = re.compile(r'<div class="info-body">(.*?)</div>', re.S)
        all = re.findall(partern_all, data)
        # print(all)
        temp['name']=all[0]
        temp['topic'] = all[2]
        temp['info']=dict()
        temp['info']['desc'] = all[10]
        temp['info']['label'] = kong(all[9])
        temp['info']['time_gx'] = clean(all[3])
        temp['info']['time'] = clean(all[8])

        print('temp'+str(index))
        print(childurl)
        print(temp)
        if i>=1:
            try:
                driver.find_element_by_xpath("//*[text()='文件下载']").click()  # 点击下载
                time.sleep(5)
                try:
                    driver.find_element_by_xpath("//*[text()='下载']").click()  # 点击下载
                    time.sleep(5)
                except:
                    print('无XLSX')

                try:
                    driver.find_element_by_xpath("//li[text()='XML']").click()  # 点击下载
                    time.sleep(5)
                    try:
                        driver.find_element_by_link_text('下载').click()
                        time.sleep(2)
                    except:
                        print('无XML')
                except:
                    print("服务器异常")

                try:
                    driver.find_element_by_xpath("//li[text()='JSON']").click()  # 点击下载
                    time.sleep(5)
                    try:
                        driver.find_element_by_link_text('下载').click()
                        time.sleep(2)
                    except:
                        print('无JSON')
                except:
                    print("服务器异常")

                try:
                    driver.find_element_by_xpath("//li[text()='CSV']").click()  # 点击下载
                    time.sleep(5)
                    try:
                        driver.find_element_by_link_text('下载').click()
                        time.sleep(2)
                    except:
                        print('无CSV')
                except:
                    print("服务器异常")

                try:
                    driver.find_element_by_xpath("//li[text()='JSON']").click()  # 点击下载
                    time.sleep(5)
                    try:
                        driver.find_element_by_link_text('下载').click()
                        time.sleep(2)
                    except:
                        print('无JSON')
                except:
                    print("服务器异常")
            except:
                print("服务器异常")

        driver.close() #关闭页面
        driver.switch_to.window(driver.window_handles[0]) #返回主页面
        time.sleep(2)
        if i >= 1:
            json_str = json.dumps(temp, ensure_ascii=False)
            with open('demo/haerbin_before.json', 'a', encoding='utf-8') as f:
                f.write(json_str)
                f.write('\n')

    #可能出现找不到元素
    try:
        driver.find_element_by_xpath("//*[text()='下一页']").click()
        time.sleep(5)
    except:
        driver.find_element_by_xpath("//*[text()='下一页']").click()
        time.sleep(5)




