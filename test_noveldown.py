import unittest
from noveldown import BookDownloader
from unittest import mock
from requests_html import HTML, HTMLSession
import random

class Tests(unittest.TestCase):
    def setUp(self):
        self.downloader = BookDownloader()
        self.url, self.chapters_selector, self.text_selector = 'https://www.ibiquge.net/48_48106/', "#list",  '#content'

    @unittest.skip
    def test_get_text(self):
        url = 'https://www.ibiquge.net/48_48106/23509936.html'
        text = self.downloader.get_text(url)
        # print(text)

    @unittest.skip
    def test_get_contents(self):
        self.downloader.get_contents()
        print(self.downloader.contents)

    @unittest.skip
    def test_random_user_agent(self):
        for i in range(10):
            user_agent = random.choice(self.downloader.user_agents_list)
            # print(user_agent)

    @unittest.skip
    def test_down_chapter(self):
        url = 'https://www.ibiquge.net/48_48106/23509945.html'
        
        self.downloader.text_selector = '#content'

        text = self.downloader.get_text(url)
        print(text)

    def test_break_download(self):
        # 失败, 不知道为什么, 总是成功不了, 每次 Ctrl-c,都会被 threading 捕获到, 完全不会调用数据库代码
        # 其实 chapters信息可以直接保存下来,以后每次要调用就直接得到
        # queue 信息呢?
        # 其实 URL 也可以保存一波啊, 包括 两个selector
        self.downloader.download_book(self.url, self.chapters_selector, self.text_selector)







if __name__ == '__main__':
   unittest.main()
        


        

        
