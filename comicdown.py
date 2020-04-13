# 把创建目录的逻辑抽出来， 做一个数据结构
# 把User-agent 逻辑隐藏起来，像get_soup一样
# 尝试用多线程和Queue
# 如果我要发布，requirements该如何生成呢？
# 下载器的骨架是什么，是URL啊，URL是贯穿全局的线索，
# 所有逻辑，都是围绕着如何得到URL，如何下载URL，如何保存URL到某个位置
# 关于如何避免被反爬，可以通过增加中间件，或者直接在某一个步骤中，从而把复杂性隐藏起来
# 比如小说下载器中，有以下复杂性，编码复杂性，可能有不同的编码，我把编码复杂性直接塞到get_soup里，外面完全看不出
# 比如获得正文的复杂性，有不同的css选择器需要尝试，我单独抽出来一个函数parse_soup_text，把这个函数嵌入download_url中。

import json
import logging
import random
import sys
import time
from pathlib import Path
from typing import Dict

import requests_html
from requests_html import HTMLSession

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
COMIC_URL = "https://www.caomeng.cc/neihanmanhua/370.html"
CHAPTER_SELECTOR = "#sortWrap"
PAGE_SELECTOR = "#mhxxBimg > p:nth-child(1) > a:nth-child(1) > img:nth-child(1)"
COMIC_NAME = '默认漫画名'
ChapterNameTable: Dict[str, str] = dict()
SLEEP_SEC = 5
session = HTMLSession()
USER_AGENT_LIST = None

with open('user-agents.json') as f:
    USER_AGENT_LIST = json.load(f)['user-agents']
    

def get_r(url):
    user_agent = random.choice(USER_AGENT_LIST)
    header = {"user-agent": requests_html.user_agent()}
    r = session.get(url=url, headers=header)
    return r

def get_chapters_url():
    r = get_r(COMIC_URL)
    lanmu = r.html.find(CHAPTER_SELECTOR, first=True)
    links_and_titles = [(item.attrs['href'], item.attrs['title']) for item in lanmu.find("a")]
    
    abs_links = lanmu.absolute_links
    for abs_link in abs_links:
        for link, title in links_and_titles:
            if abs_link.endswith(link):
                ChapterNameTable[abs_link] = title
                break

    return abs_links

# 现在能得到章节目录的链接，但是能不能自动得到每一章的具体页数，而不是辛辛苦苦找来找去
# 能不能自动无限延长，如果Error，就说明这一章结束了



def get_url_pages(url_chapter):
    base = ".".join(url_chapter.split(".")[:-1])
    for i in range(1, 100):
        if i == 1:
            yield url_chapter
        else:
            yield f"{base}_{i}.html"

def download_chapter(url_chapter, chapter_name):
    try:
        for page_num, url_page in enumerate(get_url_pages(url_chapter),start=1):
            file_path = Path(f"{COMIC_NAME}/{chapter_name}/{page_num:03d}.jpg")
            if file_path.exists():
                logging.info(f"{file_path} already exists, skip")
            else:
                logging.info(f"trying to download {url_page}")
                download_page(url_page, chapter_name, page_num)
    except Exception as e:
        logging.info(e)
        # 我写这段代码，是无心插柳，
        # 没想到完美地解决了一个意想不到地bug,那就是，即使遇到下载失败，程序也不会停止
        # 但是也有一个问题，就是错误恢复的粒度太大，是以章节为单位进行的， 我完全可以把粒度控制到页为单位
        pass


def download_page(url_page, chapter_name, page_num):
    r = get_r(url_page)
    try:
        img = r.html.find(PAGE_SELECTOR)[0]
    except Exception as e:
        # 我之前看到的调试原则，把错误控制在最小范围内
        # 这一段的错误是因为要求的page_num 太大了，所以得不到任何元素
        # 我翻了个错，没有原地控制住错误, 在get_url_pages里的错误，被传入了这里，不利于错误的定位
        # 因为我是作者，所以我知道怎么找，如果换个人来，就直接懵逼了, 最好写一个中间件，判断有没有超出，
        raise Exception(f"fail to get img ele: {e}")
    # 可以检查元素，然后复制CSS选择器来得到
    # print(img)
    try:
        img_url = img.attrs['src']
        r = get_r(img_url)
    except Exception as e:
        logging.info(f"fail to get img src: {url_page}, {chapter_name}, {page_num}: {e}")
        return 
    try:
        img_data = r.html.raw_html
    except Exception as e:
        logging.info(f"fail to get raw data: {url_page}, {chapter_name}, {page_num}: {e}")
        return
    try:
        save_img_to(img_data, chapter_name, page_num)
    except Exception as e:
        logging.info(f"fail to save: {url_page}, {chapter_name}, {page_num}: {e}")
        return
    else:
        logging.info(f"sleeping....")
        time.sleep(SLEEP_SEC)



def save_img_to(img_data, chapter_name, page_num):
    dir_path = Path(f"{COMIC_NAME}/{chapter_name}")
    file_path = Path(f"{COMIC_NAME}/{chapter_name}/{page_num:03d}.jpg")
    dir_path.mkdir(exist_ok=True, parents=True)
    file_path.touch(exist_ok=False)
    file_path.write_bytes(img_data)
    logging.info(f"save to {file_path}")



def download_comic():
    global COMIC_NAME
    r = get_r(COMIC_URL)
    COMIC_NAME = r.html.find('title', first=True).text
    for chapter_url in get_chapters_url():
        chapter_name = ChapterNameTable[chapter_url]
        download_chapter(chapter_url, chapter_name)
    logging.info(f"Task {COMIC_NAME} Done!")



if '__main__' == __name__:
    download_comic()
    # get_chapters_url()

    # print(ChapterNameTable)

    





# 其实本来这个很容易写的，毕竟已经写过一次，但是我为了玩点花样，
# 学了requests-html库，还有pathlib的用法，以及如何使用pytest,包括调教spacemacs,所以才花了很多时间
# 我需要关心的细节是什么？ pytest首先是如何使用，如何调用，其次是发现与匹配，会发现什么样的文件文件中的哪些函数

# 现在还有一个问题，尾大不掉，代码已经很多了，我必须编写一个测试文件，不然真的不行了

# 好，现在有一个问题，我们成功地下载了一部分内容，如何增量下载，第二次把第一次成功地部分忽略掉，直接下载没有下载地部分？
