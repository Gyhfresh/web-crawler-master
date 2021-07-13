import os
import json
import re


filePath = 'demo/zhejiang'
os.chdir(filePath)
filelist=os.listdir(filePath)
print(filelist)
jsontemp=[]
count=0
for name in filelist:
    partern_desc = re.compile(r'cata_(.*?)\D', re.S)
    id = re.findall(partern_desc, name)
    count+=1
    print(count)
    # print(id)
    if id!=[]:
        with open('demo/zhejiang_before.json', 'r', encoding='utf-8') as f:
            while True:
                line = f.readline()
                if not line: # 到 EOF，返回空字符串，则终止循环
                    break
                js = json.loads(line)
                if js['info']['id']==id[0]:
                    subname=js['name']
                    newname = name.replace('cata_'+id[0],subname)
                    print(newname)
                    try:
                        os.rename(name,newname)
                    except:
                        print('eee')

                    partern_json = re.compile(r'(.*?)\.[a-z]', re.S)
                    jsonname = re.findall(partern_json, newname)
                    if jsonname[0] not in jsontemp:
                        jsontemp.append(jsonname[0])
                        data = {
                                        'name': jsonname[0],
                                        'topic': js['topic'],
                                        'info': js['info']
                                    }
                        json_str = json.dumps(data, ensure_ascii=False)
                        with open('demo/zhejiang.json', 'a', encoding='utf-8') as fp:
                                    fp.write(json_str)
                                    fp.write('\n')

                    break




