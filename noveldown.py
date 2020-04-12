import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
TO_DOWNLOAD: List = []
NOVEL_CONTENT_URL = 'http://www.shuquge.com/txt/293/index.html'
BOOK_NAME = None
DECODE = ['gbk', 'utf-8']

def parse_soup_content(soup: BeautifulSoup):
    global TO_DOWNLOAD, BOOK_NAME
    # soup = BeautifulSoup(f, 'html.parser')
    BOOK_NAME = soup.find("title").text
    ele = soup.find("div", class_="listmain")
    items = ele.find_all("a")
    for item in items:
        url = item['href']
        title = item.text
        TO_DOWNLOAD.append((url, title))
        logging.debug(f"append {url},{title}")


def parse_soup_text(soup):
    res = soup.find(id=re.compile('content')).text
    logging.debug(f"download text: {res[0:10]}")
    return res

def get_soup(url):
    r = requests.get(url, timeout=5)
    for decode_method in DECODE:
        try:
            r_text = r.text.encode("latin1").decode(decode_method)
        except UnicodeDecodeError:
            continue
        else:
            break
    soup = BeautifulSoup(r_text, 'html.parser')
    return soup

# 跟漫画不一样，漫画必须分集存放，不然根本没法看， 小说则相反，必须把不同章节整合成一本。
# 不要急着做抽象，不得不抽象时，才抽象，过早优化时万恶之源


def download_url(base_url, chapter_url):
    url = base_url + "/" + chapter_url 
    logging.debug(f"dealing {url}")
    soup = get_soup(url)
    return parse_soup_text(soup)


def download_book():
    base_url = "/".join(NOVEL_CONTENT_URL.split("/")[:-1])
    soup = get_soup(NOVEL_CONTENT_URL)
    parse_soup_content(soup)
    with open(BOOK_NAME+".txt", "w") as f:
        for chapter_url, title in TO_DOWNLOAD:
            text = download_url(base_url, chapter_url)
            f.write(title+"\n\n")
            f.write(text)

    logging.info(f"Task {BOOK_NAME} Done!")

download_book()






