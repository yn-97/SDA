import json
import pickle
import numpy as np
import torch
from torch import cuda
from tqdm import tqdm
from transformers import RobertaForSequenceClassification, RobertaTokenizer
from model import VulFixMinerFineTuneClassifier, VulFixMinerClassifier
from patch import CommitAggregator
from torch.nn import functional as F
from torch import nn as nn

use_cuda = cuda.is_available()
device = torch.device("cuda:0" if use_cuda else "cpu")

def get_diff_num(diff):
    finetune_model_path = './data/model/patch_vulfixminer_finetuned_model.sav'
    finetune_model = VulFixMinerFineTuneClassifier()

    finetune_model.load_state_dict(torch.load(finetune_model_path))
    code_bert = finetune_model.code_bert
    code_bert.eval()
    code_bert.to(device)

    print("Finished loading")

    aggregator = CommitAggregator(code_bert)
    embeddings = aggregator.transform(diff)
    model = VulFixMinerClassifier()
    model = nn.DataParallel(model)
    model.to(device)

    outs = model(embeddings)
    # 根据形状调整
    if len(outs.shape) == 1:  # 如果是 1D 张量
        outs = F.softmax(outs, dim=0)
        prob = outs[1].item()
        return prob
    elif len(outs.shape) == 2:  # 如果是 2D 张量
        outs = F.softmax(outs, dim=1)
        prob = outs[:, 1].mean().item()
        return prob


def get_message_num(message):
    model = RobertaForSequenceClassification.from_pretrained('roberta-base', num_labels=2)
    model.to(device)
    # 加载微调后的模型参数
    message_model_path = 'data/model/message.sav'
    model.load_state_dict(torch.load(message_model_path))
    # 初始化分词器
    tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
    # 对输入消息进行编码
    inputs = tokenizer(message, padding='max_length', max_length=128, truncation=True, return_tensors="pt")
    # 将数据移动到相同设备上
    inputs = {key: value.to(device) for key, value in inputs.items()}
    # 模型预测
    model.eval()
    with torch.no_grad():
        outs = model(**inputs)  # 使用关键字参数传递
        probabilities = F.softmax(outs.logits, dim=1)  # logits 转化为概率

    # 打印类别 1 的概率
    return probabilities[:, 1].item()


# 加载 JSON 数据
with open('data/output/all.json', 'r', encoding='utf-8') as f:
    data_list = json.load(f)

# 加载模型
with open('data/model/tf_commit_classifier.sav', 'rb') as f:
    model = pickle.load(f)

final_list = []
for data in tqdm(data_list):
    args = {}
    args['idx'] = data['idx']
    args['project'] = data['project']
    args['commit_id'] = data['commit_id']
    args['project_url'] = data['project_url']
    args['commit_url'] = data['commit_url']
    args['commit_message'] = data['commit_message']
    args['target'] = data['target']
    args['func_before'] = data['func_before']
    args['func_hash'] = data['func_hash']
    args['file_name'] = data['file_name']
    args['file_hash'] = data['file_hash']
    args['cwe'] = data['cwe']
    args['cve'] = data['cve']
    args['cve_desc'] = data['cve_desc']
    args['diff'] = data['diff']
    args['func_after'] = data['func_after']

    if data['diff'] == '' or data['commit_message'] == '':
        args['prediction'] = ''
        final_list.append(args)
        continue
    diff_feature = get_diff_num(data['diff'])  # 返回 diff 的特征
    message_feature = get_message_num(data['commit_message'] + data['cve_desc'])  # 返回消息的特征

    # 构建特征列表
    feature_list = [[diff_feature, message_feature]]

    # 转换为 NumPy 数组
    feature_array = np.array(feature_list)

    # 模型预测
    result = model.predict(feature_array)
    args['prediction'] = result[0]
    print(args)
    final_list.append(args)

# 将 final_list 中的 numpy 类型转换为原生 Python 类型
def convert_numpy_types(obj):
    if isinstance(obj, np.integer):  # 转换 numpy 整数为 Python int
        return int(obj)
    elif isinstance(obj, np.floating):  # 转换 numpy 浮点数为 Python float
        return float(obj)
    elif isinstance(obj, np.ndarray):  # 转换 numpy 数组为列表
        return obj.tolist()
    elif isinstance(obj, dict):  # 遍历字典
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):  # 遍历列表
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj  # 保留其他类型

# 转换 final_list
serializable_list = convert_numpy_types(final_list)

# 写入 JSON 文件
with open('data/output/final_result.json', 'w', encoding='utf-8') as file:
    json.dump(serializable_list, file, indent=4)

print("Data has been written to final_result.json")
