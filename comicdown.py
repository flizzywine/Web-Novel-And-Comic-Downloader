import os
import re
import sys
import threading
import time
from multiprocessing import Pool
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup
from requests.exceptions import MissingSchema
from requests.exceptions import ChunkedEncodingError
Url = str
FileName = str

img_table = set()

pic_name_table: Dict[Url,FileName] = dict() 


def urls_iter(url, type='chapter'):
    if type == 'chapter':
        match_pat = r'\[(.*)\-(.*)\]'
        sub_pat = r'\[.*\]'
    elif type == 'volumns':
        match_pat = r'\{(.*)\-(.*)\}'
        sub_pat = r'\{.*\}'

    m = re.search(match_pat, url)
    if not m:
        yield url
        return  
    start, end = int(m.group(1)), int(m.group(2))
    for i in range(start, end+1):
        if i == 1:
            url2 = re.sub(sub_pat, "", url)
            url2 = url2.replace("_", "")
        else:
            url2 = re.sub(sub_pat, str(i), url)
               
        yield url2

def img_url(page_url):
    # print(f"try to get imgs of {page_url}")
    page_data = requests.get(page_url, timeout=5).text
    soup = BeautifulSoup(page_data, 'html.parser')
    # print("soup", soup)
    title = soup.select('title')[0].text
    imgs = soup.find_all("img")
    # print(imgs)
   
    for img in imgs:
        # print(f"title {title} alt: {img['alt']}")
        if img['alt'].startswith(title[0:4]):
            return img['src']




def download_img(img_url, page_url, dir_num):
    resp = requests.get(img_url)
    # print(f"header {resp.headers}")
    img_name = page_url.split("/")[-1].split(".")[0] + ".jpg"
    img_path = os.path.join(comic_name, str(dir_num), img_name)
    with open(img_path, 'wb') as pic:
        for chunk in resp.iter_content(128):
            pic.write(chunk)
    print(f"{img_path} downloaded")

    
    
    


urls_text = "https://www.caomeng.cc/neihanmanhua/370/284_[14-50].html"
comic_name = "秋色之空"
DIR_NUM = 2
SLEEP = 5 
if __name__ == '__main__':
    
    urls: List[Any] = []
    if not os.path.exists(comic_name):
        os.mkdir(comic_name)
    dir_num = DIR_NUM -1
    for url_vol in urls_iter(urls_text, type='volumns'):
        dir_num += 1
        path = os.path.join(comic_name, str(dir_num))
        if not os.path.exists(path):
            os.mkdir(path)

        urls.append(list(urls_iter(url_vol, type='chapter')))

    print(f"trying to download urls: {urls}")

    dir_num = DIR_NUM - 1
    for url_vol in urls:
        dir_num += 1
        for url_ch in url_vol:
            try:
                pic_url = img_url(url_ch)
                print(f"get img src of {url_ch}: {pic_url}")
            except:
                print("error in img_url")
                break
            try:
                download_img(pic_url, url_ch, dir_num)
                time.sleep(SLEEP)
                print("Sleeping....")
            except MissingSchema as e:
                print(f"download fail: {dir_num}/{url_ch}, continue next chapter")
                break
            except ChunkedEncodingError as e:
                # time.sleep(60)
                # download_img(pic_url, url_ch, dir_num)
                raise Exception("reset by peer")
