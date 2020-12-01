
# 说明
仅供学习交流; 个人使用的半成品项目; 

下载慕课网( https://www.imooc.com ) 的金职位视频、图文;

# 使用
## 安装环境 
python 3.7
```
pip install -r requirements.txt
```
安装`wkhtmltopdf`, 并加入path;

## 登录
目前的做法: 浏览器登陆后把cookie复制到`login.py`的对应位置; 

## 下载
下载视频分为两步: 
1. 下载m3u8和key文件
2. 根据m3u8、key下载视频


### 下载m3u8和key文件
金职位包括多个课程(course), 课程下包含多个课时(lesson), 课时可能是视频、图文、考试、练习;    
下载lesson, 使用`JzwLessonM3u8Downloader.py`, 可以参考底部调用实例;   
下载course, 使用`JzwCourseM3u8Downloader.py`, 可以参考底部调用实例;   
下载整个金职位, 可以参考`JzwM3u8Downloader.py`, 金职位的页面结构不同, 无法通用;   

### 根据m3u8、key下载视频
使用`download_m3u8.py`, 可以参考底部的调用实例

### 下载图文类型的lesson
使用`download_md.py`, 可以参考底部的调用实例


# 常见问题
## 解密的分析
参考 [Hellowshuo/imooc-download: imooc 下载脚本](https://github.com/Hellowshuo/imooc-download)
