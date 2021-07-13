 # -*- coding:utf-8 -*-
from selenium import webdriver
import re
from bs4 import BeautifulSoup
import time
import json
from utilis import *
import os.path as osp
import pandas as pd
#

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/70.0.3538.110 Safari/537.36'}

##领域/不限
url = 'http://tj.jiangsu.gov.cn/2015/indexc.htm'
urlroot='http://tj.jiangsu.gov.cn/2015/'
driver = webdriver.Chrome()
driver.get(url)

login = input('按任意键继续')  #点击excel模式

html = driver.page_source
# print(html)
soup = BeautifulSoup(html, 'html.parser')
data = soup.find_all('tbody')
data = str(data)
# print(data)
partern_topic = re.compile(r'<td onclick="location\.href.*?">(.*?)</td>', re.S)
topic = re.findall(partern_topic, data)
print('topic')
print(topic)

copyt=[]
for t in topic:
    if t not in copyt:
        copyt.append(t)
        childrenurl=[]
        click_name = t
        click_button = driver.find_element_by_xpath("//*[text()='{}']".format(click_name))
        click_button.click()
        time.sleep(1)
        html = driver.page_source
        # print(html)
        soup = BeautifulSoup(html, 'html.parser')
        data0 = soup.find_all('tbody')
        data0 = str(data0)
        # print(data0)
        partern_url = re.compile(r'class="style9"><a href="(.*?)" target="_blank">', re.S)
        later_url = re.findall(partern_url, data0)
        for l in later_url:
            childrenurl.append(urlroot+l)
        print('childrenurl')
        print(childrenurl)
        copy=[]
        for index, childurl in enumerate(childrenurl):
            if childurl not in copy and  'xls' not in childurl:
                copy.append(childurl)
                temp = dict()
                try:
                    driver.execute_script("window.open('{}')".format(childurl))  # 打开子页面
                    driver.switch_to.window(driver.window_handles[-1])  # 切换到子页面
                    time.sleep(1)
                    ##获取页面信息
                    html = driver.page_source
                    # print(html)
                    table = pd.read_html(html)
                    html_data = pd.DataFrame(table[0])
                    # print(html_data)
                    print(html_data[0][0])
                    temp['name'] = html_data[0][0]+ '2015'
                    temp['topic'] = t
                    temp['info'] = dict()
                    print(temp)

                    driver.close()  # 关闭页面
                    driver.switch_to.window(driver.window_handles[0])  # 返回主页面

                    if temp['name']!='简 要  说 明2015' and temp['name']!= '主要统计指标解释2015' and temp['name']!= '编辑人员2015':
                        file = 'E:\项目\中国移动\crawl_ctw\demo\jiangsu_nj\\2015\\'+temp['name'] + '.csv'
                        print(file)
                        html_data.to_csv(file, encoding='utf_8_sig', index=False)

                        json_str = json.dumps(temp, ensure_ascii=False)
                        with open('demo/jiangsu_nj_before.json', 'a', encoding='utf-8') as f:
                            f.write(json_str)
                            f.write('\n')
                except:
                    driver.close()  # 关闭页面
                    driver.switch_to.window(driver.window_handles[0])
                    print('页面错误')
            else:
                pass


