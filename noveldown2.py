from requests_html import HTMLSession, HTML
from pickle import load, dump
import os
from urllib.parse import urljoin
from queue import Queue
import time
import argparse
import re

def clean_title(title):
    return title[:10]
    

class NovelDownloader:
    def __init__(self, start_url, limit_n=None):
        self.start_url = start_url
        self.book_name = None
        self.queue = Queue()
        self.seq_url = []
        self.url_tmpfile = {}
        self.session = HTMLSession()
        self.cache = {}
        self.limit_n = limit_n
        
                    
    def work(self):
        self.get_urls()
        while not self.queue.empty():
            if self.limit_n is not None and len(self.url_tmpfile) >= self.limit_n:
                break
            i, url = self.queue.get()
            if url in self.cache and url in self.url_tmpfile:
                pass
            else:
                try:
                    html = self.download(url)
                    title, text = self.process(html)
                    text = title + '\n\n' + text
                    self.save_tmp(url, title, text)
                except Exception as e:
                    self.queue.put((i, url))
                    time.sleep(3)
                    print(f'get {i},{url} failed, sleep 3 secs:{e}')
                    raise e
        
        self.merge()

    def get_urls(self):
        start_page = self.download(self.start_url)
        start_page = HTML(html=start_page)
        # find the 'dl' element which has most 'a' element in it
        self.book_name = start_page.find('title')[0].text
        try:
            element = sorted(start_page.find('dl'), key=lambda ele: len(ele.find('a')), reverse=True)[0]
        except IndexError:
            element = sorted(start_page.find('table'), key=lambda ele: len(ele.find('a')), reverse=True)[0]

        links = []
        if not element.find('a')[0].attrs['href'].startswith(self.start_url):
            # the link url is relative, not absolute
            for link in element.find('a'):
                url = link.attrs['href']
                links.append(urljoin(self.start_url, url))
        else:
            for link in element.find('a'):
                url = link.attrs['href']
                links.append(url)
        for i, url in enumerate(links, start=1):
            self.seq_url.append(url)
            self.queue.put((i,url))

    def download(self, url):
        """just download url and cache it"""
        if url in self.cache:
                print('hit cache')
                return self.cache[url]
        else:
            html = self.session.get(url).html.html
            self.cache[url] = html        
            return html
        

    def process(self, html):
        text_html = HTML(html=html)
        title = text_html.find('title')[0].text
        self.divs = []
        for div in text_html.find('div'):
            if len(div.find('div')) == 1:
                self.divs.append(div)
        try:
            ele = sorted(self.divs, key=lambda div: len(div.text), reverse=True)[0]
            text = ele.text
        except IndexError:
            text = "MISS TEXT"
        
        self.divs = []
        return title, text
    
    def save_tmp(self, url, title, text):
        tmp_name = title + '.txt'
            
        with open(tmp_name, 'w') as f:
            f.write(text)
        self.url_tmpfile[url] = tmp_name
        

    def merge(self):
        with open(self.book_name, 'w+') as f:
            for url in self.seq_url:
                try:
                    tmp_name = self.url_tmpfile[url]
                    tmp_f = open(tmp_name, 'r')
                    f.write(tmp_f.read()+'\n\n')
                    tmp_f.close()
                except KeyError as e:
                    print(f'missing file for url:{url}, interrput')
                    break

        
        os.system(f'mv {self.book_name}.txt ..')
        os.system(f'rm *.txt')
        self.url_tmpfile = {}
        


    def __enter__(self):
        if os.path.exists('cache.pkl'):
            with open('cache.pkl', 'rb') as f:
                self.cache = load(f)
        else:
            with open('cache.pkl', 'wb') as f:
                dump(self.cache, f)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open('cache.pkl', 'wb') as f:
            dump(self.cache, f)

   

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    args = parser.parse_args()
    with NovelDownloader(args.url) as downloader:
        downloader.work()

