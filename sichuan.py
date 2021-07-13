# -*- coding: utf-8 -*-



import json
import pickle
import os
import os.path as osp
import shutil
import time
from bs4 import BeautifulSoup
from selenium import webdriver

import pdb

def move(souce,target):
    '''

    Args:
        souce:
        target:

    Returns:

    '''
    shutil.move(souce, target)

def mkdir_ifmiss(directory):
    '''

    Args:
        directory:

    Returns:

    '''
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_folder_list(checked_directory, log_fn):
    '''

    Args:
        checked_directory:
        log_fn:

    Returns:

    '''
    checked_list = os.listdir(checked_directory)
    with open(log_fn, "w") as f:
        for item in checked_list:
            f.write(item + "\n")


def strcal(shotid, num):
    '''

    Args:
        shotid:
        num:

    Returns:

    '''
    return str(int(shotid) + num).zfill(4)


def read_json(json_fn):
    '''

    Args:
        json_fn:

    Returns:

    '''
    with open(json_fn, "r") as f:
        json_dict = json.load(f)
    return json_dict


def write_json(json_fn, json_dict):
    '''

    Args:
        json_fn:
        json_dict:

    Returns:

    '''
    with open(json_fn, "a+",encoding='utf-8') as f:
        json.dump(json_dict, f, ensure_ascii=False,indent=4)


def read_pkl(pkl_fn):
    '''

    Args:
        pkl_fn:

    Returns:

    '''
    with open(pkl_fn, "rb") as f:
        pkl_contents = pickle.load(f)
    return pkl_contents


def write_pkl(pkl_fn, pkl):
    '''

    Args:
        pkl_fn:
        pkl:

    Returns:

    '''
    with open(pkl_fn, "wb") as f:
        pickle.dump(pkl, f)


def read_txt_list(txt_fn):
    '''

    Args:
        txt_fn:

    Returns:

    '''
    with open(txt_fn, "r") as f:
        txt_list = f.read().splitlines()
    return txt_list


def write_txt_list(txt_fn, txt_list):
    '''

    Args:
        txt_fn:
        txt_list:

    Returns:

    '''
    with open(txt_fn, "w") as f:
        for item in txt_list:
            f.write("{}\n".format(item))



def getDonwLoadFileName(download_path, row):
    '''
        Args:
        download_path:chromeDiver默认下载文件的位置
        row:字典形式，由页面解析生成的，负责提供下载的文件名称信息

    Returns:
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
        except:
            newest_file = ''
        if row['文件名称'] in newest_file and 'download' not in newest_file:
            time.sleep(0.5)
            return newest_file
        time.sleep(1)
        time_hold += 1
        if time_hold >= 50:
            a = input('好像号断了或者什么的')
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


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/70.0.3538.110 Safari/537.36'}
base_url = 'http://www.scdata.net.cn/odweb/catalog/'
url = 'http://www.scdata.net.cn/odweb/catalog/index.htm'
download_dir = r'C:\Users\边策\Downloads'
saved_data_dir = './data'

def main():
    '''
    主函数
    '''
    driver = webdriver.Chrome()
    driver.get(url)
    login = input('按任意键继续')
    html = driver.page_source
    driver.find_element_by_xpath("//*[text()='更新时间']").click()

    soup = BeautifulSoup(html, 'html.parser')
    page_num = int(soup.find_all('a', attrs={'style': 'cursor:pointer'})[-2].text)
    log_list = []
    for page_count in range(page_num - 1):  # 每一页的循环
        # 每一次翻页都要重新获取html

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        ul_temp = soup.find_all('ul', id='catalog-list')  # 寻找点击列表
        li_list = ul_temp[0].find_all('li')  ##寻找点击列表
        print('长度：', len(li_list))
        for i in li_list:
            #载入一个子页面的title信息
            left_div = i.find('div', attrs={'class': 'item-left'})
            right_div = i.find('div', attrs={'class': 'item-right'})
            count_div = i.find('div', attrs={'class': 'item-count'})
            topic = right_div.find('div', attrs={'class': 'item-tag'}).find_all('span')[-1].text  # '生活服务'
            info = left_div.find('div', attrs={'class': 'item-info'}).text  # '2020年度易地扶贫搬迁先进个人包含姓名、单位等字段内容。'
            title = left_div.find('a').text  # '达州市易地扶贫搬迁先进个人'
            date_time = i.find('div', attrs={'class': 'item-datetime'}).text.split('：')[-1]  # '2021-06-15 19:45:41'
            # time.sleep(1)
            data_info = {}

            #这里还是要解析一下基本信息的名称
            data_info['title'] = title
            data_info['latest_time'] = date_time
            data_info['简介'] = info
            data_info['topic'] = topic
            data_info['saved_data'] = []
            #跳转新页面
            # time.sleep(1)
            new_page_url = base_url + left_div.a.get('href')
            driver.execute_script("window.open('{}')".format(new_page_url))
            driver.switch_to.window(driver.window_handles[-1])
            # try:
            #     driver.find_element_by_link_text(left_div.a.text).click()
            # except:
            #     time.sleep(5)
            #     driver.find_element_by_link_text(left_div.a.text).click()
            # time.sleep(1)#这里暂停一秒钟

            #进入子页面后

            # 这里获得基本信息,返回字典
            son_page_html = driver.page_source
            base_info = parser_base_info(son_page_html)
            data_info['info'] = base_info
            data_root = osp.join(saved_data_dir, data_info['title'])
            mkdir_ifmiss(data_root)

            try:
                driver.find_element_by_xpath("//*[text()='数据下载']").click()
            except:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                continue
            #进入下载页面后



            # 这里要解析数据下载页面得到格式，如，下载格式，文件名称，大小，时间等
            html_download = driver.page_source
            download_list = down_load_parser(html_download)
            xiazai_list = driver.find_elements_by_xpath("//*[text()='下载']")

            for (row_dict, download_pattern) in zip(download_list, xiazai_list):
                # 根据页面进行下载
                down_count = 0
                a = ''
                while True:
                    try:
                        download_pattern.click()
                        break
                    except Exception as e:
                        print(e)
                        down_count += 1
                    if down_count >= 10:
                        a = input()
                        break
                if a == 'ok':
                    continue
                latestDownloadedFileName = getDonwLoadFileName(download_dir,
                                                               row_dict)  # waiting 3 minutes to complete the download
                path = osp.join(download_dir, latestDownloadedFileName)
                if osp.exists(path):
                    print('ok')
                else:
                    raise ValueError('这文件都不存在啊')
                pre_name, format_name = latestDownloadedFileName.split('.')
                new_name = pre_name + '_' + row_dict['时间'].split(' ')[0] + '.' + format_name
                newpath = osp.join(data_root, new_name)
                move(path, newpath)
                # time.sleep(1)

                row_dict['保存地址'] = newpath
                data_info['saved_data'].append(row_dict)
                print('已保存', newpath)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            write_json('四川.json', data_info)
            log_list.append(data_info)

        driver.find_element_by_xpath("//*[text()='下一页']").click()

    # method to get the downloaded file name
if __name__ =='__main__':
    main()
