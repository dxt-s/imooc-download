# -*- coding: utf-8 -*-
import pickle,requests,os
from urls import urls
from lxml import etree
import tools

# 自动登录类
class Login(object):
    def login(self):
        # if session:
        #     return session
        session = requests.Session()
        session.headers  = self.get_header()
        self.is_login_avalid(session)
        return session

    def get_header(self):    
        # java工程师
        cookie1 = '''
        '''

        # 大前端：前端全栈加强版！前端全栈+全周期+多端（升级Vue3.0）
        cookie2 = '''
        '''

        # Java架构师体系课：跟随千万级项目从0到100全过程高效成长
        cookie3 = '''    
        '''

        cookie = cookie1

        cookie = cookie.strip()
        header_raw = '''
# Host: www.imooc.com
Connection: keep-alive
Pragma: no-cache
Cache-Control: no-cache
Accept: text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36
X-Requested-With: XMLHttpRequest
# Sec-Fetch-Site: same-origin
# Sec-Fetch-Mode: cors
# Sec-Fetch-Dest: empty
# Referer: https://www.imooc.com/
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7
Cookie: %s
        ''' % (cookie)
        header = {}
        for line in header_raw.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            name,value = line.split(":",maxsplit=1)
            header[name.strip()] = value.strip()
        return header

    def is_login_avalid(self,session):
        resp = session.get(urls['user_info'])
        text = resp.text
        if '"result":0,"data":' in text: 
            print('cookies登陆成功')
            return session
        else:
            print('cookies 登陆失败')
            return False

if __name__ == '__main__':
    login = Login()
    login.login()