import json
import math


def split_list(list,size):
    return [list[i:i+size] for i in range(0,len(list),size)]

with open('output/all.json','r',encoding='utf-8') as f:
    data_list = json.load(f)

data_list=split_list(data_list,1000)
cnt=1
for data in data_list:
    path=f'func_{cnt}.json'
    with open(path,'w',encoding='utf-8') as f:
        json.dump(data,f,indent=4)
    cnt+=1