# 把创建目录的逻辑抽出来， 做一个数据结构
# 把User-agent 逻辑隐藏起来，像get_soup一样
# 尝试用多线程和Queue
# 如果我要发布，requirements该如何生成呢？
# 下载器的骨架是什么，是URL啊，URL是贯穿全局的线索，
# 所有逻辑，都是围绕着如何得到URL，如何下载URL，如何保存URL到某个位置
# 关于如何避免被反爬，可以通过增加中间件，或者直接在某一个步骤中，从而把复杂性隐藏起来
# 比如小说下载器中，有以下复杂性，编码复杂性，可能有不同的编码，我把编码复杂性直接塞到get_soup里，外面完全看不出
# 比如获得正文的复杂性，有不同的css选择器需要尝试，我单独抽出来一个函数parse_soup_text，把这个函数嵌入download_url中。
USER_AGENT_LIST = [ 
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    ]
import logging
import random
import sys
import time
from pathlib import Path
from typing import Dict

import requests_html
from requests_html import HTMLSession

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
COMIC_URL = 'https://www.caomeng.cc/neihanmanhua/370.html'
COMIC_NAME = '默认漫画名'
ChapterNameTable: Dict[str, str] = dict()
SLEEP_SEC = 5

session = HTMLSession()
def get_r(url):
    user_agent = random.choice(USER_AGENT_LIST)
    header = {"user-agent": requests_html.user_agent()}
    r = session.get(url=url, headers=header)
    return r

def get_chapters_url():
    r = get_r(COMIC_URL)
    lanmu = r.html.find("#sortWrap", first=True)
    titles = [item.attrs['title'] for item in lanmu.find("a")]
    
    links = lanmu.absolute_links
    for link, title in zip(links, titles):
        ChapterNameTable[link] = title
    return links
    

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
        for page_num, url_page in enumerate(get_url_pages(url_chapter)):
            logging.debug(f"trying to download {url_page}")
            download_page(url_page, chapter_name, page_num)
    except Exception as e:
        logging.debug(e)
        pass

def download_page(url_page, chapter_name, page_num):
    r = get_r(url_page)
    img = r.html.find("#mhxxBimg > p:nth-child(1) > a:nth-child(1) > img:nth-child(1)")[0]
    # 可以检查元素，然后复制CSS选择器来得到
    # print(img)
    img_url = img.attrs['src']
    r = get_r(img_url)
    img_data = r.html.raw_html
    save_img_to(img_data, chapter_name, page_num)

def save_img_to(img_data, chapter_name, page_num):
    dir_path = Path(f"{COMIC_NAME}/{chapter_name}")
    file_path = Path(f"{COMIC_NAME}/{chapter_name}/{page_num:03d}.jpg")
    dir_path.mkdir(exist_ok=True, parents=True)
    file_path.touch(exist_ok=True)
    file_path.write_bytes(img_data)
    logging.debug(f"save to {file_path}")
    logging.info(f"sleeping....")
    time.sleep(SLEEP_SEC)





def download_comic():
    global COMIC_NAME
    r = get_r(COMIC_URL)
    COMIC_NAME = r.html.find('title', first=True).text
    for chapter_url in get_chapters_url():
        chapter_name = ChapterNameTable[chapter_url]
        download_chapter(chapter_url, chapter_name)
    logging.info(f"Task {COMIC_NAME} Done!")



# with open('index.html') as f:
#     doc = f.read()

# from requests_html import HTML

# html = HTML(html=doc)




download_comic()
    





# 其实本来这个很容易写的，毕竟已经写过一次，但是我为了玩点花样，
# 学了requests-html库，还有pathlib的用法，以及如何使用pytest,包括调教spacemacs,所以才花了很多时间
# 我需要关心的细节是什么？ pytest首先是如何使用，如何调用，其次是发现与匹配，会发现什么样的文件文件中的哪些函数




# 现在还有一个问题，尾大不掉，代码已经很多了，我必须编写一个测试文件，不然真的不行了。
