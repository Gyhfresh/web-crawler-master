# -*- coding: utf-8 -*-
# @File : test.py

from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
import os.path as osp
# import rarfile
import json
import os
import glob
import zipfile
import shutil
from util.utilis import *
from util.logger import Logger

info_log = Logger('../log/sichuana_info.log','info')
error_log = Logger('../log/sichuan_error.log','info')
info_log.logger.info('开始爬取数据了')
error_log.logger.error('请检查网络设置，目前断线')
Flag = True
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/70.0.3538.110 Safari/537.36'}
base_url = 'http://www.scdata.net.cn/odweb/catalog/'
url = 'http://www.scdata.net.cn/odweb/catalog/index.htm'
download_dir = os.path.abspath('./download')
saved_data_dir = os.path.abspath('./saved_data')

if os.path.exists('sichuan_V2.json'):
    json_list = read_json('sichuan_V2.json')
else:
    json_list = []
if os.path.exists('url.json'):
    readed_url_list = read_json('url.json')
else:
    readed_url_list = []

#1. 设置dirver参数
options = webdriver.ChromeOptions()
prefs = {'download.default_directory': download_dir}
options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(chrome_options=options)
driver.get(url)
info_log.logger.info('请登录账号后，按任意键继续爬虫')
login = input('')
def getDonwLoadFileName(download_path, row,timing):
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
        #     document_name = document_name_zip
        #     break
        # if os.path.exists(check_down_load_path_rar):
        #     document_name = document_name_rar
        #     break
        try:
            newest_file = newest_filename(download_path)
            finished_time = os.path.getatime(os.path.join(download_path, newest_file))
        except:
            newest_file = ''
            finished_time = 0
        if  timing <= finished_time and row['文件名称'] in newest_file and 'download' not in newest_file and '.tmp' not in newest_file:
            time.sleep(0.5)
            return newest_file
        time.sleep(1)
        time_hold += 1
        if time_hold >= 50:
            error_log.logger.error('如果文件没下载完，按任意键继续；如果网络问题，请输入 quit 退出')
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


def down_load_parser(html_download):
    '''
    用于解析下载页面的信息
    :param html_download: 下载页面的html
    :return: down_list->list:[row_dict,row_dict...] 包含每条数据文件的信息
    '''
    down_list = []
    soup_down = BeautifulSoup(html_download, 'html.parser')
    table = soup_down.find('table', attrs={'id': 'catalog-download_file'})
    tr_list = table.find('tbody').find_all('tr')
    for i in tr_list:
        row_table = i.find_all('td')
        try:
            row_dict = {
                '下载格式': row_table[1].text,
                '文件名称': row_table[2].text,
                '大小': row_table[3].text,
                '时间': row_table[4].text,

            }
            # down_list.append(row_dict)
        except:
            row_dict = {
                '下载格式': '',
                '文件名称': '',
                '大小': '',
                '时间': '',

            }
        down_list.append(row_dict)
    return down_list


def parser_base_info(page_html):
    '''
    用于爬取基础信息页面
    :param page_html: 基础信息页面的html
    :return: info_dict -> {key1: value1,....}
    '''
    info_dict = {}
    soup_son = BeautifulSoup(page_html, 'html.parser')
    table = soup_son.find('table')
    tr_list = table.find_all('tr')
    for tr in tr_list:
        td_list = tr.find_all('td')
        row_num = len(td_list)
        for i in range(int(row_num / 2)):
            info_dict[td_list[2 * i].text] = td_list[2 * i + 1].text
    return info_dict

def read_json(json_fn):
    with open(json_fn, "r",encoding='utf-8') as f:
        json_dict = json.load(f)
    return json_dict
def Write_json_bc(data,josin_fn):
    with open(josin_fn, "w",encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False,indent=4)

def unrar_file(dir_path,temp_saved_path):
    '''
    解压rar的代码，需要配下载unrar，要去csdn里面找哦
    :param dir_path: 原压缩文件
    :param temp_saved_path: 解压后的目录：这里面只是做中间暂存目录，要把这里面的文件改名字
    :return:
    '''
    rf = rarfile.RarFile(dir_path)
    rf.extractall(temp_saved_path)



def unzip_file(dir_path,temp_saved_path):
    '''

    :param dir_path: 原压缩文件
    :param temp_saved_path: 解压后的目录：这里面只是做中间暂存目录，要把这里面的文件改名字
    :return:
    '''
    # 解压缩后文件的存放路径
    # 找到压缩文件夹
    dir_list = glob.glob(dir_path)
    if dir_list:
        # 循环zip文件夹
        for dir_zip in dir_list:
            # 以读的方式打开
            with zipfile.ZipFile(dir_zip, 'r') as f:
                for file in f.namelist():
                    f.extract(file, path=temp_saved_path)
def return_all_file_path(parrent_path,file_path_list):
    '''
    搜索一个文件夹下的所有文件，调用时file_path_list为空
    :param parrent_path: 母目录
    :param file_path_list: 递归调用时用的，函数初始输入为空表[]
    :return: List:[] ,元素为所有文件的绝对路径
    '''
    son_file_path_list = os.listdir(parrent_path)
    for file_name in son_file_path_list:
        file = os.path.join(parrent_path,file_name)
        if  os.path.isdir(file):
            file_path_list = return_all_file_path(file, file_path_list)
        else:
            file_path_list.append(file)

    return file_path_list

def process_download_data(download_dir, saved_data_dir,latestDownloadedFileName,row_dict):
    '''
    这个主要是将下载好的文件进行解压，解压到中间暂存目录后，再将文件重命名然后移植
    :param download_dir: 下载获得的zip目录
    :param saved_data_dir: 保存的目录
    :param latestDownloadedFileName: 下载的zip文件名，如"重庆2021人口局数据.zip"
    :param row_dict: 主要是重命名时需要row_dict['info']['time']对文件进行命名
    :return: list:[] 元素为每个文件的json字典
    '''
    raw_path = os.path.join(download_dir, latestDownloadedFileName)
    info_log.logger.info(raw_path)
    if os.path.exists(raw_path):
        info_log.logger.info('ok')
    else:
        raise ValueError('这文件都不存在啊')
    pre_name, format_name = latestDownloadedFileName.split('.')

    temp_file_name = pre_name + '_' + row_dict['info']['时间'].split(' ')[0]
    temp_file_dir = os.path.join(download_dir, temp_file_name)###压缩后文件存在地址
    if format_name == 'zip':
        unzip_file(raw_path, temp_file_dir)#将raw_path的压缩文件，解压到temp_file_dir
    elif format_name == 'rar':
        try:
            unrar_file(raw_path, temp_file_dir)
        except:
            error_log.logger.error('unrar的环境没配好，请配好unrar的环境')
            return []
    else:
        os.mkdir(temp_file_dir)
        shutil.move(raw_path,temp_file_dir)
    list_of_file_dict = move_temp_file(temp_file_dir,saved_data_dir,row_dict,temp_file_name)
    return list_of_file_dict

import copy
def move_temp_file(temp_saved_path,target_saved_data_dir,file_dict,temp_file_name):
    '''

    :param temp_saved_path:  压缩包解压后的地址
    :param target_saved_data_dir：保存文件的最终地址
    :param file_dict: 压缩文件的字典，主要是生成每个压缩文件的字典，用于json存储
    :param temp_file_name: 原压缩文件的文件名，无后缀“重庆2021人口局数据_2001"
    :return:list:[] 元素为每个文件的json字典
    '''
    file_dict_list = []
    file_path_list = return_all_file_path(temp_saved_path,[])
    for idx,files in enumerate(file_path_list):
        format = files.split('.')[-1]
        new_file_dict = copy.deepcopy(file_dict)
        new_name = temp_file_name + '_' + str(idx)
        new_file_dict['name'] = new_name
        path_name = new_name + '.'+format
        taget_file_path = os.path.join(target_saved_data_dir,path_name)
        shutil.move(files,taget_file_path)


        Flag = 1
        time_hold = 0
        while Flag == 1:
            if os.path.exists(taget_file_path):
                break
            else:
                time.sleep(1)
                time_hold +=1
            if time_hold >=10:
                Flag = 0
                error_log.logger.error('shutle出错了，没找到目标文件')
        if Flag == 1:
            file_dict_list.append(new_file_dict)

    return  file_dict_list





def main(driver):
    '''
    主函数
    '''



    try:
        html = driver.page_source
        driver.find_element_by_xpath("//*[text()='更新时间']").click()
    except:
        error_log.logger.error('检查网络情况')
        raise ValueError('检查网络情况')
    #########################################################################################
    soup = BeautifulSoup(html, 'html.parser')
    page_num = int(soup.find_all('a', attrs={'style': 'cursor:pointer'})[-2].text)
    log_list = []
    for page_count in range(page_num - 1):  # 每一页的循环
        # 每一次翻页都要重新获取html

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        ul_temp = soup.find_all('ul', id='catalog-list')  # 寻找点击列表
        li_list = ul_temp[0].find_all('li')  ##寻找点击列表

        for i in li_list:
            ################################载入一个子页面的title信息
            left_div = i.find('div', attrs={'class': 'item-left'})
            right_div = i.find('div', attrs={'class': 'item-right'})
            count_div = i.find('div', attrs={'class': 'item-count'})
            topic = right_div.find('div', attrs={'class': 'item-tag'}).find_all('span')[-1].text  # '生活服务'
            info = left_div.find('div', attrs={'class': 'item-info'}).text  # '2020年度易地扶贫搬迁先进个人包含姓名、单位等字段内容。'
            title = left_div.find('a').text  # '达州市易地扶贫搬迁先进个人'
            date_time = i.find('div', attrs={'class': 'item-datetime'}).text.split('：')[-1]  # '2021-06-15 19:45:41'
            # time.sleep(1)
            data_info = {}
            ############################
            ###这里还是要解析一下基本信息的名称
            # data_info['title'] = title  #边策7.5删除
            # data_info['latest_time'] = date_time   #边策7.5删除
            # data_info['简介'] = info       #   边策7.5删除
            data_info['topic'] = topic
            # data_info['saved_data'] = []  #边策7.5删除
            #################################################跳转新页面
            # time.sleep(1)
            new_page_url = base_url + left_div.a.get('href')
            if new_page_url in readed_url_list:
                continue

            readed_url_list.append(new_page_url)
            Write_json_bc(readed_url_list,'url.json')
            try:
                driver.execute_script("window.open('{}')".format(new_page_url))
                driver.switch_to.window(driver.window_handles[-1])
            except:
                error_log.logger.error('网页打开失败了')

        # if os.path.exists(check_down_load_path_zip):driver.switch_to.window(driver.window_handles[0])
            # try:
            #     driver.find_element_by_link_text(left_div.a.text).click()
            # except:
            #     time.sleep(5)
            #     driver.find_element_by_link_text(left_div.a.text).click()
            # time.sleep(1)#这里暂停一秒钟
            #########################################################################################
            ##进入子页面后
            ###########################################################
            # 这里获得基本信息,返回字典
            son_page_html = driver.page_source
            base_info = parser_base_info(son_page_html)

            data_info['info'] = base_info

            data_info['info']['title'] = title
            data_info['info']['简介'] = info
            data_info['info']['latest_time'] = date_time

            # data_root = osp.join(saved_data_dir, data_info['title'])
            # mkdir_ifmiss(data_root)
            ###########################################################
            try:
                driver.find_element_by_xpath("//*[text()='数据下载']").click()
            except:
                error_log.logger.error('下载失败了')
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                continue
            ##进入下载页面后

            ###################################

            # 这里要解析数据下载页面得到格式，如，下载格式，文件名称，大小，时间等
            html_download = driver.page_source
            download_list = down_load_parser(html_download)
            xiazai_list = driver.find_elements_by_xpath("//*[text()='下载']")
            ####################################
            for (row_dict, download_pattern) in zip(download_list, xiazai_list):
                # 根据页面进行下载
                down_count = 0
                a = ''
                cur_time = time.time()
                while True:
                    try:
                        download_pattern.click()
                        break
                    except Exception as e:
                        error_log.logger.error(e)
                        down_count += 1
                    if down_count >= 10:
                        a = input()
                        break
                if a == 'ok':
                    continue
                latestDownloadedFileName = getDonwLoadFileName(download_dir,
                                                               row_dict,cur_time)  # waiting 3 minutes to complete the download

                if latestDownloadedFileName == 'quit':
                    continue
                data_info['info'].update(row_dict)
                file_dict_list = process_download_data(download_dir, saved_data_dir, latestDownloadedFileName, data_info)
                json_list.extend(file_dict_list)
                # time.sleep(1)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            Write_json_bc(json_list, '../info/sichuan_V2.json')
            log_list.append(data_info)

        driver.find_element_by_xpath("//*[text()='下一页']").click()
    global Flag
    Flag = False
    # method to get the downloaded file name
if __name__ =='__main__':

    while Flag:
        try:
            main(driver)
        except:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(10)
