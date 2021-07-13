from selenium import webdriver
import re
from bs4 import BeautifulSoup
import time
import json
import os
# 导入库，其中selenium用于模拟浏览器操作，bs4用于解析页面，time库用于计算时间，保证页面的更新时间


from util.TNlogger import TNLog

logger = TNLog(name='天津')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/70.0.3538.110 Safari/537.36'}


# 传入headers
def newest_filename(path_file):
    '''
    给定文件目录，返回最新下载的文件信息
    Args:
        path_file:文件目录

    Returns: File_Path

    '''
    lists = os.listdir(path_file)
    lists.sort(key=lambda fn: os.path.getmtime(path_file + '\\' + fn))

    return lists[-1]


def getDonwLoadFileName(download_path, filaname, timing):
    '''
    用于检查文件是否下载完成，当下载完成时会从这个函数跳出

    :param download_path: chromeDiver默认下载文件的位置
    :param row: 字典形式，由页面解析生成的，负责提供下载的文件名称信息
    :return:
    '''

    # document_name_zip = row['文件名称']+'.zip'
    # document_name_rar = row['文件名称']+'.rar'
    # check_down_load_path_zip = os.path.join(download_path,document_name_zip)
    # check_down_load_path_rar = os.path.join(download_path, document_name_rar)
    time_hold = 0
    while True:

        try:
            newest_file = newest_filename(download_path)
            finished_time = os.path.getatime(os.path.join(download_path, newest_file))
        except:
            newest_file = ''
            finished_time = 0
        if timing <= finished_time and 'download' not in newest_file and '.tmp' not in newest_file:
            time.sleep(1)
            return newest_file
        time.sleep(1)
        time_hold += 1
        if time_hold >= 50:
            a = input('好像号断了或者什么的')
            if a == 'quit':
                return a
    # time.sleep(0.5)
    # return  document_name


download_dir = r'C:\Users\GYHfresh\Downloads'


def tianjin(path):
    for year in range(2015, 2021):
        logger.info('现在爬取的是天津第' + str(year) + '年的统计年鉴')
        # 领域/不限

        url = 'http://stats.tj.gov.cn/nianjian/{}nj/zk/indexce.htm'.format(year)

        driver = webdriver.Chrome()
        time.sleep(1)
        driver.get(url)
        driver.switch_to.frame(1)
        time.sleep(1)
        html = driver.page_source
        # print(html)

        soup = BeautifulSoup(html, 'html.parser')
        # print(soup)
        topic_list = soup.find_all('li', attrs={'id': 'foldheader'})
        # click_button = driver.find_element_by_xpath("//*[text()='{}']".format('第二部分 统计资料'))
        # click_button.click()

        for topic in topic_list[1:]:
            topic_str = ''.join(topic.text)
            file_list = topic.find_next_sibling('ul', attrs={'id': 'foldinglist'}).find_all('li')
            # except:
            #     continue
            previous_file_name = ''
            for file in file_list:
                try:
                    file.a.get('href')
                except:
                    continue
                if 'xls' in file.a.get('href'):
                    file_json = {}
                    file_json['topic'] = topic_str
                    file_json['info'] = {}

                    click_name = file.text
                    raw_file_name = click_name.split()[0]
                    cur_file_name = click_name.split()[-1]

                    if '续表' in cur_file_name:
                        cur_file_name = previous_file_name + '_' + cur_file_name.replace('续表', '')
                    else:
                        previous_file_name = cur_file_name
                    cur_file_name = str(year) + '_' + cur_file_name
                    cur_time = time.time()

                    click_button = driver.find_element_by_xpath("//*[text()='{}']".format(click_name))
                    click_button.click()
                    latestDownloadedFileName = getDonwLoadFileName(download_dir, raw_file_name, cur_time)

                    path = os.path.join(download_dir, latestDownloadedFileName)

                    if os.path.exists(path):
                        pass
                    else:
                        # print(path)
                        logger.error('文件不存在')

                    pre_name, format_name = latestDownloadedFileName.split('.')
                    # new_name = cur_file_name + '.' + format_name
                    newpath = os.path.join(download_dir, cur_file_name + '.' + format_name)
                    # try:
                    time.sleep(1)
                    try:
                        os.rename(path, newpath)
                    except:
                        continue
                    if os.path.exists(newpath) and not os.path.exists(path):
                        logger.info('已保存' + str(newpath))

                    else:
                        logger.error('无法找到' + str(newpath))
                        continue

                    file_json['name'] = cur_file_name
                    file_json['topic'] = topic_str
                    file_json['info'] = str(year)

                    with open(path, "a+", encoding='utf-8') as f:
                        json.dump(file_json, f, indent=2, ensure_ascii=False)

                    del cur_file_name


if __name__ == '__main__':
    path = os.path.dirname(__file__) + '/../info/天津年鉴.json'

    tianjin(path)
