import json
import os
import subprocess

url_list=[]
# 文件路径
file_path = 'data/manual_labeled_with_func_names.json'

# 读取文件并转换为Python对象
with open(file_path, 'r', encoding='utf-8') as file:
    # 使用 json.load() 来解析整个文件内容为一个Python对象
    data_list = json.load(file)

for data in data_list:
    data['project_url']=data['project_url'].replace('https://github.com', 'https://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@github.com')
    url_list.append(data['project_url'])

url_list=list(set(url_list))

os.chdir('data/project')

for url in url_list:
    project_name=url.split('/')[-1]
    if  os.path.exists(project_name):
        continue
    print(f'git clone {project_name}')
    subprocess.run(f'git clone {url}', shell=True)
    print('file save to :'+url)