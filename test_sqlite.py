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
       name           TEXT    NOT NULL UNIQUE,
       chapters       BLOB,
       queue          BLOB);''')

    def tearDown(self):
        self.conn.commit()
        self.conn.close()

    def test_select_not_found_book(self):
        self.c.execute("select * from books where name=?", ("NoThisBook", ))
        self.assertEqual(self.c.fetchall(), [])

    def test_load_from_db(self):
        self.c.execute("select chapters, queue from books where name=?", ("hi",))
        chs , que = self.c.fetchone()
        chapters = loads(chs)
        queue = loads(que)
        self.assertEqual(chapters, range(10))
        self.assertEqual(queue, range(100))
        


if __name__ == '__main__':
   unittest.main()
