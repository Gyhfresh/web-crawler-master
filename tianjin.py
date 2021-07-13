from selenium import webdriver
import re
from bs4 import BeautifulSoup
import time
# 导入库，其中selenium用于模拟浏览器操作，bs4用于解析页面，time库用于计算时间，保证页面的更新时间

download_dir = "/北京"
chrome_options = webdriver.ChromeOptions()
preferences = {"download.default_directory": download_dir ,
               "directory_upgrade": True,
               "safebrowsing.enabled": True }
chrome_options.add_experimental_option("prefs", preferences)
# 修改浏览器默认操作，防止因浏览器的提示而导致的程序报错


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/70.0.3538.110 Safari/537.36'}
# 传入headers

##领域/不限
url = 'https://data.tj.gov.cn/sjj/index.htm'
# urlroot = 'https://data.beijing.gov.cn/'
# https://data.beijing.gov.cn/cms/web/bjdata/sso/ssoLogin.jsp
# 三个网址分别为要爬取数据的网址、主页面、登陆页面

driver = webdriver.Chrome()
time.sleep(1)
driver.get(url)
# 直接获取网站信息
# driver.find_element_by_xpath("//*[text()='登录/注册']").click()


login = input('按任意键继续')  #登录
html = driver.page_source
time.sleep(1)
# 此时在浏览器中人工实现登录操作，因其有图片验证码，所以无法进行自动化处理

print(html)

time.sleep(1)
# driver.find_element_by_xpath("//*[text()='尾页']").click()
# print('到尾页了')

windows1 = driver.window_handles

time.sleep(2)
page=1
while page<15:
    page=page+1
    print(page)
    time.sleep(1)
    driver.find_element_by_xpath("//span[contains(text(),'无条件开放')]").click()
    windows = driver.window_handles
    driver.switch_to.window(windows[-1])
    time.sleep(1)
    driver.find_element_by_xpath("//*[text()='文件下载']").click()
    windows = driver.window_handles
    driver.switch_to.window(windows[-1])
    time.sleep(1)
    driver.find_element_by_xpath("//*[text()='下载']").click()
    driver.switch_to.window(windows1[-1])
    for i in range(1,10):
        try:
            driver.find_elements_by_xpath("//span[contains(text(),'无条件开放')]")[i].click()
            windows = driver.window_handles
            driver.switch_to.window(windows[-1])
            time.sleep(1)
            driver.find_element_by_xpath("//*[text()='文件下载']").click()
            windows = driver.window_handles
            driver.switch_to.window(windows[-1])
            time.sleep(1)
            driver.find_element_by_xpath("//*[text()='下载']").click()
            time.sleep(1)
            driver.close()
            driver.switch_to.window(windows1[-1])

        except:
            continue

    driver.find_element_by_xpath("//a[text()='》']").click()
    time.sleep(2)





