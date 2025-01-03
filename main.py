import asyncio
import os
from typing import Optional, Dict

import videosearch
from reply import get_reply_by_oid
import time
import csv
import concurrent.futures

from playwright.async_api import (BrowserContext, BrowserType, Page,
                                  async_playwright)

from bilibili.login import BilibiliLogin
from bilibili.client import BilibiliClient
import config
from tools import utils

# 每页的并发线程数
EXECUTOR_PER_PAGE=4

async def launch_browser(
        chromium: BrowserType,
        playwright_proxy: Optional[Dict],
        user_agent: Optional[str],
        headless: bool = True
) -> BrowserContext:
    """
    launch browser and create browser context
    :param chromium: chromium browser
    :param playwright_proxy: playwright proxy
    :param user_agent: user agent
    :param headless: headless mode
    :return: browser context
    """
    # utils.logger.info(
    #     "[BilibiliCrawler.launch_browser] Begin create browser context ...")
    if config.SAVE_LOGIN_STATE:
        # feat issue #14
        # we will save login state to avoid login every time
        user_data_dir = os.path.join(os.getcwd(), "browser_data",
                                     config.USER_DATA_DIR % config.PLATFORM)  # type: ignore
        browser_context = await chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            accept_downloads=True,
            headless=headless,
            proxy=playwright_proxy,  # type: ignore
            viewport={"width": 1920, "height": 1080},
            user_agent=user_agent
        )
        return browser_context
    else:
        # type: ignore
        browser = await chromium.launch(headless=headless, proxy=playwright_proxy)
        browser_context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=user_agent
        )
        return browser_context

async def create_bilibili_client(browser_context,context_page) -> BilibiliClient:
    """
    create bilibili client
    :return: bilibili client
    """
    # utils.logger.info(
    #     "[BilibiliCrawler.create_bilibili_client] Begin create bilibili API client ...")
    cookie_str, cookie_dict = utils.convert_cookies(await browser_context.cookies())
    bilibili_client_obj = BilibiliClient(
        proxies=None,
        headers={
            "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
            "Cookie": cookie_str,
            "Origin": "https://www.bilibili.com",
            "Referer": "https://www.bilibili.com",
            "Content-Type": "application/json;charset=UTF-8"
        },
        playwright_page=context_page,
        cookie_dict=cookie_dict,
    )
    return bilibili_client_obj

async def show_login_page():
    index_url = "https://www.bilibili.com"
    async with async_playwright() as playwright:
        # Launch a browser context.
        chromium = playwright.chromium
        browser_context = await launch_browser(
            chromium,
            None,
            None,
            headless=config.HEADLESS
        )
        # stealth.min.js is a js script to prevent the website from detecting the crawler.
        await browser_context.add_init_script(path="libs/stealth.min.js")
        context_page = await browser_context.new_page()
        await context_page.goto(index_url)
        # Create a client to interact with the xiaohongshu website.
        bili_client = await create_bilibili_client(browser_context,context_page)
        if not await bili_client.pong():
            login_obj = BilibiliLogin(
                login_type=config.LOGIN_TYPE,
                login_phone="",  # your phone number
                browser_context=browser_context,
                context_page=context_page,
                cookie_str=config.COOKIES
            )
            await login_obj.begin()
            await bili_client.update_cookies(browser_context=browser_context)

def save_comments_to_csv(comments, video_bvname):
    with open(f'.\\{video_bvname}.csv', mode='w', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['评论内容', '性别','点赞数量', '回复时间'])
        writer.writeheader()
        for comment in comments:
            writer.writerow(comment)

def fetch_replies(keyword,page_count=2,reply_page_per_video=10):
    search_result=videosearch.search_bilibili_videos(keyword,page_count)

    result=[]

    with concurrent.futures.ThreadPoolExecutor(max_workers=page_count*EXECUTOR_PER_PAGE) as executor:
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

async def main():

    # start_time=time.time() # 测试用
    await show_login_page()
    keyword=input("请输入视频关键字：")

    result=fetch_replies(keyword,4,10)

    save_comments_to_csv(result,keyword)

    # end_time=time.time() # 测试用

    # print(f"总耗时：{end_time-start_time}s") # 测试用

    # print(f"检索了{count}个视频，抓取到{len(result)}条评论")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(0)
