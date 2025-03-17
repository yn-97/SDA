import json
import math


def split_list(list,size):
    return [list[i:i+size] for i in range(0,len(list),size)]

with open('second.json','r',encoding='utf-8') as f:
    data_list = json.load(f)

list=split_list(data_list,math.ceil(len(data_list)*0.8))

message_list=[]
args=[]
for train in list[0]:
    args = {}
    args['commit_id']=train['commit_id']
    args['repo']=train['project_url'].replace('https://github.com/','')
    args['msg']=train['commit_message']+train['cve_desc']
    args['filename']=train['file_name']
    args['diff']=train['diff']
    args['label']=train['dependency']
    args['partition']='train'
    message_list.append(args)

for test in list[1]:
    args = {}
    args['commit_id']=test['commit_id']
    args['repo']=test['project_url'].replace('https://github.com/','')
    args['msg']=test['commit_message']+test['cve_desc']
    args['filename']=test['file_name']
    args['diff']=test['diff']
    args['label']=test['dependency']
    args['partition']='test'
    message_list.append(args)

with open('message.json','w',encoding='utf-8') as f:
    json.dump(message_list,f,indent=4)
