import os
import json
from util.TNlogger import TNLog

logger = TNLog(name='海南')

filenames = []


def gci(filepath):
    # 遍历filepath下所有文件，包括子目录
    files = os.listdir(filepath)
    for fi in files:
        fi_d = os.path.join(filepath, fi)
        if os.path.isdir(fi_d):
            gci(fi_d)
        else:
            filenames.append(os.path.join(filepath, fi))
            logger.info('开始存储' + str(os.path.join(filepath, fi)))


def hainan(save_path):
    # 递归遍历/root目录下所有文件
    gci(save_path)
    print(filenames)
    try:
        for file in filenames:
            data = {
                'name': str(file).split('\\')[-1],
                'time': str(file).split('\\')[-2]
            }
            with open(save_path + r'\海南.json', 'a', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
                f.write('\n')
    except:
        logger.error('无法找到文件')


if __name__ == '__main__':
    save_path = 'D:\\海南'
    hainan(save_path)
