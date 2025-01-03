# Bilibili-reply-bot:用于爬取给定关键词的bilibili视频评论

# **仅作学习使用**

**本仓库的所有内容仅供学习和参考之用，禁止用于商业用途。任何人或组织不得将本仓库的内容用于非法用途或侵犯他人合法权益。本仓库所涉及的爬虫技术仅用于学习和研究，不得用于对其他平台进行大规模爬虫或其他非法行为。对于因使用本仓库内容而引起的任何法律责任，本仓库不承担任何责任。使用本仓库的内容即表示您同意本免责声明的所有条款和条件。**

## 使用方法

首先，创建虚拟环境并安装相关依赖
``` bash
$ python -m venv venv
$ .venv\Scripts\activate
$ pip install -r requirements.txt
```

运行前可能需要手动安装chromium
```bash
$ playwright install
```

启动
``` bash
$ python ./main
```

第一次使用需要进行二维码登陆，使用bilibili客户端扫描二维码登陆，然后关闭二维码，回到该程序主页面。

该程序会自动记录你的登陆状态，所以再次进行操作时不会需要登陆

## 参考代码

Bilibili的二维码登陆界面参考了项目[MediaCrawler](https://github.com/NanmiCoder/MediaCrawler/)
