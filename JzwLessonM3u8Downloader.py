import requests
import re
from lxml import etree
from enc import n
from Crypto.Cipher import AES
import os
import shutil
import threading
import time

from urls import urls
import tools
from login import Login
import simplejson as json


'''
https://class.imooc.com/lesson/m3u8h5?mid=41093&cid=1330&ssl=1&cdn=aliyun1


'''
# 下载金职位的m3u8、key


class JzwLessonM3u8Downloader(object):
    MEDIA_INFO_JSON = "media_info.json"
    # media_info = None

    def __init__(self, session, course_id, media_id, lesson_name, path):
        self.session = session
        self.course_id = course_id
        self.media_id = media_id
        self.lesson_name = lesson_name
        # 视频保存的绝对路径
        self.path = path
        lesson_name = tools.filename_reg_check(lesson_name)
        self.lesson_path = tools.join_path(self.path, lesson_name) #key、m3u8保存的位置

    def get_lesson_m3u8h5_infos(self):
        '''
        获取课程视频的m3u8的url, 有三种分辨率
        '''
        url = 'https://class.imooc.com/lesson/m3u8h5?mid=%s&cid=%s&ssl=1&cdn=aliyun1' % (
            self.media_id, self.course_id)
        response = self.session.get(url)

        # region 返回结果
        '''
        "#EXTM3U
        # EXT-X-VERSION:3
        # EXT-X-STREAM-INF:PROGRAM-ID=1, BANDWIDTH=512000, RESOLUTION=1280x720
        https://class.imooc.com/video/5f8e7c92255ba9031b531997/high.m3u8?cdn=aliyun1&v3domain=1&play_device=&ssl=1&uid=9494245&hxk_uri=https%3A%2F%2Fclass.imooc.com%2Fvideo%2F5f8e7c92255ba9031b531997%2Fhigh.hxk%3Fu%3D9494245%26timestamp%3D1605922272%26token%3Djiuyeban%253AMWQ0OGQyYmY3YmQwMjVkNmMzZDU0Zjk2ODNjNjJmNjU5M2QzNTcxZA%253D%253D&timestamp=1605922272&token=jiuyeban%3ANmNiYTU5MDUxMTIyNzY0NDZhNTM4MTI0YWJhMDBkNmQ1MzBjOWU1MQ%3D%3D
        # EXT-X-STREAM-INF:PROGRAM-ID=1, BANDWIDTH=384000, RESOLUTION=1280x720
        https://class.imooc.com/video/5f8e7c92255ba9031b531997/medium.m3u8?cdn=aliyun1&v3domain=1&play_device=&ssl=1&uid=9494245&hxk_uri=https%3A%2F%2Fclass.imooc.com%2Fvideo%2F5f8e7c92255ba9031b531997%2Fmedium.hxk%3Fu%3D9494245%26timestamp%3D1605922272%26token%3Djiuyeban%253AMWQ0OGQyYmY3YmQwMjVkNmMzZDU0Zjk2ODNjNjJmNjU5M2QzNTcxZA%253D%253D&timestamp=1605922272&token=jiuyeban%3AN2U0Njc0YjJiNmM3NzgxODVkZDdjZWQ3M2NjZDA4MDViZWQ3ODEzNA%3D%3D
        # EXT-X-STREAM-INF:PROGRAM-ID=1, BANDWIDTH=256000, RESOLUTION=720x480
        https://class.imooc.com/video/5f8e7c92255ba9031b531997/low.m3u8?cdn=aliyun1&v3domain=1&play_device=&ssl=1&uid=9494245&hxk_uri=https%3A%2F%2Fclass.imooc.com%2Fvideo%2F5f8e7c92255ba9031b531997%2Flow.hxk%3Fu%3D9494245%26timestamp%3D1605922272%26token%3Djiuyeban%253AMWQ0OGQyYmY3YmQwMjVkNmMzZDU0Zjk2ODNjNjJmNjU5M2QzNTcxZA%253D%253D&timestamp=1605922272&token=jiuyeban%3AMDA4ZmY3YWIxNzE1Njk1ZTg3YjBmZThkYWUyM2YzMWU4YWUxYzdmOA%3D%3D"
        '''
# endregion
        infos = []
        response_json = response.json()
        for url in n(response_json['data']['info'], '').split("\n")[2:]:
            if '#' in url:
                bindwidth, resolution = re.findall(
                    "BANDWIDTH=(.*?), RESOLUTION=(.*)", url)[0]
            else:
                info = {
                    "bindwidth": bindwidth.strip(),
                    "resolution": resolution.strip(),
                    "url": url.strip()
                }
                infos.append(info)
        return infos

    def download_m3u8(self):
        m3u8_file = os.path.join(self.lesson_path, "vedio.m3u8")
        if not os.path.exists(m3u8_file):
            m3u8_content = self.get_lesson_m3u8()
            with open(m3u8_file, 'w', encoding="utf8") as file:
                file.write(m3u8_content)
        else:
            with open(m3u8_file, "r", encoding="utf8") as f:
                m3u8_content = f.read()

        key_file = os.path.join(self.lesson_path, "key.key")
        if not os.path.exists(key_file):
            key_content = self.get_key(m3u8_content)
            with open(key_file, 'wb') as file:
                file.write(key_content)
        self.download_media_info()

    def download_media_info(self,forceDownload=True):
        media_info_file = os.path.join(self.lesson_path, self.MEDIA_INFO_JSON)
        if  forceDownload or not os.path.exists(media_info_file):
            media_content = self.get_media_info()
            with open(media_info_file, 'w', encoding="utf8") as file:
                file.write(media_content)

    def get_key(self, m3u8_content):
        try:
            source = m3u8_content
            url = re.search(r'URI="(.+)"', source).group(1)
            response_json = self.session.get(url).json()
            encode_info = response_json["data"]["info"]
            return n(encode_info, True)
        except Exception as ex:
            # raise ex,"get_key error: "+ex.message
            msg = "traceback ", "get_key error: "+ex.message, str(ex)
            return msg

    def get_lesson_m3u8(self):
        url = self.get_lesson_m3u8h5_infos()[0]['url']
        response_json = self.session.get(url).json()
        # if(len(resp))< 100:
        #     msg = "get_lesson_m3u8: 返回数据过短: "+resp
        #     raise RuntimeError(msg)
        # data = json.loads(resp)
        encode_info = response_json["data"]["info"]
        return n(encode_info)

    def get_media_info(self):
        url = 'https://class.imooc.com/lesson/ajaxmediainfo?mid=%s' % (
            self.media_id)
        resonse = self.session.get(url)
        data = resonse.text
        # data = data.replace("\\/", "/")  # 用'/'替换'\/'
        # data = data.encode().decode('unicode_escape') #这种做法似乎会多清理\
        data_json = json.loads(data)
        data_new = json.dumps(data_json, ensure_ascii=False, indent=2)
        return data_new



if __name__ == "__main__":
    # https://class.imooc.com/lesson/m3u8h5?mid=41093&cid=1330&ssl=1&cdn=aliyun1
    session = Login().login()
    save_path = tools.join_path(tools.main_path(), "下载")

    course_id = 1222
    media_id = 30406
    lesson_name = "lesson_test"
    downloader = JzwLessonM3u8Downloader(
        session, course_id, media_id, lesson_name, save_path)
    # downloader.download_m3u8()
    # data = downloader.get_lesson_m3u8h5_infos()
    downloader.get_media_info()

