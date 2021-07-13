 # -*- coding:utf-8 -*-
from selenium import webdriver
import re
from bs4 import BeautifulSoup
import time
import json
from utilis import *
import os.path as osp
#
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/70.0.3538.110 Safari/537.36'}

##领域/不限
url = 'http://tjj.hlj.gov.cn/app/tongjnj/2020/zk/indexch.htm'
driver = webdriver.Chrome()
driver.get(url)

login = input('按任意键继续')  #点击excel模式


driver.switch_to.frame(1)
html = driver.page_source
# print(html)
soup = BeautifulSoup(html, 'html.parser')
data = soup.find_all('ul')
# print(data)
data = str(data)
# print(data)
partern_topic = re.compile(r'<li id="foldheader">(.*?)</li>', re.S)
topic = re.findall(partern_topic, data)
partern_name = re.compile(r'<a href="html/.*?xls">([0-9].*?)</a></li>', re.S)
name = re.findall(partern_name, data)
print('topic')
print(topic)
print('name')
print(name)

temp=dict()
for n in name:
    partern_id = re.compile(r'([0-9]+)-[0-9]+ ', re.S)
    id = re.findall(partern_id, n)
    # print(id)
    try:
        if id[0] in temp:
            if n not in temp[id[0]]:
                temp[id[0]].append(n)
        else:
            temp[id[0]]=[n]
    except:
        print('附录不要')
print(temp)

for index,t in enumerate(topic[1:-1]):
    print(t)
    click_name=t
    click_button = driver.find_element_by_xpath("//*[text()='{}']".format(click_name))
    click_button.click()
    time.sleep(2)
    for file in temp[str(index+1)]:
        click_name = file
        try:
            click_button = driver.find_element_by_xpath("//*[text()='{}']".format(click_name))
            click_button.click()
            time.sleep(2)
        except:
            print('无文件')
        table=dict()
        table['name'] = file
        table['topic'] = t
        table['info'] = dict()
        print(table)
        json_str = json.dumps(table, ensure_ascii=False)
        with open('demo/heilongjiang_nj_before.json', 'a', encoding='utf-8') as f:
            f.write(json_str)
            f.write('\n')
