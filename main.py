import requests
from bs4 import BeautifulSoup
import sys
import re
import os
import argparse
import time

BODY_SELECTOR = None
OUTPUT_FILENAME = None
TITLE_SELECTOR = None
ADD_DIR = False
ENCODING = None


def get_title_selector(soup):
    global TITLE_SELECTOR
    if TITLE_SELECTOR:
        return
    candidates = ['h1', 'h2', 'title']
    def better_title(a):
        if re.search(r'第.*[章节回卷集]', a[0]):
            return 0
        if re.search(r'[0-9]+', a[0]):
            return 1
        if re.search(r'[一二三四五六七八九十]+', a[0]):
            return 1
        else:
            return 2

    titles = []
    for candidate in candidates:
        try:
            title = (soup.select(candidate)[0].text, candidate)
            titles.append(title)
        except:
            pass
    titles.sort(key=better_title)
    
    if len(titles) > 0:
        TITLE_SELECTOR = titles[0][1]
        return

    raise RuntimeError("No title found, please specify title_selector")


def get_body_selector(soup):
    global BODY_SELECTOR
    if BODY_SELECTOR:
        return
    for div in soup.find_all('div'):
        try:
            for cls in div['class']:
                
                if 'content' in cls or 'text' in cls:
                    BODY_SELECTOR = "."+cls
                    return
        except:
            pass
    for div in soup.find_all('div'):
        try:
            id = div['id']
            if 'content' in id or 'text' in id:
                BODY_SELECTOR = "#"+id
                return
        except:
            pass

    raise RuntimeError("No body text found, please specify body_selector")


def init_config(urls):
    global BODY_SELECTOR, OUTPUT_FILENAME, ADD_DIR, TITLE_SELECTOR, ENCODING
    for url in url_iter(urls):
        res = requests.get(url, timeout=None)
        print(res.encoding)
        if res.encoding == 'utf-8':
            ENCODING = 'utf-8'
        else:
            ENCODING = 'gbk'

        t = res.text.encode(res.encoding).decode(ENCODING, 'ignore')

        soup = BeautifulSoup(t, 'html.parser')

        if OUTPUT_FILENAME is None:
            OUTPUT_FILENAME = soup.select('title')[0].text

        get_title_selector(soup)
        title = soup.select(TITLE_SELECTOR)[0].text
        m = re.search("第.*[章回节卷]", title)
        if not m:
            ADD_DIR = True

        get_body_selector(soup)
        break

    print(
        f"configure success.\nout:{OUTPUT_FILENAME}, title:{TITLE_SELECTOR}, body:{BODY_SELECTOR}, dir:{ADD_DIR}, encoding:{ENCODING}")


def get_content(content_url, i=1):
    # time.sleep(10)
    global OUTPUT_FILENAME, BODY_SELECTOR
    try:
        res = requests.get(content_url, timeout=5)
    except KeyboardInterrupt:
        exit(1)
    except:
        return None
    try:
        t = res.text.encode(res.encoding).decode(ENCODING, 'ignore')
    except:
        t = res.text
        
    soup = BeautifulSoup(t, 'html.parser')

    title = soup.select(TITLE_SELECTOR)[0].text

    if ADD_DIR:
        title = f"第{i}章 " + title

    bodies = soup.select(BODY_SELECTOR)

    content = ""
    for part in bodies:
        content += part.text

    both = title + '\n' + content + '\n\n'
    return both


def download(urls):
    init_config(urls)
    with open(OUTPUT_FILENAME + '.txt', 'w+') as f:
        for i, url in enumerate(url_iter(urls), start=1):
            print(url)
            data = get_content(url, i)
            while data is None:
                data = get_content(url, i)
                print(f'retry get {url}')
            f.write(data)

    print('\nDONE')


def url_iter(urls):
    for url in urls:
        m = re.search(r'\[(.*)\-(.*)\]', url)
        if not m:
            yield url
            continue
        start, end = int(m.group(1)), int(m.group(2))
        for i in range(start, end+1):
            url2 = re.sub(r"\[.*\]", str(i), url)
            yield url2


if __name__ == '__main__':
    urls = [
        "https://www.qihaoqihao.com/15/15543/[2704178-2704182].html "
    ]
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", nargs='+',
                        default=urls)
                                    
    parser.add_argument('--body')
    parser.add_argument('--title')

    args = parser.parse_args()
    if args.body:

        BODY_SELECTOR = args.body
    if args.title:
        TITLE_SELECTOR = args.title
    download(args.urls)




