# -*- coding:utf-8 -*-
import shutil
import re
import pandas as pd
import os
from util.utilis import *
from util.logger import Logger

info_log = Logger('../log/yunnan_info.log','info')
error_log = Logger('../log/yunnan_error.log','info')
info_log.logger.info('开始爬取数据了')
error_log.logger.error('请检查网络设置，目前断线')
dir_list = list(range(2013, 2021))
base_root = os.path.abspath('./')

if not os.path.exists(base_root+'2021'):
    error_log.logger.error('请到云南官网将统计文献进行下载，并解压，按年份命名')
    raise IOError('请到云南官网将统计文献进行下载，并解压，按年份命名')
save_root = os.path.abspath('./yunnan')

#对于有目录txt的文件：

def return_all_file_path(parrent_path,file_path_list):
    '''
    搜索一个文件夹下的所有文件，调用时file_path_list为空
    :param parrent_path: 母目录
    :param file_path_list: 递归调用时用的，函数初始输入为空表[]
    :return: List:[] ,元素为所有文件的绝对路径
    '''
    son_file_path_list = os.listdir(parrent_path)
    son_file_path_list.sort()
    for file_name in son_file_path_list:
        file = os.path.join(parrent_path,file_name)
        if  os.path.isdir(file):
            file_path_list = return_all_file_path(file, file_path_list)
        else:
            file_path_list.append(file)

    return file_path_list
def main():
    all_list = []
    for year in dir_list:
        year_file_dict = {}
        year_dir = os.path.join(base_root, str(year))
        if not os.path.exists(year_dir):
            error_log.logger.error('未找到文件')
        all_file_list = return_all_file_path(parrent_path=year_dir, file_path_list=[])
        for file in all_file_list:
            if 'xls' in file.lower() or 'xlsx' in file.lower():
                try:
                    df_data = pd.read_excel(file, header=None)
                    file_name = df_data.iloc[0, 0].strip()
                except:
                    continue
                if re.search('(^\d+-\d+)\s?([\u002d\u4e00-\u9fa5、\s\w]+(（.*）|\(.*\))?)', file_name):
                    abcd = re.search('(^\d+-\d+)\s?([\u002d\u4e00-\u9fa5、\s\w]+(（.*）|\(.*\))?)', file_name)
                    section = ''.join(abcd.group(1).split())
                    name = ''.join(abcd.group(2).split())
                    jieshu_list = year_file_dict.setdefault(section, [])
                    year_file_dict[section].append(name)
        #                 print(section,name)
        real_file_dict = {}
        time_file_dict = {}
        for keys, values in year_file_dict.items():
            real_file_dict[keys] = [i for i in values if '续表' not in i and 'continued' not in i]
            time_file_dict[keys] = 0
        for file in all_file_list:
            if 'xls' in file.lower() or 'xlsx' in file.lower():
                try:
                    df_data = pd.read_excel(file, header=None)
                    file_name = df_data.iloc[0, 0].strip()
                except:
                    continue
                if re.search('(^\d+-\d+)\s?([\u002d\u4e00-\u9fa5、\s\w]+(（.*）|\(.*\))?)', file_name):
                    abcd = re.search('(^\d+-\d+)\s?([\u002d\u4e00-\u9fa5、\s\w]+(（.*）|\(.*\))?)', file_name)
                    section = ''.join(abcd.group(1).split())
                    name = ''.join(abcd.group(2).split())
                    times = str(time_file_dict[section])
                    #             print(file.split('.')[-1])

                    time_file_dict[section] += 1
                    #                 print(section)
                    #                 print(file)
                    #                 print(year_file_dict[section])
                    #                 print(real_file_dict[section])
                    try:
                        real_name = real_file_dict[section][-1]
                    except:
                        continue
                    new_name = str(year) + '_' + real_name + '_' + times + '.' + file.split('.')[-1]

                    seved_path = os.path.join(save_root, new_name)
                    file_json = {'name': new_name, 'topic': '', 'info': []}
                    all_list.append(file_json)

                    shutil.copy(file,seved_path)


    import json
    with open('../info/yunnan.json', "w",encoding='utf-8') as f:
        json.dump(all_list, f, ensure_ascii=False,indent=4)

if __name__ == '__main__':
    main()