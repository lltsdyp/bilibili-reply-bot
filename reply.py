import requests
import wbi

"""
获取指定oid对应的视频下的评论
num为页数，一页通常为19条评论
mode为排序方式，默认为 3
0 3：仅按热度
1：按热度+按时间
2：仅按时间
"""
def get_reply_by_oid(oid,num,type=1,mode=3):
    url = "https://api.bilibili.com/x/v2/reply/wbi/main"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': '*/*',
        'Host': 'api.bilibili.com',
        'Connection': 'keep-alive'
    }

    result=[]

    count=0

    params = {
        'type': type,
        'oid':oid,
        'mode':mode
    }

    for _ in range(num):

        # wbi签名
        img_key,sub_key=wbi.getWbiKeys()
        signed_params=wbi.encWbi(params,img_key,sub_key)

        response=requests.get(url,headers=headers,params=signed_params)
        response.raise_for_status()
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
        try:
            params['pagination_reply']=resp_json['data']['cursor']['pagination_reply']['next_offset']
        except KeyError:
            break # 读取完成
        # break #测试

    return result

if __name__ == '__main__':
    replies=get_reply_by_oid(112837145920276,20)
    print(replies)
    print(f"共{len(replies)}条评论")
