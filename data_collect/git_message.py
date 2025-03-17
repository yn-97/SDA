import requests
from bs4 import BeautifulSoup

def get_commit_message(commit_url):
    # 发送 HTTP 请求
    response = requests.get(commit_url)
    if response.status_code != 200:
        print(f"Failed to retrieve commit information: {response.status_code}")
        return None

    # 解析 HTML 内容
    soup = BeautifulSoup(response.content, 'html.parser')

    # 查找 commit_message
    commit_message_element = soup.find('div', {'class': 'commit-title'})
    if commit_message_element:
        commit_message = commit_message_element.text.strip()
        return commit_message
    else:
        print("Commit message element not found")
        return None

# 示例 URL
commit_url = "https://github.com/alexarchen/mupdf/commit/83d4dae44c71816c084a635550acc1a51529b881"

# 获取 commit_message
commit_message = get_commit_message(commit_url)
if commit_message:
    print(f"Commit Message: {commit_message}")
else:
    print("Failed to retrieve commit message")

