import subprocess
import os
import json
from tree_sitter import Language, Parser


# 构建 C 语言的解析库
language_path = 'language/build/my-languages.so'
if not os.path.exists(language_path):
    Language.build_library(
        language_path,
        ['language/tree-sitter-c','language/tree-sitter-cpp']
    )
C_LANGUAGE = Language(language_path, 'c')
CPP_LANGUAGE = Language(language_path, 'cpp')

# 创建解析器对象
parser = Parser()
parser.set_language(C_LANGUAGE)


def print_node(node,func_name,file_path):
    if node.type=='function_definition':
        for grandchild in node.children:
            if grandchild.type == 'function_declarator':
                for great_grandchild in grandchild.children:
                    if great_grandchild.type == 'identifier' and great_grandchild.text.decode('utf8') == func_name:
                        save_to_file(file_path,node.text.decode('utf8').replace('\n',''))

    for child in node.children:
        print_node(child,func_name,file_path)


def get_commit_diff(data):
    # """获取指定commit的diff信息"""
    project_name = data["project_url"].split('/')[-1]
    clone_dir = f"tmp/{project_name}/{data['commit_id']}"

    os.chdir(f'data/project/{project_name}')
    subprocess.run(f"git checkout {data['commit_id']}", shell=True,encoding='utf-8')

    # 获取diff信息
    func_name=data['func_name']
    path = subprocess.run(
        ["git", "grep", "-l", func_name],
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,  # 使输出为字符串而非字节
        check=True  # 如果命令返回非零退出状态，则抛出CalledProcessError异常
    )

    results=[]
    lines =path.stdout.splitlines()
    for line in lines:
        if '.c' in line or '.cc' in line or '.cpp' in line:
            result = subprocess.run(f"git show {data['commit_id']} -- {line}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True,encoding='utf-8')
            if result.stdout !='':
                results.append(result.stdout)
    os.makedirs('../../{}'.format(clone_dir), exist_ok=True)
    os.chdir('../../{}'.format(clone_dir))
    return results


def extract_c_files(diff_info):
    """提取被修改的C文件"""
    diff_lines = diff_info.splitlines()
    modified_files = []
    for line in diff_lines:
        if line.startswith("diff --git") and line.endswith(".cc"):
            # 提取文件路径并去掉 'a/' 和 'b/' 前缀
            file_path = line.split(" ")[-1].replace('a/', '').replace('b/', '')
            modified_files.append(file_path)
        if line.startswith("diff --git") and line.endswith(".c"):
            # 提取文件路径并去掉 'a/' 和 'b/' 前缀
            file_path = line.split(" ")[-1].replace('a/', '').replace('b/', '')
            modified_files.append(file_path)
        if line.startswith("diff --git") and line.endswith(".cpp"):
             # 提取文件路径并去掉 'a/' 和 'b/' 前缀
            file_path = line.split(" ")[-1].replace('a/', '').replace('b/', '')
            modified_files.append(file_path)
    return modified_files


def get_file_content(commit_id, file_path, previous=False):
    """获取指定commit前后的文件内容"""
    if previous:
        command = f"git show {commit_id}~1:{file_path}"
    else:
        command = f"git show {commit_id}:{file_path}"

    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,encoding='utf-8')

    if result.returncode != 0:
        print(f"Error retrieving file: {file_path}")
        return None
    return result.stdout

def save_to_file(filename, content):
    """保存内容到文件"""
    if content:
        with open(filename, 'w',encoding='utf-8') as file:
            file.write(content)
    print('file saved:'+filename)


def save_to_json(filename, data):
    """保存数据到json文件"""
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


def read_file_c(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

def analyze_commit_from_json(data):
    """主函数：从JSON文件中读取并分析给定commit，输出diff、文件和函数信息"""

    project = data["project"]
    commit_id = data["commit_id"]
    func_code = data["func"]  # 目标函数的代码
    func_name=data["func_name"]
    project_name = data['project_url'].split('/')[-1]

    # 获取diff信息
    diff_info = get_commit_diff(data)
    # 保存diff为json文件
    diff_output_file = f"{commit_id}_diff.json"
    save_to_json(diff_output_file, {"diff_info": diff_info})
    print(f"Diff saved to {diff_output_file}")
    print('diff_info:',diff_info)
    if diff_info  is not None:
        for diff in diff_info:
            # 提取被修改的C文件
            modified_files = extract_c_files(diff)
            print("Modified C Files:\n", modified_files)


            for file_path in modified_files:
                os.chdir(f'../../../project/{project_name}')
                # 获取diff前后的文件内容
                file_content_before = get_file_content(commit_id, file_path, previous=True)
                file_content_after = get_file_content(commit_id, file_path, previous=False)

                # 如果文件内容为空，输出错误信息并跳过
                if not file_content_before or not file_content_after:
                    print(f"Error: File content is empty for {file_path}")
                    continue

                # 保存整个C文件内容到.c文件
                before_file_output = f"{commit_id}_before_{os.path.basename(file_path)}"
                after_file_output = f"{commit_id}_after_{os.path.basename(file_path)}"

                os.chdir(f"../../tmp/{project_name}/{commit_id}")
                save_to_file(before_file_output, file_content_before)
                save_to_file(after_file_output, file_content_after)



                before_func_output = f"{commit_id}_before_func_{os.path.basename(file_path)}"
                after_func_output = f"{commit_id}_after_func_{os.path.basename(file_path)}"
                berfore_tree=parser.parse(read_file_c(before_file_output))
                after_tree=parser.parse(read_file_c(after_file_output))
                print_node(berfore_tree.root_node,func_name,before_func_output)
                print_node(after_tree.root_node,func_name,after_func_output)
    else:
        print('diff is null')



def read_from_start_text(path,func_name):
    with open(path,'r', encoding='utf-8') as a:
        context = a.read()
    with open(path,'r', encoding='utf-8') as a:
        for line in a:
            if func_name in line:
                start_text = line.strip()

    # 找到 start_text 的起始位置
    stack=[]
    start_index = context.index(start_text)
    end_index = context.index(start_text)
    for i in range(start_index, len(context)):
        char = context[i]
        if char == '{':
            stack.append('{')
        elif char == '}':
            if not stack:
                raise ValueError("Unmatched '}' found before the corresponding '{'.")
            stack.pop()
            # 如果栈为空，说明找到了匹配的 '}'
            if not stack:
                end_index = i
                break

        # 从 start_text 开始读取后续内容
    result = context[start_index:end_index + 1]
    return result

file_path = 'data/manual_labeled_with_func_names.json'

# 读取文件并转换为Python对象
with open(file_path, 'r', encoding='utf-8') as file:
    # 使用 json.load() 来解析整个文件内容为一个Python对象
    data_list = json.load(file)

for data in data_list:
    os.chdir('D:\项目\python\data_crawling_out')
    project_name=data['project_url'].split('/')[-1]
    os.makedirs(f"data/project/{project_name}", exist_ok=True)
    analyze_commit_from_json(data)


# # 调用主函数，传入JSON文件路径
# analyze_commit_from_json('data/input.json')
