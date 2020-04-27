import requests_html

import json
import logging
import sys
from requests_html import HTMLSession
import random
import os
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


import ssl
ssl._create_default_https_context = ssl._create_unverified_context

class BookDownloader():
    book_url = "https://www.chinesezj.net/chinesezj/28/28143/"
    book_name = 'xxx'
    contents_selector = '.list-charts'
    text_selector = '.content-ext'
    contents = []
    last_downloaded_chapter = 0
    USE_AGENTS = False

    def __init__(self):
        self.session = HTMLSession()
        # if self.USE_AGENTS:
        with open('user-agents.json') as f:
            self.user_agents_list = json.load(f)['user-agents']

    def get_r(self, url):
        user_agent = random.choice(self.user_agents_list)
        header = {"user-agent": requests_html.user_agent()}
        # r = self.session.get(url=url, headers=header)
        r = self.session.get(url, verify=False, headers=header)
        return r

    def get_contents(self):
        r = self.get_r(self.book_url)
        lanmu = r.html.find(self.contents_selector, first=True)
        self.book_name = r.html.find("title", first=True).text
        contents = [(item.attrs['href'], item.text) for item in lanmu.find("a")]
        for l, t in contents:
            for link in lanmu.absolute_links:
                if link.endswith(l):
                    self.contents.append((link, t))
                    break
                
        logging.info(f"book name: {self.book_name}")
        logging.info(f"contents: {self.contents[:10]}")

    def get_text(self, chapter_url):
        r = self.get_r(chapter_url)
        text = "\n".join([item.text for item in r.html.find(self.text_selector)])
        logging.info(f"text: {text[:20]}")
        return  text




    def save_bookmark(self):
        with open('fail.log', 'a') as f:
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





    def download_book(self):
        self.get_contents()
        if os.path.exists('fail.log'):
            self.continue_download()

        with  open(self.book_name+".txt", 'a') as f:
            try:
                for chapter_url, chapter_title in self.contents[self.last_downloaded_chapter:]:
                    logging.info(f"downloading {chapter_url}, {chapter_title}")
                    chapter_text = self.get_text(chapter_url)
                    f.write(f"\n\n{chapter_title}\n\n")
                    f.write(chapter_text)
                    self.last_downloaded_chapter += 1
                logging.info("DONE!")
                os.remove("fail.log")
            except Exception as e:
                print(e)
                self.save_bookmark()
                raise Exception("break download")

            


downloader = BookDownloader()

downloader.download_book()

