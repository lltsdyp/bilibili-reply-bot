import json

import requests
import wbi
from bilibili.field import CommentOrderType

"""
获取指定oid对应的视频下的评论
num为页数，一页通常为19条评论
mode为排序方式，默认为 3
0 3：仅按热度
1：按热度+按时间
2：仅按时间
"""
async def get_reply_by_oid(bili_client,oid,num,type=1,mode=3):
    # print(oid)
    url = "https://api.bilibili.com/x/v2/reply/wbi/main"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': '*/*',
        'Host': 'api.bilibili.com',
        'Connection': 'keep-alive'
    }

    result=[]

    count=0

    params = {'type': type, 'oid': oid, 'mode': mode, 'pagination_str': dict()}

    for i in range(num):

        # wbi签名
        # img_key,sub_key=bili_client.get_wbi_keys()
        # signed_params=wbi.encWbi(params,img_key,sub_key)
        # signed_params= await bili_client.pre_request_data(params)

        response=await bili_client.get_video_comments(oid,order_mode=CommentOrderType.DEFAULT,next=i)
        # response.raise_for_status()
        resp_json=response.json()

        # 可能是关闭了评论区
        if resp_json['code']!=0:
            break

        replies=resp_json['data']['replies']

        # 无评论则退出
        if replies is None:
            break

        for reply in replies:
            result.append(reply)
        # try:
        #     next_str=resp_json['data']['cursor']['pagination_reply']
        #     if len:
        #         params['pagination_str']=''
        #     else:
        #         next_str=next_str['next_cursor']
        #         next_json=json.loads(next_str)
        #         next_json['pagination_reply']['data']['pn']+=1
        #         params['pagination_reply']=json.dumps(next_json)
        #         print(params['pagination_reply'])
        #     if resp_json['data']['cursor']['is_end']:
        #         print(f"Reach end, pages={i}")
        #         break
        # except KeyError:
        #     break # 读取完成
        pagination_reply=resp_json['data']['cursor']['pagination_reply']
        if len(pagination_reply) == 0:
            pass
        else:
            params['pagination_str']['offset']=pagination_reply['next_offset']
            print(f'Not end nextoffset={pagination_reply["next_offset"]}')
        if resp_json['data']['cursor']['is_end']:
            break
        # break #测试

    return result

if __name__ == '__main__':
    replies=get_reply_by_oid(112837145920276,20)
    print(replies)
    print(f"共{len(replies)}条评论")
