import requests
from bs4 import BeautifulSoup
import sys
import re
import os
import argparse


BODY_SELECTOR = None
OUTPUT_FILENAME = None
TITLE_SELECTOR = None
ADD_DIR = False
ENCODING = None

def get_body_selector(soup):
    global BODY_SELECTOR
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
            for id in div['id']:
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
        if res.encoding == 'utf-8':
            ENCODING = 'utf-8'
        else:
            ENCODING = 'gbk'
            
        t = res.text.encode(res.encoding).decode(ENCODING, 'ignore')
        
        soup = BeautifulSoup(t, 'html.parser')

        if OUTPUT_FILENAME is None:
            OUTPUT_FILENAME = soup.select('title')[0].text
        try:
            title = soup.select('h1')[0].text
            TITLE_SELECTOR = 'h1'
        except:
            title = soup.select('title')[0].text
            TITLE_SELECTOR = 'title'
            
        m = re.search("第.*[章回节卷]", title)
        if not m:
            ADD_DIR = True
            
        get_body_selector(soup)
        break

    print(f"configure success.\nout:{OUTPUT_FILENAME}, title:{TITLE_SELECTOR}, body:{BODY_SELECTOR}, dir:{ADD_DIR}, encoding:{ENCODING}")


def get_content(content_url, i=1):
    global OUTPUT_FILENAME, BODY_SELECTOR
    try:
        res = requests.get(content_url, timeout=5)
    except:
        return None

    t = res.text.encode(res.encoding).decode(ENCODING, 'ignore')

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
        # print(m.group(1), m.group(2))
        start, end = int(m.group(1)), int(m.group(2))
        for i in range(start, end+1):
            url2 = re.sub(r"\[.*\]", str(i), url)
            yield url2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", nargs='+', default=[
                        'https://www.sjks88.com/gudaiyanqing/22247_[85-223].html'])
    parser.add_argument('--body')
    parser.add_argument('--title')
    args = parser.parse_args()
    if args.body :
        BODY_SELECTOR = args.body
    if args.title:
        TITLE_SELECTOR = args.title
    download(args.urls)
