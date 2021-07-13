import os
import json

filenames = []
root = r'D:\download\worm\湖北'


def gci(filepath):
    # 遍历filepath下所有文件，包括子目录
    files = os.listdir(filepath)
    for fi in files:
        fi_d = os.path.join(filepath, fi)
        if os.path.isdir(fi_d):
            gci(fi_d)
        else:
            filenames.append(str(os.path.join(filepath, fi)).split('\\')[-3:])


# 递归遍历/root目录下所有文件
gci(root)
print(filenames)
for file in filenames:
    data = {
        'name': file[-1],
        'time': file[0],
        'topic': file[1],
    }
    with open(root + r'\湖北.json', 'a', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
        f.write('\n')
