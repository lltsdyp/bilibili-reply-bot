import time
import config
import datetime

result=[]

async def batch_add_video_replies(video_id,replies):
    if not replies:
        return
    for reply in replies:
        reply_time = datetime.datetime.fromtimestamp(reply['ctime'])
        current_time = datetime.datetime.now()
        delta = current_time - reply_time

        if config.DAY_BEFORE==0 or delta.days<config.DAY_BEFORE:
            result.append({
                '评论内容': reply['content']['message'],
                '性别': reply['member']['sex'],
                '点赞数量': reply['like'],
                '回复时间': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reply['ctime']))
            })
