# -*- coding:utf-8 -*-
import requests
import pandas as pd
from lxml import etree

res = requests.get('http://tjj.qinghai.gov.cn/tjData/newData/202106/t20210617_73509.html')
res_elements = etree.HTML(res.text)
print(res_elements)
table = res_elements.xpath('//table[@align="center"]')
table = etree.tostring(table[0], encoding='utf-8').decode()

df = pd.read_html(table, encoding='utf-8', header=0)[0]
results = list(df.T.to_dict().values())  # 转换成列表嵌套字典的格式
df.to_csv("std.csv", index=False, encoding='utf-8',)

