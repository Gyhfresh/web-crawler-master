from selenium import webdriver
import re
from bs4 import BeautifulSoup
import time
from util.TNlogger import TNLog

logger = TNLog(name='北京平台')

# 导入库，其中selenium用于模拟浏览器操作，bs4用于解析页面，time库用于计算时间，保证页面的更新时间

download_dir = "/北京"
chrome_options = webdriver.ChromeOptions()
preferences = {"download.default_directory": download_dir,
               "directory_upgrade": True,
               "safebrowsing.enabled": True}
chrome_options.add_experimental_option("prefs", preferences)
# 修改浏览器默认操作，防止因浏览器的提示而导致的程序报错


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/70.0.3538.110 Safari/537.36'}
# 传入headers

##领域/不限
url = 'https://data.beijing.gov.cn/search/query/zhuti_index.html'
urlroot = 'https://data.beijing.gov.cn/'
# https://data.beijing.gov.cn/cms/web/bjdata/sso/ssoLogin.jsp
# 三个网址分别为要爬取数据的网址、主页面、登陆页面

driver = webdriver.Chrome()
driver.get(url)
# 直接获取网站信息

login = input('按任意键继续')  # 登录
html = driver.page_source


# 此时在浏览器中人工实现登录操作，因其有图片验证码，所以无法进行自动化处理

# print(html)
def get_childurl():
    """

    :return:
    """
    childrenurl = []
    page = 0
    while page < 600:
        # 进行循环，人工看到网站大概五百多页，每一页有十个分页面的网址
        # print(page)
        html = driver.page_source
        if page > 0:
            # 翻页操作之后，各页面的网址未发生变化，所以考虑实现模拟点击翻页
            try:
                driver.find_element_by_xpath("//*[text()='下一页']").click()
            except:
                logger.info('目前没有下一页了')
                # print('没有下一页')
                break
            time.sleep(1)
            html = driver.page_source
        page += 1
        soup = BeautifulSoup(html, 'html.parser')
        data = soup.find_all('h2', attrs={'style': "font-size: 22px;"})
        # 寻找页面解析代码之中的分页面代码，命名为data
        data = str(data)
        # print(data)
        partern_url = re.compile(r'<a href="(.*?)" target="_blank"', re.S)
        later_url = re.findall(partern_url, data)
        for l in later_url:
            childrenurl.append(l)
        logger.info('共得到' + str(len(childrenurl)) + '个子网站')
        # print(len(childrenurl))
        # 将每一页的分页面网址存入一个列表并返回，利于后续的遍历访问
    return childrenurl


childrenurl = get_childurl()
childrenurl = list(reversed(childrenurl))
# print(childrenurl)
f = open('北京后300.txt', 'a+')
# 获取分页面所有的网址，并创建txt用于存储各文件的附件信息

num = 1
# 创建变量num用于计数
for index, childurl in enumerate(childrenurl):

    # 遍历每一个分页面的网址
    # print(num)
    logger.info('目前num为' + str(num))
    num += 1
    # if num > 300:
    #     continue
    # if num > 3000:
    #     break
    try:
        # print(childurl)
        driver.execute_script("window.open('{}')".format(childurl))  # 打开子页面
        time.sleep(0.5)
        driver.close()
        time.sleep(0.5)
        driver.switch_to.window(driver.window_handles[-1])  # 切换到子页面
        time.sleep(1)
        # 打开子页面并切换到子页面，随后进行time.sleep操作等待页面加载

        try:
            time.sleep(1)
            driver.find_element_by_xpath("//*[text()='下载']").click()

        except:
            logger.info('该界面没有下载键')

            continue
        try:
            time.sleep(1)
            driver.find_elements_by_xpath("//*[text()='下载']")[1].click()
            # driver.find_elements_by_xpath("//*[text()='下载']")[2].click()
        except:
            pass
        # 模拟点击所有的下载键，利用driver.find_element_by_xpath寻找第一个下载键，如果没有就退出循环，进入到下一次的循环；如果有则探究更多的下载键，如果没有则跳过

        try:
            time.sleep(1)
            driver.find_element_by_xpath("//*[text()='数据信息']").click()
            time.sleep(1)
        except:

            continue
        # print('有这个键')
        # driver.find_element_by_xpath("//*[text()='数据信息']").click()  # 点击下载
        ##获取页面信息
        html = driver.page_source
        time.sleep(1)
        soup = BeautifulSoup(html, 'html.parser')
        # print(soup)
        data = soup.find_all('iframe', attrs={'width': "800"})
        data = str(data)
        # print(data)
        pattern_url = re.compile(r'src="(.*?)"', re.S)
        information_url = re.findall(pattern_url, data)
        # print(information_url[0])

        data = soup.find_all('div', attrs={'class': "sjdetails_boxinfo_l"})
        data = str(data)
        # print(data)
        namezz = re.compile(r'a title="(.*?)"', re.S)
        namebe = re.findall(namezz, data)

        name = str(str(namebe[0]).split('.')[0])
        # print(name)

        chchildurl = urlroot + str(information_url[0])
        driver.execute_script("window.open('{}')".format(chchildurl))  # 打开子页面
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])  # 切换到子页面
        time.sleep(1)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        fujian = soup.find('pre', attrs={'style': "word-wrap: break-word; white-space: pre-wrap;"}).text
        fujian = str(fujian).strip()
        info = str(fujian.replace('\n', '#'))

        pattern = re.compile(r'资源分类\t(.*?)#', re.S)
        lingyu = str(re.findall(pattern, info)[0])

        # print(name, lingyu, info)
        logger.info('已保存数据成功')
        # 在各分页面之中点击数据信息，获取附加信息，如果没有附件信息即跳过（基本所有的可下载的数据均有数据信息），同时打印出来进行检查，
        # 其中利用.strip()进行换行符的替换
        try:
            f.write(name)
            f.write(',')
            f.write(lingyu)
            f.write(',')
            f.write(info)
            f.write('\n')

        except:
            continue
        # 将附件的数据信息写入txt，按行存储

    except:
        continue

driver.close()  # 关闭页面
