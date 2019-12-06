# J_article_con
import requests
from bs4 import BeautifulSoup

url = "http://www.56wen.com/book/20180409/771641.html"

r = requests.get(url)

t = r.text.encode(r.encoding).decode('utf-8')
soup = BeautifulSoup(t, 'html.parser')

pp = soup.select('#J_article_con')
data = ""
for p in pp:
    data += p.text

print(data)    

