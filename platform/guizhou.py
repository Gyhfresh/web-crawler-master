# -*- coding: utf-8 -*-
# @File : guizhou.py
import sys
# sys.path.append('.')
# sys.path.append('../')
# sys.path.append('../../')
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
import os
import os.path as osp
import time
from util.utilis import *


url = 'http://data.guizhou.gov.cn/data-catalog'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/70.0.3538.110 Safari/537.36'}
import pandas as pd
import time
from util.utilis import *
from util.logger import Logger
info_log = Logger('../log/guizhou_info.log','info')
error_log = Logger('../log/guizhou_error.log','info')

info_log.logger.info('开始爬取数据了')
error_log.logger.error('请检查网络设置，目前断线')
Flag = True

dataframe = pd.read_excel('./贵阳市政府数据资源目录信息.xlsx')
search_url = 'https://data.guiyang.gov.cn/city/datadetail.htm?resId='
data_root = os.path.abspath('./data')
download_dir = os.path.abspath('./Downloads')
if not os.path.exists(download_dir):
    os.mkdir(download_dir)
options = webdriver.ChromeOptions()
prefs = {'download.default_directory': download_dir}
options.add_experimental_option('prefs', prefs)

web_sites_base_url = 'https://data.guiyang.gov.cn/city/index.htm'
driver = webdriver.Chrome()
driver.get(web_sites_base_url)
info_log.logger.info('请登录账号后，按任意键继续爬虫')
login = input('')


if not os.path.exists(data_root):
    os.mkdir(data_root)
def getDonwLoadFileName(download_path, filaname,timing):
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
        # if os.path.exists(check_down_load_path_zip):
        #     document_name = document_name_zip
        #     break
        # if os.path.exists(check_down_load_path_rar):
        #     document_name = document_name_rar
        #     break
        try:
            newest_file = newest_filename(download_path)
            finished_time = os.path.getatime(os.path.join(download_path,newest_file))
        except:
            newest_file = ''
            finished_time = 0
        if timing <= finished_time and 'download' not in newest_file and '.tmp' not in newest_file:
            time.sleep(0.5)
            return newest_file
        time.sleep(1)
        time_hold += 1
        if time_hold >= 100:

            error_log.logger.error('下载失败，请查询网络问题，输入 quit 跳转至下一个文件的下载')
            a = input()
            if a == 'quit':
                return a
    # time.sleep(0.5)
    # return  document_name


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




def main():
    if os.path.exists('../guizhou/log.txt'):
        log_list = read_json('log.txt')
    else:
        log_list = []

    for idx,series in dataframe.iterrows():
        # print(series)
        if series['标识符'].strip() in log_list:
            continue
        else:
            log_list.append(series['标识符'].strip())
            with open('../guizhou/log.txt', "w", encoding='utf-8') as f:
                json.dump(log_list, f, ensure_ascii=False, indent=4)
        try:
            cur_url = search_url+series['标识符'].strip()
        except:
            error_log.logger.error('这条检查不到')
            continue
        try:
            driver.get(cur_url)
        except:
            error_log.logger.error('这个网站好像卡了，打不开了:{}'.format(cur_url))
            continue

        download_list = driver.find_elements_by_xpath("//table[@id='fileListTable']//a")
        Drag = driver.find_element_by_class_name("nicescroll-cursors")
        for count,download_button in enumerate(download_list):
            data_info = dict(series)
            # raw_filename = download_button.text.split('.')[0]
            cur_time = time.time()
            try:
                download_button.click()
            except:
                print(cur_url)
                print(download_button.text)
                error_log.logger.error('因为他网页的原因，这个下载连接点不到了:1.如果有数据下载一栏，点击数据下载一栏,2.如果是滑窗，往下拉一拉')
                a = input('处理好后，按任意键继续')
                try:
                    download_button.click()
                except:
                    continue
            # driver.execute_script("arguments[0].scrollIntoView();", download_button)
            try:

                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(driver).drag_and_drop_by_offset(Drag, 0, 24).perform()
            except:
                pass

            cur_file_dict = {}

            latestDownloadedFileName = getDonwLoadFileName(download_dir,
                                                           'raw_filename',cur_time)  # waiting 3 minutes to complete the download
            if latestDownloadedFileName == 'quit':
                continue
            path = osp.join(download_dir, latestDownloadedFileName)
            if osp.exists(path):
                info_log.logger.info('已保存：{}'.format(path))
            else:
                error_log.logger.info('找不到文件:{}'.format(path))
                continue
            pre_name, format_name = latestDownloadedFileName.split('.')
            new_name = series['资源名称'].strip() + '_' + str(count) + '.' + format_name
            newpath = osp.join(data_root, new_name)
            data_info['格式'] = format_name
            try:
                move(path, newpath)
            except:
                time.sleep(2)
                move(path, newpath)

            cur_file_dict['name'] = series['资源名称'].strip() + '_' + str(count)
            cur_file_dict['topic'] = series['数据领域'].strip()
            cur_file_dict['info'] = data_info
            try:
                if not osp.exists(newpath):
                    raise ValueError('新目录下没有文件')
            except:
                continue
            write_json('../info/贵阳.json', cur_file_dict)
    global Flag
    Flag = False
if __name__ == '__main__':
    while Flag:
        try:
            main()
        except:
            error_log.logger.error('停止30s继续爬虫')
            time.sleep(30)

