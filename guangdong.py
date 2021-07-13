import os
import shutil
import json
import pandas as pd
import win32com.client as win32

from tqdm import tqdm

filenames = []
xlsxs = []
root = r'D:\download\worm\广东\x'
dest = r'D:\download\worm\广东'
time = '2015'


def gci(filepath):
    # 遍历filepath下所有文件，包括子目录
    files = os.listdir(filepath)
    for fi in files:
        fi_d = os.path.join(filepath, fi)
        if os.path.isdir(fi_d):
            gci(fi_d)
        else:
            filenames.append(str(os.path.join(filepath, fi)))


# 递归遍历/root目录下所有文件


def xls2xlsx(names):
    for file in tqdm(names):
        if str(file).split('.')[-1] == 'xls':
            try:
                excel = win32.gencache.EnsureDispatch('Excel.Application')
                wb = excel.Workbooks.Open(file)
                # xlsx: FileFormat=51
                # xls:  FileFormat=56,
                # 后缀名的大小写不通配，需按实际修改：xls，或XLS
                wb.SaveAs(file.replace('xls', 'xlsx'), FileFormat=51)  # 我这里原文件是大写
                wb.Close()
                excel.Application.Quit()
                os.remove(file)
                xlsxs.append(str(file).split('.')[0] + '.xlsx')
                # df = pd.read_excel(file)
                # print(df.head)
                # print(file)
            except:
                continue


def rename(names):
    for file in names:
        if str(file).split('.')[-1] == 'xls' or str(file).split('.')[-1] == 'xlsx':
            filename = str(file).split('.')[0] + '.xlsx'
            df = pd.read_excel(filename)
            print(filename)
            name_list = list(df.keys())
            if len(name_list) > 0:
                print(name_list[0])
                shutil.copyfile(filename, dest + '\\' + time + '\\' + name_list[0] + '.xlsx')
                data = {
                    'name': name_list[0],
                    'time': time
                }
                with open(dest + '\\广东.json', 'a', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False)
                    f.write('\n')


if __name__ == '__main__':
    gci(root)
    xls2xlsx(filenames)
    rename(xlsxs)
