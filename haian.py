import os
import json

filenames = []
root = r'D:\download\worm\海南'


def gci(filepath):
    # 遍历filepath下所有文件，包括子目录
    files = os.listdir(filepath)
    for fi in files:
        fi_d = os.path.join(filepath, fi)
        if os.path.isdir(fi_d):
            gci(fi_d)
        else:
            filenames.append(os.path.join(filepath, fi))


# 递归遍历/root目录下所有文件
gci(root)
print(filenames)
for file in filenames:
    data = {
        'name': str(file).split('\\')[-1],
        'time': str(file).split('\\')[-2]
    }
    with open(root + r'\海南.json', 'a', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
        f.write('\n')
