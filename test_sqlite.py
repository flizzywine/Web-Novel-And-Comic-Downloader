import sqlite3
from pickle import loads, dumps

from unittest import TestCase
import unittest

class Tests(TestCase):
    def setUp(self):
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


    def tearDown(self):
        self.conn.commit()
        self.conn.close()

    def test_select_not_found_book(self):
        self.c.execute("select * from books where name=?", ("NoThisBook", ))
        self.assertEqual(self.c.fetchall(), [])

    @unittest.skip
    def test_load_from_db(self):
        self.c.execute("select chapters, queue from books where name=?", ("hi",))
        chs , que = self.c.fetchone()
        chapters = loads(chs)
        queue = loads(que)

    @unittest.skip
    def test_insert_repeat(self):
        self.c.execute("insert into books (url) values(?)", ('repaeat',))
        self.conn.commit()
        try:
            self.c.execute("insert into books (url) values(?)", ('repaeat',))
            self.conn.commit()
        except Exception:
            pass
        
    @unittest.skip
    def test_pickle_binary(self):
        a = 1
        b = 2
        c = 3
        bdata = [sqlite3.Binary(dumps(x)) for x in [a, b, c]]
        self.c.execute("insert into books (url) values(?)", ('array', ))
        self.c.execute("update books set chapters=?, selectors=?, queue=?", [b for b in bdata])
        self.conn.commit()

    @unittest.skip
    def test_selector_config(self):
        self.c.execute(f'''CREATE TABLE IF NOT EXISTS sites
           (id INTEGER PRIMARY KEY  AUTOINCREMENT,
           url           TEXT    NOT NULL UNIQUE,
           selectors      BLOB,
           n_ignore_first   INTEGER);''')
        url = 'https://www.ibiquge.net/'
        selectors = sqlite3.Binary(dumps(('#list','#content')))
        n_ignore_first = 12
        self.c.execute("insert into sites (url, selectors, n_ignore_first) values(?,?,?)",
                       (url, selectors, n_ignore_first))
        self.conn.commit()

    def test_site_url(self):
        from urllib.parse import urlparse
        book_url = 'https://www.ibiquge.net/48_48106/'
        site_url = urlparse(book_url).netloc
        self.assertEqual(site_url, 'www.ibiquge.net')

    def test_find_no_site(self):
        site_url = 'www.ibiquge.net'

        self.c.execute("select * from sites where url=?", (site_url, ))
        print(self.c.fetchall())
        print(self.c.fetchall())
        







if __name__ == '__main__':
   unittest.main()
