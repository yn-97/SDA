import json


none_list=[]
with open('data/second.json','r',encoding='utf-8') as f:
    bert_data_ready_list=json.load(f)

none_list=[]
for bert_data in bert_data_ready_list:
    if bert_data['func_after']==[]:
        print(bert_data['idx'])
        none_list.append(bert_data)

print(len(none_list))

# print("bert_data_ready_list:",len(bert_data_ready_list))
# with open('data/all.json','r',encoding='utf-8') as f:
#     all_list=json.load(f)
#
# print("all_list:",len(all_list))
#
# idx_list=[]
# for all in all_list:
#     idx_list.append(all['idx'])
#
# data_list=[]
# print(len(bert_data_ready_list))
# for data in bert_data_ready_list:
#     if data['idx'] not in idx_list:
#         continue
#     data_list.append(data)
#
#
# print(len(data_list))
# with open('data/bert_data.json','w',encoding='utf-8') as f:
#     json.dump(data_list,f,indent=4)
