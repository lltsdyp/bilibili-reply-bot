# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。


# 基础配置
PLATFORM = "bilibili"
LOGIN_TYPE = "qrcode"  # qrcode or phone or cookie
COOKIES = ""

# 设置为True不会打开浏览器（无头浏览器）
# 设置False会打开一个浏览器
# 链接失败可设置为False进行检查
HEADLESS = True

# 是否保存登录状态
SAVE_LOGIN_STATE = True

# 用户浏览器缓存的浏览器文件配置
USER_DATA_DIR = "%s_user_data_dir"  # %s will be replaced by platform name


# 爬取一级评论的数量控制(单视频/帖子)
CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = 60
# 爬取搜索页的页数（一般来说页数*20=视频数）
CRAWLER_MAX_SEARCH_PAGE_COUNT = 8
# 处理每页搜索结果的线程数
CONCURRENCY_THREADS_PER_PAGE = 2
# 总的线程数（自动计算）
MAX_CONCURRENCY_NUM = CONCURRENCY_THREADS_PER_PAGE*CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES

# 限制搜索范围为最近多少天（为0不限制）
DAY_BEFORE=0
