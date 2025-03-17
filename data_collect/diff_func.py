import os
import json

file_path = 'data/manual_labeled_with_func_names.json'
diff_list=[]
# 读取文件并转换为Python对象
with open(file_path, 'r', encoding='utf-8') as file:
    # 使用 json.load() 来解析整个文件内容为一个Python对象
    data_list = json.load(file)

print('data_list:',len(data_list))

for data in data_list:
    args={}
    args['idx']=data['idx']
    args['project']=data['project']
    args['commit_id']=data['commit_id']
    args['project_url']=data['project_url']
    args['commit_url']=data['commit_url']
    args['commit_message']=data['commit_message']
    args['target']=data['target']
    args['irrelevant']=data['irrelevant']
    args['func_before']=data['func']
    args['func_hash']=data['func_hash']
    args['file_name']=data['file_name']
    args['file_hash']=data['file_hash']
    args['cwe']=data['cwe']
    args['cve']=data['cve']
    args['cve_desc']=data['cve_desc']
    args['nvd_url']=data['nvd_url']
    args['func_name']=data['func_name']
    args['diff']=[]
    args['func_after']=[]
    diff_list.append(args)

with open("data/bert_data_ready.json", 'w', encoding='utf-8') as file:
    json.dump(diff_list, file,indent=4)

print('diff_list:',len(diff_list))