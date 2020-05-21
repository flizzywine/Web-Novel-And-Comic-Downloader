import requests_html

import json
import logging
import sys
from requests_html import HTMLSession
import random
import os
from threading import Thread
from queue import Queue
logging.basicConfig(stream=sys.stdout, level=logging.INFO)



class BookDownloader():

    def __init__(self, book_url, chapters_selector, text_selector):
        self.book_url = book_url
        self.book_name = None
        self.chapters_selector = chapters_selector
        self.text_selector = text_selector
        self.ignore_n_chapters = 12
        self.chapters = []
        self.last_downloaded_chapter = 0
        self.USE_AGENTS = False
        self.session = HTMLSession()
        # if self.USE_AGENTS:
        with open('user-agents.json') as f:
            self.user_agents_list = json.load(f)['user-agents']

    def get_r(self, url):
        user_agent = random.choice(self.user_agents_list)
        header = {"user-agent": user_agent}
        # r = self.session.get(url=url, headers=header)
        r = self.session.get(url, verify=False, headers=header)
        return r

    def get_chapters(self):
        r = self.get_r(self.book_url)
        lanmu = r.html.find(self.chapters_selector, first=True)
        self.book_name = r.html.find("title", first=True).text.split()[0]
        chapters = [(item.attrs['href'], item.text) for item in lanmu.find("a")]
        
        # 因为得到的href不一定是相对 URL,可能是绝对 URL,所以需要检查一下
        if not chapters[0][0].startswith(self.book_url):
            from urllib.parse import urljoin
            for url, title in chapters:
                new_url = urljoin(self.book_url, url)
                self.chapters.append((new_url, title))
        else:
            self.chapters = chapters

        # 忽略最开始的若干章预览章节
        self.chapters = self.chapters[self.ignore_n_chapters:]
        # 测试用, 只截取少量 chapters
        self.chapters = self.chapters[:30]
        logging.info(f"book name: {self.book_name}")
        logging.info(f"chapters: {self.chapters[:10]}")

    def get_text(self, chapter_url):
        r = self.get_r(chapter_url)
        text = "\n".join([item.text for item in r.html.find(self.text_selector)])
        logging.info(f"text: {text[:20]}")
        return text


    def save_bookmark(self):
        with open('fail.log', 'w') as f:
            f.write(f"{self.book_name}:{self.last_downloaded_chapter}\n")
            logging.info(f"save bookmark {self.last_downloaded_chapter}")

    def continue_download(self):
        with open('fail.log','r') as f:
            for line in f:
                name, index = line.split(":")
                if name == self.book_name:
                    self.last_downloaded_chapter = int(index)
                    return
            # raise "No bookmark"

    def download_threads(self):
        self.get_chapters()
        self.n_threads = 2
        threads = []
        self.queue = Queue()
        for chapter in self.chapters:
            self.queue.put(chapter)

        for i in range(self.n_threads):
            t = Thread(target=self.download_per_thread)
            t.start()
            threads.append(t)
            
        for t in threads:
            t.join()


        with open(self.book_name+'.txt', 'w') as f:
            for url, title in self.chapters:
                with open(title+'.txt', 'r') as part:
                    f.write(part.read())
                os.remove(title+'.txt')
                logging.info(f'merge {title}')
        
        logging.info(f'{self.book_name} DOWNLOADED!')



    def download_per_thread(self):
        while not self.queue.empty():
            chapter_url, title = self.queue.get()
            text = self.get_text(chapter_url)
            with open(title+'.txt', 'w') as f:
                f.write(title)
                f.write('\n\n')
                f.write(text)
                f.write('\n\n')
            logging.info(f'{title} downloaded!')



    def download_book(self):
        self.get_chapters()
        if os.path.exists('fail.log'):
            self.continue_download()

        with open(self.book_name+".txt", 'a') as f:
            try:
                for chapter_url, chapter_title in self.chapters[self.last_downloaded_chapter:]:
                    logging.info(f"downloading {chapter_url}, {chapter_title}")
                    chapter_text = self.get_text(chapter_url)
                    f.write(f"\n\n{chapter_title}\n\n")
                    f.write(chapter_text)
                    self.last_downloaded_chapter += 1
                logging.info("DONE!")
                if os.path.exists("fail.log"):
                    os.remove("fail.log")
            except Exception as e:
                print(e)
                self.save_bookmark()
                raise Exception("break download")

            

if __name__ == '__main__':
    downloader = BookDownloader('https://www.ibiquge.net/48_48106/', "#list",  '#content' )
    downloader.download_threads()

    


