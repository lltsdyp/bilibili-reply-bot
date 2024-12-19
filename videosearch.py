import requests
import wbi
import urllib

"""
工具函数
用于提取json中的信息
"""
def search_filter_json(json_body):
    dict_result=dict()
    for video in json_body['data']['result']:
        # print(f"标题: {video['title']}, 播放 t量: {video['play']}, 作者: {video['author']}, av号{video['aid']}")
        dict_result.setdefault(video['title'], video['aid'])
        #TODO 删除em标签
    return dict_result

"""
使用给定的参数搜索bilibili
num为最大搜索页数，一页通常为20个视频
duration默认为0 
全部时长：0
10分钟以下：1
10-30分钟：2
30-60分钟：3
60分钟以上：4
"""
def search_bilibili_videos(keyword, num,order='totalrank', duration=0,tids=0):
    # 调用api参数：
    # URL
    url = "https://api.bilibili.com/x/web-interface/wbi/search/type"

    # 设置请求参数
    params = {
        'search_type': 'video',
        'keyword': urllib.parse.quote(keyword),
        'order': order,
        'duration': duration,
        'tids': tids,
        'page': 1
    }

    # 设置请求头，包括Referer和User-Agent
    headers = {
        'Referer': 'https://www.bilibili.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': '*/*',
        'Host': 'api.bilibili.com',
        'Connection': 'keep-alive',
        'Cookie': wbi.get_buvid3()
    }

    result=dict()

    #自动向下取整
    for i in range(1,num+1):
        params['page'] = i


        # 发送GET请求
        # 发送前进行wbi签名
        img_key,sub_key=wbi.getWbiKeys()
        signed_params=wbi.encWbi(params,img_key,sub_key)

        # 发送签名后的请求
        response = requests.get(url, headers=headers, params=signed_params)

        # 检查响应状态码
        response.raise_for_status()

        resp_dict=search_filter_json(response.json())
        if resp_dict is None:
            break
        result.update(resp_dict)
        if len(resp_dict)<20:
            break

    return result



# 示例调用
if __name__ == "__main__":

    result=dict()

    keyword = "陈睿"
    result.update(search_bilibili_videos(keyword,2))

    print(f"Length: {len(result)}")
    print(result)