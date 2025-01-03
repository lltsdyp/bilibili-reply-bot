# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：  
# 1. 不得用于任何商业用途。  
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。  
# 3. 不得进行大规模爬取或对平台造成运营干扰。  
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。   
# 5. 不得用于任何非法或不当的用途。
#   
# 详细许可条款请参阅项目根目录下的LICENSE文件。  
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。  


# -*- coding: utf-8 -*-
# @Author  : relakkes@gmail.com
# @Time    : 2023/12/2 18:44
# @Desc    : bilibili 请求客户端
import asyncio
import json
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import urlencode

import httpx
from playwright.async_api import BrowserContext, Page

from base.base_crawler import AbstractApiClient
from tools import utils

from .exception import DataFetchError
from .help import BilibiliSign


class BilibiliClient(AbstractApiClient):
    def __init__(
            self,
            timeout=10,
            proxies=None,
            *,
            headers: Dict[str, str],
            playwright_page: Page,
            cookie_dict: Dict[str, str],
    ):
        self.proxies = proxies
        self.timeout = timeout
        self.headers = headers
        self._host = "https://api.bilibili.com"
        self.playwright_page = playwright_page
        self.cookie_dict = cookie_dict

    async def request(self, method, url, **kwargs) -> Any:
        async with httpx.AsyncClient(proxies=self.proxies) as client:
            response = await client.request(
                method, url, timeout=self.timeout,
                **kwargs
            )
        data: Dict = response.json()
        if data.get("code") != 0:
            raise DataFetchError(data.get("message", "unkonw error"))
        else:
            return data.get("data", {})

    async def pre_request_data(self, req_data: Dict) -> Dict:
        """
        发送请求进行请求参数签名
        需要从 localStorage 拿 wbi_img_urls 这参数，值如下：
        https://i0.hdslb.com/bfs/wbi/7cd084941338484aae1ad9425b84077c.png-https://i0.hdslb.com/bfs/wbi/4932caff0ff746eab6f01bf08b70ac45.png
        :param req_data:
        :return:
        """
        if not req_data:
            return {}
        img_key, sub_key = await self.get_wbi_keys()
        return BilibiliSign(img_key, sub_key).sign(req_data)

    async def get_wbi_keys(self) -> Tuple[str, str]:
        """
        获取最新的 img_key 和 sub_key
        :return:
        """
        local_storage = await self.playwright_page.evaluate("() => window.localStorage")
        wbi_img_urls = local_storage.get("wbi_img_urls", "") or local_storage.get(
            "wbi_img_url") + "-" + local_storage.get("wbi_sub_url")
        if wbi_img_urls and "-" in wbi_img_urls:
            img_url, sub_url = wbi_img_urls.split("-")
        else:
            resp = await self.request(method="GET", url=self._host + "/x/web-interface/nav")
            img_url: str = resp['wbi_img']['img_url']
            sub_url: str = resp['wbi_img']['sub_url']
        img_key = img_url.rsplit('/', 1)[1].split('.')[0]
        sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]
        return img_key, sub_key

    async def get(self, uri: str, params=None, enable_params_sign: bool = True) -> Dict:
        final_uri = uri
        if enable_params_sign:
            params = await self.pre_request_data(params)
        if isinstance(params, dict):
            final_uri = (f"{uri}?"
                         f"{urlencode(params)}")
        return await self.request(method="GET", url=f"{self._host}{final_uri}", headers=self.headers)

    async def post(self, uri: str, data: dict) -> Dict:
        data = await self.pre_request_data(data)
        json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        return await self.request(method="POST", url=f"{self._host}{uri}",
                                  data=json_str, headers=self.headers)

    async def pong(self) -> bool:
        """get a note to check if login state is ok"""
        utils.logger.info("[BilibiliClient.pong] Begin pong bilibili...")
        ping_flag = False
        try:
            check_login_uri = "/x/web-interface/nav"
            response = await self.get(check_login_uri)
            if response.get("isLogin"):
                utils.logger.info(
                    "[BilibiliClient.pong] Use cache login state get web interface successfull!")
                ping_flag = True
        except Exception as e:
            utils.logger.error(
                f"[BilibiliClient.pong] Pong bilibili failed: {e}, and try to login again...")
            ping_flag = False
        return ping_flag

    async def update_cookies(self, browser_context: BrowserContext):
        cookie_str, cookie_dict = utils.convert_cookies(await browser_context.cookies())
        self.headers["Cookie"] = cookie_str
        self.cookie_dict = cookie_dict

