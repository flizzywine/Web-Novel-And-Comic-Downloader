import unittest
from noveldown import BookDownloader
from unittest import mock
from requests_html import HTML, HTMLSession
import random
import time

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


    @unittest.skip
    def test_break_download(self):
        # 失败, 不知道为什么, 总是成功不了, 每次 Ctrl-c,都会被 threading 捕获到, 完全不会调用数据库代码
        # 其实 chapters信息可以直接保存下来,以后每次要调用就直接得到
        # queue 信息呢?
        # 其实 URL 也可以保存一波啊, 包括 两个selector
        # Queue是不能被序列化的
        self.downloader.download_book(self.url, self.chapters_selector, self.text_selector)


    @unittest.skip
    def test_progressbar(self):
        from progressbar import ProgressBar
        pbar = ProgressBar().start()
        for i in range(100):
            time.sleep(0.1)
            pbar.update(i+1)
        pbar.finish()

    @unittest.skip
    def test_ip_pool(self):
        from requests_html  import HTMLSession

        import random
        ip_list = []
        session = HTMLSession()
        r = session.get('https://www.kuaidaili.com/free/')
        tds = r.html.find("td")
        for td in tds:
            if td.attrs['data-title'] == 'IP':
                ip_list.append(td.text)
        ip = random.choice(ip_list)
        proxies = {'https':'https://'+ip, 'http':'http://'+ip}

        r = session.get('https://www.baidu.com', proxies=proxies)

    def test_proxy(self):
        from requests_html  import HTMLSession

        import random
        
        session = HTMLSession()
        ip_list = ['36.248.132.216', '163.204.244.65', '123.169.38.134', '182.34.35.175', '112.14.47.6', '110.243.25.178', '125.110.80.65', '118.24.155.27', '118.24.155.27', '47.94.136.5', '218.249.45.162', '171.12.220.101', '118.112.194.88', '47.107.190.212', '122.4.49.225']
        ip = random.choice(ip_list)
        proxies = {'https':'https://'+ip, 'http':'http://'+ip}

        r = session.get('http://www.baidu.com', proxies=proxies)

        print(r.html)













if __name__ == '__main__':
   unittest.main()
        


        

        
