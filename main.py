import videosearch
from reply import get_reply_by_oid
import time
import csv

def save_comments_to_csv(comments, video_bvname):
    with open(f'.\\{video_bvname}.csv', mode='w', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['评论内容', '性别','点赞数量', '回复时间'])
        writer.writeheader()
        for comment in comments:
            writer.writerow(comment)

if __name__ == '__main__':
    keyword=input("请输入视频关键字：")

    search_result=videosearch.search_bilibili_videos(keyword,2)

    count=0
    result=[]
    for i in search_result.items():
        count+=1
        replies=[]
        try:
            replies=get_reply_by_oid(i[1],10)
        except Exception as e:
            print("找不到更多的相关视频")
            break
        print(f"视频：{i[0]} 的评论")

        for reply in replies:
            result.append({
                '评论内容': reply['content']['message'],
                '性别': reply['member']['sex'],
                '点赞数量': reply['like'],
                '回复时间': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reply['ctime']))
            })

    save_comments_to_csv(result,keyword)

    print(f"检索了{count}个视频，抓取到{len(result)}条评论")