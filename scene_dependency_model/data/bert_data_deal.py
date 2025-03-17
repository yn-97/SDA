import json
import math


def split_list(list,size):
    return [list[i:i+size] for i in range(0,len(list),size)]

with open('bert_data.json','r',encoding='utf-8') as f:
    data_list = json.load(f)

message_list=[]
for data in data_list:
    args = {}
    args['commit_id']=data['commit_id']
    args['repo']=data['project_url'].replace('https://github.com/','')
    args['msg']=data['commit_message']+data['cve_desc']
    args['filename']=data['file_name']
    args['diff']=data['diff']
    args['label']=''
    message_list.append(args)


with open('bert_data_deal.json','w',encoding='utf-8') as f:
    json.dump(message_list,f,indent=4)
