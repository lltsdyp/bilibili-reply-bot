import videosearch
from reply import get_reply_by_oid
import time
import csv
import concurrent.futures

def save_comments_to_csv(comments, video_bvname):
    with open(f'.\\{video_bvname}.csv', mode='w', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['评论内容', '性别','点赞数量', '回复时间'])
        writer.writeheader()
        for comment in comments:
            writer.writerow(comment)

def fetch_replies(keyword,page_count=2,reply_page_per_video=10):
    search_result=videosearch.search_bilibili_videos(keyword,page_count)

    result=[]

    with concurrent.futures.ThreadPoolExecutor(max_workers=page_count*4) as executor:
        future_to_video={executor.submit(get_reply_by_oid,i[1],reply_page_per_video,1,3) for i in search_result.items()}
        for future in concurrent.futures.as_completed(future_to_video):
            replies=[]
            try:
                replies=future.result()
            except Exception as e:
                print("找不到更多的相关视频")
                break

            if replies is not None:
                for reply in replies:
                    result.append({
                        '评论内容': reply['content']['message'],
                        '性别': reply['member']['sex'],
                        '点赞数量': reply['like'],
                        '回复时间': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reply['ctime']))
                    })
    return result

if __name__ == '__main__':
    keyword=input("请输入视频关键字：")

    # start_time=time.time() # 测试用

    result=fetch_replies(keyword,4,10)

    save_comments_to_csv(result,keyword)

    # end_time=time.time() # 测试用

    # print(f"总耗时：{end_time-start_time}s") # 测试用

    # print(f"检索了{count}个视频，抓取到{len(result)}条评论")