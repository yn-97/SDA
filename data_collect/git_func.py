import json
import requests
from tree_sitter import Language, Parser
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
func_after_list=[]
# 构建 C 语言的解析库
language_path = 'language/build/my-languages.so'
# if not os.path.exists(language_path):
#     Language.build_library(
#         language_path,
#         ['language/tree-sitter-c','language/tree-sitter-cpp']
#     )
C_LANGUAGE = Language(language_path, 'c')
CPP_LANGUAGE = Language(language_path, 'cpp')

# 创建解析器对象
c_parser = Parser()
c_parser.set_language(C_LANGUAGE)
cpp_parser = Parser()
cpp_parser.set_language(CPP_LANGUAGE)
data_list=[]
c_identifier=['identifier']
def print_node_c(node, func_name):
    if node.type == 'function_definition':
        for grandchild in node.children:
            if grandchild.type == 'function_declarator':
                for great_grandchild in grandchild.children:
                    if great_grandchild.type not in c_identifier and 'identifier' in great_grandchild.type:
                        c_identifier.append(great_grandchild.type)
                    if great_grandchild.type in c_identifier and great_grandchild.text.decode('utf8') == func_name:
                        return node.text.decode('utf-8')  # 找到匹配的函数定义时返回节点
            elif grandchild.type == 'pointer_declarator':
                for great_grandchild in grandchild.children:
                    if great_grandchild.type == 'function_declarator':
                        for great_grandchild_child in great_grandchild.children:
                            if great_grandchild_child.type not in c_identifier and 'identifier' in great_grandchild_child.type:
                                c_identifier.append(great_grandchild.type)
                            if great_grandchild_child.type in c_identifier and great_grandchild_child.text.decode( 'utf8') == func_name:
                                return node.text.decode('utf-8')  # 找到匹配的函数定义时返回节点


    # 递归遍历子节点
    for child in node.children:
        found_node = print_node_c(child, func_name)
        if found_node is not None:
            return found_node  # 如果在子节点中找到了匹配的节点，则返回该节点

    # 如果没有找到匹配的节点，函数默认返回 None
    return None

cpp_identifier=['scoped_identifier','type_identifier','identifier','qualified_identifier','field_identifier']
def print_node_cpp(node, func_name):
    # 首先检查当前节点是否为函数定义
    if node.type == 'function_definition':
        for child in node.children:
            if child.type == 'function_declarator':
                for child_child in child.children:
                    if child_child.type not in cpp_identifier and 'identifier' in child_child.type:
                        cpp_identifier.append(child_child.type)
                    if child_child.type in cpp_identifier and child_child.text.decode('utf-8') == func_name:
                        return node.text.decode('utf-8')  # 找到匹配的函数定义时返回节点

    # 递归遍历子节点
    for child in node.children:
        found_node = print_node_cpp(child, func_name)
        if found_node is not None:
            return found_node  # 如果在子节点中找到了匹配的节点，则返回该节点

    # 如果没有找到匹配的节点，函数默认返回 None
    return None


headers = {
    "Authorization": "token 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"
}

with open('data/input.json','r') as  f:
    data_list=json.load(f)

print("data_list:",len(data_list))
cnt=0
for data in data_list:
    if data['diff'] !=[] and data['func_after']==[]:
        for diff in data['diff']:
            file_path=re.findall(r'diff --git a/(.+?) b/', diff)
            for path in file_path:
                url=data['project_url'].replace('https://github.com','https://raw.githubusercontent.com')
                file_url=f"{url}/{data['commit_id']}/{path}"
                print(file_url)
                try:
                    response = requests.get(file_url,headers=headers,verify=False)
                    print(response.status_code)
                    if response.status_code == 200:
                        c_node = c_parser.parse(response.content)
                        c_text = print_node_c(c_node.root_node, data['func_name'])
                        if c_text is not None:
                            data["func_after"].append(c_text)
                            continue
                        cpp_node = cpp_parser.parse(response.content)
                        cpp_text = print_node_cpp(cpp_node.root_node, data['func_name'])
                        if cpp_text is not None:
                            data["func_after"].append(cpp_text)
                            continue
                except:
                    continue
    func_after_list.append(data)
    cnt+=1
    print("当前：",cnt,'总共：',len(data_list))

with open('data/func.json','w',encoding='utf-8') as f:
    json.dump(func_after_list,f,indent=4)
