import unittest
from noveldown import BookDownloader
from unittest import mock
from requests_html import HTML, HTMLSession
import random

class Tests(unittest.TestCase):
    def setUp(self):
        self.downloader = BookDownloader('https://www.ibiquge.net/48_48106/', "#list",  '#content' )
     
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

    def test_threads(self):
        self.downloader.download_threads()





        


if __name__ == '__main__':
   unittest.main()
        


        

        
