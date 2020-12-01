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
from JzwCourseM3u8Downloader import JzwCourseM3u8Downloader


class JzwM3u8Downloader(object):
    JZW_INFO_JSON = "jzw_info.json"
    root_path = None  # 以金职位目录为根目录

    def __init__(self, session, jzw_url, path, jzw_name=""):
        self.session = session
        self.jzw_url = jzw_url
        self.path = path
        if jzw_name:
            jzw_name = tools.filename_reg_check(jzw_name)
            self.root_path = tools.join_path(self.path, jzw_name)

    def download_m3u8(self):
        jzw_info = self.get_jzw_info()
        jzw_title = jzw_info["jzw_title"]
        stage_infos = jzw_info["stage_infos"]
        for stage_info in stage_infos:
            state_title = stage_info["state_title"]
            week_infos = stage_info["week_infos"]
            for week_info in week_infos:
                week_title = week_info["week_title"]
                course_infos = week_info["course_infos"]
                for course_info in course_infos:
                    course_name = course_info['course_name']
                    course_url = course_info['href']
                    index = course_info['index']

                    jzw_title = tools.filename_reg_check(jzw_title)
                    state_title = tools.filename_reg_check(state_title)
                    week_title = tools.filename_reg_check(week_title)
                    course_name = tools.filename_reg_check(course_name)

                    course_path = tools.join_path(
                        self.path, jzw_title, state_title, week_title)
                    tools.check_or_make_dir(course_path)
                    # 有些课程是考试, url是/exam/123
                    if "course/" in course_url:
                        downloader = JzwCourseM3u8Downloader(
                            self.session, course_url, course_path, str(index)+". "+course_name)
                        downloader.download_m3u8()

    def get_html(self):
        # html = open("资料\Java 工程师2020版-慕课网就业班.html", encoding="utf8").read()
        response = self.session.get(self.jzw_url)
        html = response.text
        return html

    def get_jzw_info(self, forceDownload=False):
        html = self.get_html()
        html_xpath = etree.HTML(html)
        jzw_title = html_xpath.xpath(
            '//h1[@class="stage-title"]/a/text()')[0].strip()

        jzw_title = tools.filename_reg_check(jzw_title)
        if not self.root_path:
            self.root_path = tools.join_path(self.path, jzw_title)
        tools.check_or_make_dir(self.root_path)
        self.jzw_info_json_path = tools.join_path(
            self.root_path, self.JZW_INFO_JSON)
        if not forceDownload and os.path.exists(self.jzw_info_json_path):
            with open(self.jzw_info_json_path, "r", encoding="utf8") as f:
                content = f.read()
                if content:
                    info = json.loads(content)
                    return info

        stages_xpath = html_xpath.xpath(
            '//div[contains(@class,"stage-box js-stage-box")]')
        stage_infos = []
        jzw = dict(
            jzw_title=jzw_title,
            stage_infos=stage_infos
        )
        for stage_xpath in stages_xpath:
            state_title = stage_xpath.xpath(
                'div[contains(@class,"stage-title")]/text()')[0].strip()
            weeks_xpath = stage_xpath.xpath(
                'div/div[contains(@class,"week-box")]')
            week_infos = []
            stage_info = dict(
                state_title=state_title,
                week_infos=week_infos
            )
            stage_infos.append(stage_info)
            for week_xpath in weeks_xpath:
                week_title = week_xpath.xpath(
                    'div[contains(@class,"week-title")]/text()')[0].strip()
                courses_xpath = week_xpath.xpath(
                    'div[contains(@class,"class-box")]/a[@class="class def"]')
                course_infos = []
                week_info = dict(
                    week_title=week_title,
                    course_infos=course_infos
                )
                week_infos.append(week_info)
                index = 0
                for course_xpath in courses_xpath:
                    course_name = course_xpath.xpath(
                        'div/div[@class="class-name"]/text()')[0].strip()
                    href = "https://class.imooc.com" + \
                        course_xpath.attrib['href']  # /course/1330
                    course_id = int(href.split("/")[-1])
                    index += 1
                    course_info = dict(
                        course_name=course_name,
                        href=href,
                        course_id=course_id,
                        index=index
                    )
                    course_infos.append(course_info)
        data_json = json.dumps(jzw, ensure_ascii=False, indent=2)
        with open(self.jzw_info_json_path, "w", encoding="utf8") as f:
            f.write(data_json)
        return jzw


if __name__ == "__main__":
    session = Login().login()
    save_path = tools.join_path(tools.main_path(), "下载")

    url = "https://class.imooc.com/sc/83/learn"
    jzwM3u8Downloader = JzwM3u8Downloader(
        session, url, save_path, "Java 工程师2020版")
    jzwM3u8Downloader.download_m3u8()
