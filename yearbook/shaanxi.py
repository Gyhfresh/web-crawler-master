# -*- coding: utf-8 -*- 


import time
from util.utilis import *
from util.logger import Logger
import os
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
from util.utilis import *
import os.path as osp

info_log = Logger('../log/guizhou_info.log','info')
error_log = Logger('../log/guizhou_error.log','info')
info_log.logger.info('开始爬取数据了')
error_log.logger.error('请检查网络设置，目前断线')
from bs4 import BeautifulSoup
year_list = sorted(list(range(2010,2020,1)),reverse =True)
download_dir = os.path.abspath('./data')
options = webdriver.ChromeOptions()
prefs = { 'download.default_directory': download_dir}
options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(chrome_options=options)

def write_json(json_fn, json_dict):
    if not os.path.exists(json_fn):
        write_list = [json_dict]
    else:
        write_list = read_json(json_fn)
        write_list.append(json_dict)
    with open(json_fn, "w",encoding='utf-8') as f:
        json.dump(write_list, f, ensure_ascii=False,indent=4)
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
        # if os.path.exists(check_down_load_path_zip):
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
        if timing <= finished_time and 'download' not in newest_file and '.tmp' not in newest_file :
            time.sleep(1)
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




def main():

    if os.path.exists('shanxi.json'):
        json_list = read_json('shanxi.json')
    else:
        json_list = []
    url_list = [
        'http://tjj.shaanxi.gov.cn/upload/n2020/indexce.htm',
                'http://tjj.shaanxi.gov.cn/upload/2020/pro/3sxtjnj/zk/indexce.htm',
                'http://tjj.shaanxi.gov.cn/upload/201802/zk/indexce.htm','http://tjj.shaanxi.gov.cn/upload/2018/7/zk/indexce.htm',
                'http://tjj.shaanxi.gov.cn/upload/2016/tongjinianj2016/2016/indexce.htm','http://tjj.shaanxi.gov.cn/upload/2016/tongjinianj/2015/indexce.htm',
                'http://tjj.shaanxi.gov.cn/upload/2014/indexce.htm','http://tjj.shaanxi.gov.cn/upload/2013/indexce.htm',
                'http://tjj.shaanxi.gov.cn/upload/2012/indexce.htm','http://tjj.shaanxi.gov.cn/upload/2011/indexce.htm',
                'http://tjj.shaanxi.gov.cn/upload/2010/indexce.htm'
                ]
    for year,base_url in zip(year_list,url_list):

        # base_url = 'http://tjj.shaanxi.gov.cn/upload/{}/zk/indexce.htm'.format(2018)
        driver.get(base_url)
        driver.switch_to.frame(1)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        # download_list = driver.find_elements_by_xpath("//table[@id='fileListTable']//a")
        ####整个目录
        topic_list = soup.find_all('li',attrs = {'id':'foldheader'})


        for topic in topic_list:
            if topic.text == '统计图' or topic.text == '附录':
                continue
            topic_str = ''.join(topic.text.split('、')[-1].split())
            try:
                file_list = topic.find_parent().find_next_sibling('ul',attrs = {'id':'foldinglist'}).find_all('li')
            except:
                file_list = topic.find_next_sibling('ul',attrs = {'id':'foldinglist'}).find_all('li')
            tongming_num = 1
            previous_file_name = ''
            for file in file_list:
                if 'xls' in file.a.get('href') or 'xlrx' in file.a.get('href'):
                    file_json = {}
                    file_json['topic'] = topic_str
                    file_json['info'] = {}

                    click_name = file.text
                    if len(click_name.split())>1:
                        raw_file_name = click_name.split()[0]
                        cur_file_name = ' '.join(click_name.split()[1:])
                    else:
                        raw_file_name = click_name.split()[0]
                        cur_file_name = click_name.split()[-1]

                    if '续表' in cur_file_name:
                        cur_file_name = previous_file_name +'_'+ cur_file_name.replace('续表','')
                    elif previous_file_name == cur_file_name:
                        cur_file_name = cur_file_name + '_' + str(tongming_num)
                        tongming_num += 1
                    else:
                        previous_file_name = cur_file_name
                        tongming_num = 1
                    cur_file_name = str(year)+ '_' + cur_file_name
                    cur_time = time.time()
                    click_button = driver.find_element_by_xpath("//*[text()='{}']".format(click_name))
                    click_button.click()
                    latestDownloadedFileName = getDonwLoadFileName(download_dir, raw_file_name, cur_time)

                    if latestDownloadedFileName == 'quit':
                        continue

                    path = osp.join(download_dir, latestDownloadedFileName)

                    if osp.exists(path):
                       pass
                    else:
                        info_log.logger('不存在这个文件：'+path)
                        continue
                        # raise ValueError('这文件都不存在啊')

                    pre_name, format_name = latestDownloadedFileName.split('.')
                    # new_name = cur_file_name + '.' + format_name
                    newpath = osp.join(download_dir, cur_file_name + '.' + format_name)
                    # try:
                    time.sleep(1)
                    if osp.exists(newpath):
                        info_log.logger.info('已经保存过这个文件了，不保存了哦！')
                        continue
                    os.rename(path, newpath)
                    if osp.exists(newpath) and not osp.exists(path):
                        info_log.logger.info('已保存:'+newpath)
                    else:
                        error_log.logger.error('！！！！！！！！！！！！！！！！！没找到:'+ newpath)
                        error_time = 0
                        while(True):
                            time.sleep(1)
                            error_time +=1
                            if not osp.exists(path):
                                break
                            if error_time >=50:
                                error_log.logger.error('真的rename不到文件诶')
                                continue


                        # time.sleep(5)
                        # os.rename(path, newpath)
                        # raise ValueError('这文件都不存在啊')
                    # except:
                    #     time.sleep(2)
                    #     os.rename(path, newpath)
                    file_json['name'] = cur_file_name
                    json_list.append(file_json)
                    with open('../info/shanxi.json', "w", encoding='utf-8') as f:
                        json.dump(json_list, f, ensure_ascii=False, indent=4)

                    del cur_file_name

if __name__ == '__main__':
    main()
