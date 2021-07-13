import os
import json
from util.TNlogger import TNLog

logger = TNLog(name='湖北')

filenames = []


def gci(filepath):
    # 遍历filepath下所有文件，包括子目录
    files = os.listdir(filepath)
    for fi in files:
        fi_d = os.path.join(filepath, fi)
        if os.path.isdir(fi_d):
            gci(fi_d)
        else:
            filenames.append(str(os.path.join(filepath, fi)).split('\\')[-3:])
            logger.info('开始存储' + str(os.path.join(filepath, fi)))


def hubei(save_path):
    # 递归遍历/root目录下所有文件
    gci(save_path)
    print(filenames)
    try:
        for file in filenames:
            data = {
                'name': file[-1],
                'time': file[0],
                'topic': file[1],
            }
            with open(save_path + r'\湖北.json', 'a', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
                f.write('\n')
    except:
        logger.error('无法找到文件')


if __name__ == '__main__':
    save_path = 'D:\\湖北'
    hubei(save_path)
