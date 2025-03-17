import os
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "Accept": "application/vnd.github.v3.diff",
    "Authorization": "token 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"
}

file_path = 'data/bert_data_ready.json'
diff_list=[]
# 读取文件并转换为Python对象
with open(file_path, 'r', encoding='utf-8') as file:
    # 使用 json.load() 来解析整个文件内容为一个Python对象
    data_list = json.load(file)

print('data/data_list:',len(data_list))

for data in data_list:
    if data['diff']==[]:
        if 'https://github.com' not in data['commit_url']:
            continue
        path=data['commit_url'].replace('https://github.com','https://api.github.com/repos').replace('commit','commits')
        print(path)
        try:
            response = requests.get(path,headers=headers,verify=False)
            print(response.status_code)
            if response.status_code == 200:
                data['diff'].append(response.text)
        except Exception as e:
            continue


with open("data/second.json", 'w', encoding='utf-8') as file:
    json.dump(data_list, file,indent=4)

print('second_list:',len(data_list))