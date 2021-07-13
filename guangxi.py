import time
import json

from lxml import etree
from selenium import webdriver
from selenium.webdriver import ChromeOptions

options = ChromeOptions()
options.add_argument("start-maximized")  # 初始化就最大化
prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': 'D:\\download\\worm\\guangxi'}
options.add_experimental_option('prefs', prefs)

bro = webdriver.Chrome(executable_path='./chromedriver', options=options)
bro.maximize_window()  # 第一种加载完成后最大化

bro.get('http://data.gxzf.gov.cn/portal/catalog/index?page=1')

time.sleep(30)

js = "window.open('http://www.sogou.com')"
bro.execute_script(js)

while 1:
    html = etree.HTML(bro.page_source)
    url_list = html.xpath('//div[@class="cata-title"]/a/@href')
    bro.switch_to.window(bro.window_handles[-1])

    for url in url_list:
        url = 'http://data.gxzf.gov.cn' + url
        bro.get(url)
        time.sleep(1)
        html = etree.HTML(bro.page_source)
        td_list = html.xpath('//li[@name="basicinfo"]/table/tbody//td/text()')
        name = str(html.xpath('//ul[@class="d-title pull-left"]/li/h4/text()')[0]).strip()
        topic = str(html.xpath('//li[contains(text(),"重点领域")]/span/text()')[0]).strip()
        data_list = []
        info = {}
        for td in td_list:
            str_td = str(td).strip()
            if str_td not in ['', '用户评分', '标签']:
                data_list.append(str_td)

        for i in range(len(data_list)):
            if i % 2 == 0:
                continue
            info[data_list[i - 1]] = data_list[i]

        # print(data)
        # print("----------------------------------------------------")
        time.sleep(1)
        bro.find_element_by_xpath('//li[contains(text(),"数据下载")]').click()
        filenames = etree.HTML(bro.page_source).xpath('//tbody//span[@class="file-name"]/text()')

        for file in filenames:
            data = {
                'name': file,
                'topic': topic,
                'info': info
            }
            with open('D:\\download\\worm\\guangxi\\json\\guangxi.json', 'a', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
                f.write('\n')

        time.sleep(1)
        bro.find_element_by_xpath('//button[contains(text(),"全选")]').click()
        time.sleep(1)
        bro.find_element_by_xpath('//li[@name="file-download"]//button[contains(text(),"批量下载")]').click()
        time.sleep(1)
        try:
            bro.find_element_by_xpath('//div[@class="modal-content"]//input[@name="readed"]').click()
            time.sleep(1)
            bro.find_element_by_xpath('//div[@class="modal-footer"]/button[contains(text(),"批量下载")]').click()
        except:
            pass
        time.sleep(5)

    bro.switch_to.window(bro.window_handles[0])

    try:
        bro.find_element_by_xpath('//a[contains(text(),"下一页")]').click()
    except:
        break
