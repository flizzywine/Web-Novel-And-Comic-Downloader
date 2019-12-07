l = [('红楼遗秘', 'h1'), ('设定及资料集（一）', 'h2'), ('红楼遗秘最新章节_红楼遗秘设定及资料集（一）_辣文肉文_一起看书网小说', 'title')]

import re

def better_title(a):
    if re.search(r'第.*[章节回卷集]', a[0]):
        return 0
    if re.search(r'[0-9]+', a[0]):
        return 1
    if re.search(r'[一二三四五六七八九十]+', a[0]):
        print(a, 1)
        return 1
    else:
        return 2

l.sort(key=better_title)
print(l)



