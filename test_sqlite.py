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

    def test_pickle_binary(self):
        a = 1
        b = 2
        c = 3
        bdata = [sqlite3.Binary(dumps(x)) for x in [a, b, c]]
        self.c.execute("insert into books (url) values(?)", ('array', ))
        self.c.execute("update books set chapters=?, selectors=?, queue=?", [b for b in bdata])
        self.conn.commit()







if __name__ == '__main__':
   unittest.main()
