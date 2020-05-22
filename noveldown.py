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
import time
import argparse
from urllib.parse import urlparse
from progressbar import ProgressBar
DEBUG = False
logging.basicConfig(stream=sys.stdout, level=logging.WARN)



class BookDownloader():

    def __init__(self):
        self.book_url = None
        self.book_name = None
        self.chapters_selector = None
        self.text_selector = None
        self.progressbar = ProgressBar().start()
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

    def get_chapters_from_web(self):
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
        self.chapters = self.chapters[self.n_ignore_first:]
        # 测试用, 只截取少量 chapters
        global DEBUG
        if DEBUG:
            self.chapters = self.chapters[:15]
        for chapter in self.chapters:
            self.queue.put(chapter)
        # self.download_record = {url: False for url, title in self.chapters}
        logging.info(f"book name: {self.book_name}")
        logging.info(f"chapters: {self.chapters[:10]}")

        write_data = (self.book_url,
                      self.book_name,
                      sqlite3.Binary(pickle.dumps(self.chapters)),
                      sqlite3.Binary(pickle.dumps(self.chapters)), # this is queue 
                      sqlite3.Binary(pickle.dumps((self.chapters_selector, self.text_selector)))
                      )
      
        self.c.execute('insert into books (url, name, chapters, queue, selectors) values(?,?,?,?,?)',
                       write_data)
        self.conn.commit()

    def get_text(self, chapter_url, title):
        r = self.get_r(chapter_url)
        text = "\n".join([item.text for item in r.html.find(self.text_selector)])
        logging.info(f"text: {text[:20]}")
        return text

    def map_download(self):
        threads = []

        for i in range(self.n_threads):
            t = Thread(target=self.thread_job)
            t.setDaemon(True)
            t.start()
            threads.append(t)
        for thread in threads:
            thread.join()

        # self.check_all_downloaded()

    def check_all_downloaded(self):
        for chapter in self.chapters:
            if not os.path.exists(chapter[1]+'.txt'):
                self.queue.put(chapter)
        self.map_download()


    def reduce_download(self):
        with open(self.book_name+'.txt', 'w') as f:
            for url, title in self.chapters:
                with open(title+'.txt', 'r') as part:
                    f.write('\n\n'+title+'\n\n')
                    f.write(part.read())
                os.remove(title+'.txt')
                logging.info(f'merged {title}')
                
        logging.info(f'{self.book_name} DOWNLOADED!')
        self.progressbar.finish()

    def progress(self):
        while not self.queue.empty():
            cur_progress = len(self.chapters) - self.queue.qsize()
            self.progressbar.update(cur_progress/len(self.chapters)*100)
            # time.sleep(0.2)
        self.progressbar.finish()
        return


    def thread_job(self):

        n_fail_times = 0
        while not self.queue.empty():
            chapter_url, title = self.queue.get()
            text = self.get_text(chapter_url, title)
            if text == '':
                n_fail_times += 1
                if n_fail_times > 5:
                    n_fail_times = 1
                
                self.queue.put((chapter_url, title))
                logging.info(f"{title} get empty text")
                time.sleep(2)
            else:
                with open(title+'.txt', 'w') as f:
                    f.write(text)
                time.sleep(0.5)
                self.progressbar.update((len(self.chapters)-self.queue.qsize())/len(self.chapters)*100)
                logging.info(f'{title} downloaded!')

    def save_download_record(self):
        queue_list = []
        
        # queue_copied = copy.deepcopy(self.queue)
        while not self.queue.empty():
            queue_list.append(self.queue.get())

        for item in queue_list:
            self.queue.put(item)

        que = sqlite3.Binary(pickle.dumps(queue_list))

        self.c.execute("update books set queue=? where url=?", (que, self.book_url))
        self.conn.commit()
        logging.info(f"save queu to db len:{len(queue_list)}")

    def get_chapters_info(self):
        self.c.execute("select * from books where url=?", (self.book_url, ))
        if len(self.c.fetchall()) == 0:
            logging.info("get chapters from web")
            self.get_chapters_from_web()
        else:
            self.c.execute("select name, chapters, queue, selectors from books where url=?", (self.book_url, ))
            name, chs, que, selectors = self.c.fetchone()
            self.conn.commit()
            self.book_name = name
            self.chapters = pickle.loads(chs)
            self.chapters_selector, self.text_selector = pickle.loads(selectors)
            queue_list = pickle.loads(que)
            logging.info("get chapters from db")
            logging.info(f"get queue from db len:{len(queue_list)}")
            while len(queue_list) > 0:
                self.queue.put(queue_list.pop(0))

    def site_config(self):
        """针对输入的 URL,在数据表 site 中查找对应的配置记录,
        查不到就放弃, 如果发现未记录的网站, 并且没有手动配置, 就会报错,
        如果有手动配置, 则更新或插入记录"""
        
        site_url = urlparse(self.book_url).netloc
        
        self.c.execute('select * from sites where url=?', (site_url,))
        if len(self.c.fetchall()) == 0:
            if self.chapters_selector is not None and self.text_selector is not None:

                self.c.execute("insert into sites (url, selecotrs, n_ignore_first) values(?,?,?)",
                                (site_url,
                                 sqlite3.Binary(pickle.dumps((self.chapters_selector, self.text_selector))),
                                 self.n_ignore_first))
            else:
                raise Exception("Please specify selecotrs")
        else:
            self.c.execute('select * from sites where url=?', (site_url,))
            id, url, selecotrs, n_ignore_first = self.c.fetchone()
            self.chapters_selector, self.text_selector = pickle.loads(selecotrs)
            self.n_ignore_first = n_ignore_first
            logging.info("get site config from db")
        



    def download_book(self, book_url, chapters_selector=None, text_selector=None, ignore_n_chapters=0, n_threads=1):
        self.book_url = book_url
        self.book_name = None
        self.chapters_selector = chapters_selector
        self.text_selector = text_selector
        self.ignore_n_chapters = ignore_n_chapters
        self.n_threads = n_threads
        self.chapters = []
        self.last_downloaded_chapter = 0
        self.queue = Queue()
        self.conn = sqlite3.connect('shelf.db')
        self.c = self.conn.cursor()
        self.c.execute(f'''CREATE TABLE IF NOT EXISTS books
           (id INTEGER PRIMARY KEY  AUTOINCREMENT,
           url           TEXT    NOT NULL UNIQUE,
           name          TEXT,
           selectors      BLOB,
           chapters       BLOB,
           queue          BLOB
           all_text      TEXT);''')

        self.site_config()

        self.get_chapters_info()
        try:
            self.map_download()
            self.check_all_downloaded()
            self.reduce_download()
        except KeyboardInterrupt:
            # 为了做到断点续传, 需要维护两个信息, 剩余未下载的章节, 章节间的顺序
            self.save_download_record()
            self.conn.close()
        else:
            self.conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('book_url', type=str)
    parser.add_argument('--chapters_selector', type=str)
    parser.add_argument('--text_selector', type=str)
    args = parser.parse_args()
    downloader = BookDownloader()
    # 输入 小说目录页 URL 即可
    # 多数情况下只需要输入一个 URL 即可, 但对于某些非主流网站, 必须手动配置chapters_selector, text_selector
    book_url = args.book_url
    downloader.download_book(book_url)



