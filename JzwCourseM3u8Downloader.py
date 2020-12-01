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
from JzwLessonM3u8Downloader import JzwLessonM3u8Downloader 

class JzwCourseM3u8Downloader(object):
    COURSE_INFO_JSON = "course_info.json"
    root_path = None  # 以course_name为根目录
    course_info_json_path = None

    def __init__(self, session, course_url, path,course_name=None):
        """[summary]

        Args:
            session ([object]): requests已登录的session
            course_url ([string]): 课程url, 如: https://class.imooc.com/course/1330
            path ([string]): 保存的绝对路径, 在这个目录下创建course_name文件夹, 以course_name文件夹为root_path
        """
        self.session = session
        self.course_url = course_url
        self.course_id = int(course_url.split("/")[-1])
        self.path = path
        if course_name:
            self.root_path = tools.join_path(self.path,course_name)

    def download_m3u8(self):
        course_info = self.get_course_info(forceDownload=True)
        course_name = course_info["title"]
        for chapter in course_info['chapters']:
            chapter_name = chapter['chapter_title']
            for lesson in chapter["lessons"]:
                lesson_name = lesson['lesson_name']
                media_id = lesson['media_id']
                lesson_type = lesson['type_icon']

                course_name = tools.filename_reg_check(course_name)
                chapter_name = tools.filename_reg_check(chapter_name)
                lesson_name = tools.filename_reg_check(lesson_name)

                chapter_path = tools.join_path(
                    self.root_path, chapter_name)
                tools.check_or_make_dir(self.root_path)

                lesson_path = tools.join_path(chapter_path, lesson_name)
                tools.check_or_make_dir(lesson_path)
                print(lesson_path)
                downloader = JzwLessonM3u8Downloader(
                        self.session, self.course_id, media_id, lesson_name, chapter_path)
                if "-video" in lesson_type:
                    downloader.download_m3u8()
                else:
                    downloader.download_media_info()

    def get_course_html(self):
        # html = open("Java常量与变量-慕课网就业班.html", encoding="utf8").read()
        response = self.session.get(self.course_url)
        html = response.text
        return html

    def get_aid_infos(self, html):
        """辅助材料信息

        Args:
            html ([type]): [description]

        Returns:
            [type]: 返回数组
        """
        html_xpath = etree.HTML(html)
        # material_xpath = html_xpath.xpath('//h2[contains(text(),"辅助材料")]/parent::div')[0]
        a_xpath_list = html_xpath.xpath("//ul[@class='aid-sheet']/li/a")
        infos = []
        for a_xpath in a_xpath_list:
            label = a_xpath.xpath("span[@class='label']/text()")[0].strip()
            text = a_xpath.xpath("span[@class='text']/text()")[0].strip()
            href = a_xpath.attrib['href']
            info = dict(
                label=label,
                text=text,
                href=href
            )
            infos.append(info)
        return infos

    def get_course_info(self, forceDownload=False):
        """获取课程信息, 解析章节目录
        课程(course)有多个章节(chapter), 章节有多个课时(lesson)
        格式参考course_info.json

        Args:
            url ([type]): course的url, 如: https://class.imooc.com/course/1330

        Returns:
            [type]: [description]
        """

        html = self.get_course_html()
        html_xpath = etree.HTML(html)

        title = html_xpath.xpath("/html/body//h1/a/text()")[0].strip()
        title = tools.filename_reg_check(title)
        if not self.root_path:
            self.root_path = tools.join_path(self.path, title)
        tools.check_or_make_dir(self.root_path)
        self.course_info_json_path = tools.join_path(
            self.root_path, self.COURSE_INFO_JSON)
        if not forceDownload and os.path.exists(self.course_info_json_path):
            with open(self.course_info_json_path, "r", encoding="utf8") as f:
                content = f.read()
                if content:
                    info = json.loads(content)
                    return info

        introduction = html_xpath.xpath('//p[@class="con"]/text()')[0].strip()
        chapters_xpath = html_xpath.xpath(
            '//div[contains(@class,"chapter-item")]')
        chapter_infos = []
        for chapter_ in chapters_xpath:
            chapter_title = chapter_.xpath("h2/text()")[0].strip()
            lessons = []
            for a_xpath in chapter_.xpath('ul/li/a'):
                names = a_xpath.xpath(
                    'span[not(contains(@class,"finished"))]/text()')
                lesson_name = ''.join(names)
                lesson_name = lesson_name.replace(
                    " ", "").replace("\n", "").strip()
                # 图标的类型, 可以用来表示课程类型, 视频、练习、图文等等
                type_icon = a_xpath.xpath('i/@class')[0]
                href = a_xpath.xpath('@href')[0]
                # href: lesson/1330#mid=41093
                # 1330是course_id, media_id相当于lesson_id
                media_id = href.split("=")[-1]
                media_id = int(media_id)
                lesson = dict(
                    lesson_name=lesson_name,
                    href=href,
                    media_id=media_id,
                    type_icon=type_icon
                )
                lessons.append(lesson)
            chapter_info = {
                "chapter_title": chapter_title,
                "lessons": lessons
            }
            chapter_infos.append(chapter_info)
        aid_infos = self.get_aid_infos(html)
        data = dict(
            title=title,
            introduction=introduction,
            course_id=self.course_id,
            chapters=chapter_infos,
            aid_infos=aid_infos
        )
        data_json = json.dumps(data, ensure_ascii=False, indent=2)
        with open(self.course_info_json_path, "w", encoding="utf8") as f:
            f.write(data_json)
        return data


if __name__ == "__main__":
    # https://class.imooc.com/lesson/m3u8h5?mid=41093&cid=1330&ssl=1&cdn=aliyun1
    session = Login().login()
    save_path = tools.join_path(tools.main_path(), "下载")

    course_url = "https://class.imooc.com/course/1330"
    courseM3u8Downloader = JzwCourseM3u8Downloader(
        session, course_url, save_path)
    # courseM3u8Downloader.get_course_info(forceDownload=True)
    courseM3u8Downloader.download_m3u8()