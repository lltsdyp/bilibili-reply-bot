import asyncio
import datetime
import os
from typing import Optional, Dict

from store import lite
import videosearch
from bilibili import BilibiliCrawler
from reply import get_reply_by_oid
import time
import csv
import config

from playwright.async_api import (BrowserContext, BrowserType, Page,
                                  async_playwright)

from bilibili.login import BilibiliLogin
from bilibili.client import BilibiliClient
import config
from tools import utils

def save_comments_to_csv(comments, video_bvname):
    with open(f'{video_bvname}.csv', mode='w', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['评论内容', '性别','点赞数量', '回复时间'])
        writer.writeheader()
        for comment in comments:
            writer.writerow(comment)

"""
filter:指定筛选近多少天的评论，如：如果近一年则filter=365
"""
async def fetch_replies(client, keyword, page_count=2, reply_page_per_video=10, filter=None):
    search_result = videosearch.search_bilibili_videos(keyword, page_count)

    result = []

    async def fetch_and_filter_replies(oid):
        replies = await get_reply_by_oid(client, oid, reply_page_per_video, 1, 3)
        if replies is not None:
            for reply in replies:
                reply_time = datetime.datetime.fromtimestamp(reply['ctime'])
                current_time = datetime.datetime.now()
                time_difference = current_time - reply_time

                if filter is None or time_difference < datetime.timedelta(days=filter):
                    result.append({
                        '评论内容': reply['content']['message'],
                        '性别': reply['member']['sex'],
                        '点赞数量': reply['like'],
                        '回复时间': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reply['ctime']))
                    })

    tasks = [fetch_and_filter_replies(i[1]) for i in search_result.items()]
    await asyncio.gather(*tasks)
    return result

async def main():

    bili_crawler = BilibiliCrawler()
    # 登录
    await bili_crawler.start()

    keyword=input("请输入视频关键字：")
    search_result = videosearch.search_bilibili_videos(keyword, config.CRAWLER_MAX_SEARCH_PAGE_COUNT)


    l=[i[1] for i in search_result.items()]

    start_time=time.time() # 测试用
    await bili_crawler.batch_get_video_comments(l)
    end_time=time.time() # 测试用

    print(f"总耗时：{end_time-start_time}s") # 测试用

    save_comments_to_csv(lite.result,keyword)


    # print(f"检索了{count}个视频，抓取到{len(result)}条评论")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(0)
