import time
import json

from lxml import etree
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from util.TNlogger import TNLog

logger = TNLog(name='山东')


def shandong(url_path, save_path):
    options = ChromeOptions()
    options.add_argument("start-maximized")  # 初始化就最大化
    prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': save_path}
    options.add_experimental_option('prefs', prefs)

    bro = webdriver.Chrome(executable_path='./chromedriver', options=options)
    bro.maximize_window()  # 第一种加载完成后最大化

    bro.get(url_path)
    bro.find_element_by_xpath('//div[contains(text(),"关闭")]').click()
    bro.find_element_by_xpath('//*[@placeholder="登录名/手机号/身份证"]').send_keys(13227716295)
    bro.find_element_by_xpath('//*[@placeholder="请输入密码"]').send_keys('xjtuzhc970922')

    time.sleep(30)

    js = "window.open('http://www.sogou.com')"
    bro.execute_script(js)

    while 1:
        html = etree.HTML(bro.page_source)
        url_list = html.xpath('//div[@class="cata-title"]/a/@href')
        bro.switch_to.window(bro.window_handles[-1])

        for url in url_list:
            url = 'http://data.sd.gov.cn' + url
            bro.get(url)
            time.sleep(1)
            html = etree.HTML(bro.page_source)
            td_list = html.xpath('//li[@name="basicinfo"]/table/tbody//td/text()')
            name = str(html.xpath('//ul[@class="d-title pull-left"]/li/h4/text()')[0]).strip()
            topic = str(html.xpath('//li[contains(text(),"重点领域")]/span/text()')[0]).strip()
            logger.info('开始下载' + name)
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
                with open(save_path + '\\shandong.json', 'a', encoding='utf-8') as f:
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
                logger.error('无法下载文件')
            time.sleep(5)

        bro.switch_to.window(bro.window_handles[0])

        try:
            bro.find_element_by_xpath('//a[contains(text(),"下一页")]').click()
        except:
            logger.error('已到达最后一页')


if __name__ == '__main__':
    url_path = 'http://zwfw.sd.gov.cn/JIS/front/login.do?uuid=kSwamUMs12k2&gotourl=http%3A%2F%2Fdata.sd.gov.' \
               'cn%2Fportal%2Fcatalog%2Findex'
    save_path = 'Z:\\中国移动\\worm\\山东'
    shandong(url_path, save_path)
