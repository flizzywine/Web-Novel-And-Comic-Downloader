import requests_html

import json
import logging
import sys
from requests_html import HTMLSession
import random
import os
from threading import Thread
from queue import Queue
import pickle
import sqlite3
logging.basicConfig(stream=sys.stdout, level=logging.INFO)



class BookDownloader():

    def __init__(self):
        self.book_url = None
        self.book_name = None
        self.chapters_selector = None
        self.text_selector = None
        self.ignore_n_chapters = 0
        self.chapters = []
        self.last_downloaded_chapter = 0
        self.USE_AGENTS = False
        self.session = HTMLSession()
        # self.download_record = {}
        # if self.USE_AGENTS:
        with open('user-agents.json') as f:
            self.user_agents_list = json.load(f)['user-agents']

    def get_r(self, url):
        user_agent = random.choice(self.user_agents_list)
        header = {"user-agent": user_agent}
        # r = self.session.get(url=url, headers=header)
        r = self.session.get(url, headers=header)
        return r

    def get_book_name(self):
        r = self.get_r(self.book_url)
        self.book_name = r.html.find("title", first=True).text.split()[0]



    def get_chapters_from_web(self):
        r = self.get_r(self.book_url)
        lanmu = r.html.find(self.chapters_selector, first=True)
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
        for chapter in self.chapters:
            self.queue.put(chapter)
        # self.download_record = {url: False for url, title in self.chapters}
        logging.info(f"book name: {self.book_name}")
        logging.info(f"chapters: {self.chapters[:10]}")

    def get_text(self, chapter_url, title):
        # try:
        r = self.get_r(chapter_url)
        text = "\n".join([item.text for item in r.html.find(self.text_selector)])
        logging.info(f"text: {text[:20]}")
        # except:
        #     self.queue.put((chapter_url, title))
        # else:
        #     if text == '':
        #         self.queue.put((chapter_url, title))

        return text

    def map_download(self):
        threads = []

        for i in range(self.n_threads):
            t = Thread(target=self.thread_job)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    def reduce_download(self):
        with open(self.book_name+'.txt', 'w') as f:
            for url, title in self.chapters:
                with open(title+'.txt', 'r') as part:
                    f.write(part.read())
                # os.remove(title+'.txt')
                logging.info(f'merge {title}')
        logging.info(f'{self.book_name} DOWNLOADED!')



    def thread_job(self):
        while not self.queue.empty():
            chapter_url, title = self.queue.get()
            text = self.get_text(chapter_url, title)
            with open(title+'.txt', 'w') as f:
                f.write(title)
                f.write('\n\n')
                f.write(text)
                f.write('\n\n')
            logging.info(f'{title} downloaded!')

    def save_download_record(self):
        chs = sqlite3.Binary(pickle.dumps(self.chapters))
        queue_list = []
        while not self.queue.empty():
            queue_list.append(self.queue.get())
        
        que = sqlite3.Binary(pickle.dumps(queue_list))
        conn = sqlite3.connect('shelf.db')
        c = conn.cursor()
        c.execute(f'''CREATE TABLE IF NOT EXISTS books
           (id INTEGER PRIMARY KEY  AUTOINCREMENT,
           name           TEXT    NOT NULL UNIQUE,
           chapters       BLOB,
           queue          BLOB);''')

        c.execute("select * from books where name=?", (self.book_name, ))
        if len(c.fetchall()) == 0:
            c.execute("insert into books (name, chapters, queue) values (?,?,?)", (self.book_name, chs, que))
            logging.info(f"insert to db {self.book_name}")
        else:
            c.execute("update books set chapters = ? , queue = ? where name = ?", (chs, que, self.book_name))
            logging.info(f"update db {self.book_name}")
        conn.commit()
        conn.close()

    def get_chapters_info(self):
        conn = sqlite3.connect('shelf.db')
        c = conn.cursor()
        c.execute(f'''CREATE TABLE IF NOT EXISTS books
           (id INTEGER PRIMARY KEY  AUTOINCREMENT,
           name           TEXT    NOT NULL UNIQUE,
           chapters       BLOB,
           queue          BLOB);''')
        c.execute("select * from books where name=?", (self.book_name, ))
        if len(c.fetchall()) == 0:
            conn.commit()
            conn.close()
            logging.info("get chapters from web")
            self.get_chapters_from_web()
        else:
            c.execute("select chapters, queue from books where name=?", (self.book_name, ))
            chs, que = c.fetchone()
            self.chapters = pickle.loads(chs)
            queue_list = pickle.loads(que)
            while len(queue_list) > 0:
                self.queue.put(queue_list.pop(0))
            # self.queue = pickle.loads(que)
            logging.info("get chapters from db: {self.chapters}, {self.queue}")
            conn.commit()
            conn.close()


    def download_book(self, book_url, chapters_selector, text_selector, ignore_n_chapters=12, n_threads=2):
        self.book_url = book_url
        self.book_name = None
        self.chapters_selector = chapters_selector
        self.text_selector = text_selector
        self.ignore_n_chapters = ignore_n_chapters
        self.n_threads = n_threads
        self.chapters = []
        self.last_downloaded_chapter = 0
        self.queue = Queue()


        self.get_book_name()
        self.get_chapters_info()
        
        
        try:
            self.map_download()
            self.reduce_download()
        except KeyboardInterrupt:
            
            # 为了做到断点续传, 需要维护两个信息, 剩余未下载的章节, 章节间的顺序
            self.save_download_record()

        

            

if __name__ == '__main__':
    downloader = BookDownloader()
    downloader.download_book('https://www.ibiquge.net/48_48106/', "#list",  '#content')

    


