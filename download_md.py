# encoding=utf-8


import requests
import sys
import os
import re
from Crypto.Cipher import AES

import time
import threading
from queue import Queue
from threading import Thread
import tools
import simplejson as json

import pdfkit

"""
下载图文类型的lesson, 保存为pdf
"""

def download(file):
    if "大家学习中有疑问该怎么办" in file: 
        return 
    with open(file, 'r', encoding="utf8") as f:
        file_content = f.read()
    data = json.loads(file_content)
    media_info = data['data']['media_info']
    if not "content" in media_info:
        print("not exist md")
        return
    
    print(file)
    md = media_info["content"]
    html = media_info['content_md']
    html = html.replace('src="//','src="http://') #有些图片地址少了http, 直接以//开头

    current_path = tools.get_dir_path(file)
    parent_path = tools.get_parent_dir_path(file)
    lesson_name = os.path.basename(current_path)

    md_path = tools.join_path(current_path, lesson_name+".md")
    if not os.path.exists(md_path):
        with open(md_path, "w", encoding="utf8") as f:
            f.write(md)

    pdf_path = tools.join_path(parent_path, lesson_name+".pdf")
    if not os.path.exists(pdf_path):
        try:
            pdfkit.from_string(html, pdf_path, options={
                "--encoding": "utf8"
            })            
        except OSError as ex:
            print("OSError",file)
            pass
        except Exception as ex:
            print("Exception",file)
            pass
            


def get_file_list(base_dir):
    """返回文件列表

    Args:
        base_dir ([type]): [description]

    Returns:
        [type]: [description]
    """
    list = []
    for path, dir_list, file_list in os.walk(base_dir):
        # 文件名按照数字大小排序
        # dir_list.sort(key=lambda n: n.split(".")[0].zfill(6))
        for file in file_list:
            list.append(os.path.join(path, file))
    return list


def download_all(base_dir):
    '''
    下载base_dir及子目录下的文件;
    '''
    file_list = get_file_list(base_dir)
    for file in file_list:
        if file.endswith("media_info.json"):
            download(file)


def download_main():
    '''
    单线程下载的入口
    '''
    reverse = False
    arg1 = ""
    arg2 = ""
    if len(sys.argv) >= 2:
        arg1 = sys.argv[1]
    if len(sys.argv) >= 3:
        arg2 = sys.argv[2]

    dir = ""
    reverse = False
    if arg1:
        print("dir "+arg1)
        dir = arg1
    if arg2 == "1":
        print("reverse true")
        reverse = True
    download_all(dir.decode("gbk"), reverse)


queue = Queue()


def download_multi():
    while True:
        dir = queue.get()
        print('thread: %s, dir: %s' % (threading.current_thread(), dir))
        download(dir)
        queue.task_done()
        if queue.empty():
            break


def download_all_multi(base_dir, thread_count=5):
    dir_list = get_dir_list(base_dir)
    for dir in dir_list:
        queue.put(dir)
    for i in range(thread_count):
        t = Thread(target=download_multi)
        t.daemon = True  # 设置线程daemon  主线程退出，daemon线程也会推出，即时正在运行
        t.start()
    queue.join()


def download_main_multi():
    '''
    多线程下载的入口
    '''
    if len(sys.argv) >= 2:
        dir = sys.argv[1]
    else:
        print("缺少dir参数")
        return
    download_all_multi(dir.decode("gbk"), 3)


if __name__ == "__main__":
    path = tools.join_path(tools.main_path(), "下载")
    download_all(path)

