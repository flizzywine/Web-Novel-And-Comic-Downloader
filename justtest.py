from bs4 import BeautifulSoup

with open('index.html', 'r') as f:
    t = f.read()

soup = BeautifulSoup(t, 'html.parser')


for div in soup.find_all('div'):
    try:
        for cls in div['class']:
            if 'content'  in cls or 'text' in cls:
                print(cls)
    except:
        pass

    
    
    
