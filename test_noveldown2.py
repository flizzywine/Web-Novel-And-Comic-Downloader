import unittest
from unittest import TestCase
from noveldown2 import NovelDownloader
from requests_html import HTML,HTMLSession,Element

class TestNovelDown(TestCase):
    def setUp(self):
        url = "https://www.shuhaige.net/90998/"
        self.downloader = NovelDownloader(url)
        self.downloader.__enter__()
        self.downloader.get_urls()
        
    def tearDown(self):
        self.downloader.__exit__(None, None ,None)
        
    def test_get_urls(self):
        self.downloader.get_urls()
        
    def test_work(self):
        self.downloader.work()
    
    def test_download(self):
        html = self.downloader.download(self.downloader.seq_url[1])

    def test_merge(self):
        self.downloader.merge() 
        

if __name__ == "__main__":
    unittest.main()

