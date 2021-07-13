import requests
import json
import os

from lxml import etree
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from tqdm import tqdm
from util.TNlogger import TNLog

logger = TNLog(name='湖南')


def hunan(url_path, save_path, time):
    root = save_path
    root_url = url_path
    os.mkdir(root + time)

    options = ChromeOptions()
    options.add_argument("start-maximized")  # 初始化就最大化
    prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': 'D:\\download\\worm\\湖南'}
    options.add_experimental_option('prefs', prefs)

    bro = webdriver.Chrome(executable_path='./chromedriver', options=options)
    bro.maximize_window()  # 第一种加载完成后最大化

    bro.get(root_url + 'indexce.htm')
    bro.switch_to.frame('contents')
    html = etree.HTML(bro.page_source)
    href_list = html.xpath('//div[@class="menu_body"]/a/@href')
    name_list = html.xpath('//div[@class="menu_body"]/a/text()')
    bro.quit()
    # print(href_list)
    # print(name_list)
    # print(len(href_list))
    # print(len(name_list))

    try:
        for i in tqdm(range(len(href_list))):
            name = name_list[i] + '.' + str(href_list[i]).split('.')[-1]
            url = root_url + href_list[i]
            r = requests.get(url)
            with open(root + time + '\\' + name, 'wb') as f:
                f.write(r.content)

            data = {
                'name': name,
                'time': time,
            }

            logger.info('开始存储' + name)

            with open(root + '湖南.json', 'a', encoding='utf-8') as ff:
                json.dump(data, ff, ensure_ascii=False)
                ff.write('\n')
    except:
        logger.error('无法找到文件')


if __name__ == '__main__':
    url_path = 'http://222.240.193.190/{}tjnj/'.format('10')
    save_path = 'D:\\湖南'
    time = '2010'
    hunan(url_path, save_path, time)
