import pytest
from requests_html import HTMLSession
from requests_html import HTML
import sys
from comicdown2 import download_comic, get_chapters_url, ChapterNameTable

@pytest.fixture
def html():
    with open('index.html') as f:
        res = HTML(html=f.read())
    return res.html

def test_chapter_link_and_title(html):
    links = get_chapters_url()
    print(links)
    

if __name__ == '__main__':
   pytest.main()
    

