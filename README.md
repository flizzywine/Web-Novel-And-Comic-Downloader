# Web-Novel-And-Comic-Downloader
# 网络小说与漫画下载器


## 小说下载器
基本用法:

`python noveldown.py book_url`

指定元素选择器:

`python noveldown.py book_url --chapters_selector '#list' --text_selector '#content'`

## 漫画下载器

`python comicdown.py comic_url`

## 特色
### 简便
最少只需要输入一个URL，起始URL即可。
### 避开反爬
通过改变User-Agent，降低GET频率来一定程度上避开反爬, 重新下载空白章节
### 增量下载
中断后不需要重新下载
### 自动命名
自动提取的章节标题
