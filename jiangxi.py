from selenium import webdriver
import re
from bs4 import BeautifulSoup
import time
import json
from utilis import *
import os.path as osp
from selenium.webdriver.common.action_chains import ActionChains

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/70.0.3538.110 Safari/537.36'}

url = 'https://data.jiangxi.gov.cn/node/2.jspx'
urlroot='https://data.jiangxi.gov.cn/'


driver = webdriver.Chrome()
driver.get(url)

page=25  #总页数page
login = input('按任意键继续')  #冲洗打开一个页面 登录400 关闭 回原页面刷新

jsontemp=[]
for i in range(1,page+1):

    print('page'+str(i))
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    # print(soup)
    data = soup.find_all('div', attrs={'class': "items items-hover"})
    data = str(data)
    # print(data)

    partern_id = re.compile(r'<a href="//data.jiangxi.gov.cn/(.*?)" target="_blank" title', re.S)
    id = re.findall(partern_id, data)
    childrenurl = []
    for num in range(len(id)):
        childrenurl.append(urlroot + id[num] )
    print('childrenurl')
    print(childrenurl)

    for index, childurl in enumerate(childrenurl):
        driver.execute_script("window.open('{}')".format(childurl))  # 打开子页面
        driver.switch_to.window(driver.window_handles[-1])  # 切换到子页面
        time.sleep(2)
        html = driver.page_source
        # print(html)
        soup = BeautifulSoup(html, 'html.parser')
        data = soup.find_all('div', attrs={'class': "up"})
        data = str(data)
        # print(data)
        partern_name = re.compile(r'<input id="obj_name" type="hidden" value="(.*?)"/>', re.S)
        name = re.findall(partern_name, data)
        partern_topic = re.compile(r'所属主题：(.*?)</li>', re.S)
        topic = re.findall(partern_topic, data)
        partern_time = re.compile(r'<li style="width:200px">发布日期：(.*?)</li>', re.S)
        time_gx = re.findall(partern_time, data)
        print('name')
        print(name)
        # print(topic)
        # print(time_gx)
        temp = dict()
        temp['name']=name[0]
        temp['topic'] = topic[0]
        temp['info']=dict()
        temp['info']['time'] = time_gx[0]
        print('temp'+str(index))
        print(temp)
        if name[0] not in jsontemp:
            jsontemp.append(name[0])
            json_str = json.dumps(temp, ensure_ascii=False)
            with open('demo/jiangxi_before.json', 'a', encoding='utf-8') as f:
                f.write(json_str)
                f.write('\n')
        if i >= 1:
            try:
                mouse=driver.find_element_by_id("dl")
                ActionChains(driver).move_to_element(mouse).perform()
                driver.find_element_by_link_text('json').click()  # 点击下载
                time.sleep(5)
                driver.find_element_by_link_text('csv').click()  # 点击下载
                time.sleep(5)
                driver.find_element_by_link_text('xls').click()  # 点击下载
                time.sleep(5)
            except:
                print('无文件')


        driver.close()  # 关闭页面
        driver.switch_to.window(driver.window_handles[0])  # 返回主页面
        time.sleep(2)
    #可能出现找不到元素
    try:
        driver.find_element_by_xpath("//*[text()='下一页 »']").click()
        time.sleep(10)
    except:
        driver.find_element_by_xpath("//*[text()='下一页 »']").click()
        time.sleep(10)

    print(len(jsontemp))
