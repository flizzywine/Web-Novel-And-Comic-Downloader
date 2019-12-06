import requests
from bs4 import BeautifulSoup
import sys
import re
import os


TITLE_SELECTOR = 'h1'
BODY_SELECTOR = '#content'
OUTPUT_FILENAME = 'downloaded_novel.txt'
PREFIX_URL = None
START_NUM = None
END_NUM = None

def parse(start_url, end_url, title, body, out):
    global TITLE_SELECTOR, BODY_SELECTOR, PREFIX_URL, START_NUM, END_NUM, OUTPUT_FILENAME
    if out:
        OUTPUT_FILENAME = out
    if title:
        TITLE_SELECTOR = title
    if body:
        BODY_SELECTOR = body

    START_NUM = int(re.search("(\d+)\.html", start_url).group(1))
    END_NUM = int(re.search("(\d+)\.html", end_url).group(1))
    PREFIX_URL = os.path.dirname(start_url)
    assert PREFIX_URL == os.path.dirname(end_url)

    
    

def get_content(content_url):
    res = requests.get(content_url, timeout=10)

    t = res.text.encode(res.encoding).decode('utf-8')

    soup = BeautifulSoup(t, 'html.parser')
    title = soup.select(TITLE_SELECTOR)[0].text
    bodies = soup.select(BODY_SELECTOR)
    content = ""
    for part in bodies:
        content += part.text

    both = title + +'\n' + content + '\n\n'
    return both


def download():
    with open(OUTPUT_FILENAME, "w+") as f:
        for i, num in enumerate(range(START_NUM, END_NUM+1), start=1):
            url = PREFIX_URL+"/"+str(num)+".html"
            content = get_content(url)
            print(".", end=' ')
            if i % 10 == 0 and i != 0:
                print('')
            sys.stdout.flush()
            f.write(content)
            i += 1
    print('\nDONE')
