import zlib
import sqlite3
from typing import Iterator, Tuple

# There are 3 classes, they are all basically the same

class WikiDB:
    def __init__(self, filename: str):
        """
        This is the source wikidb to do more specific actions on
        Generated by wikiparse.py
        :param filename: Filename for your db
        """
        self.conn = sqlite3.connect(filename)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
          pageid integer,
          title text,
          categories text,
          zarticle text)""")
        self.conn.commit()
        self.pending = 0  # Counter for when to commit

    def maybe_commit(self):
        """
        Called when row is inserted
        Will check if self.pending is 100
        If so commit current data
        This improves time efficiency
        """
        self.pending += 1
        if self.pending > 100:
            self.commit()

    def commit(self):
        """
        Called every 100 self.maybe_commits() and at the end of the parsing
        """
        self.conn.commit()
        self.pending = 0

    def insert(self, pageid: int, title: str, categories: str, article: str):
        """
        Compresses article and inserts values into db
        :param pageid: Unique identifier for every wiki article
        :param title: Title of wiki article
        :param categories: repr of list of categories
        :param article: Wiki article
        """
        zarticle = zlib.compress(article.encode('utf-8'))
        self.conn.execute("""
          INSERT INTO articles VALUES (?, ?, ?, ?);
        """, (pageid, title, categories, zarticle))
        self.maybe_commit()

    def __iter__(self) -> Iterator[Tuple[int, str, str, str]]:
        """
        Generator, iterates over every row of db
        """
        for (pageid, title, categories, zarticle) in self.conn.execute('''
        SELECT * FROM articles;
      '''):
            article = zlib.decompress(zarticle).decode('utf-8')  # Decompress article
            yield (pageid, title, categories, article)

    def iterRandom(self, e: int) -> Iterator[Tuple[int, str, str, str]]:
        """
        Uniformly randomly iterate over e rows in db
        :param e: Amount of articles to iterate over
        """
        for (pageid, title, categories, zarticle) in self.conn.execute('''
                SELECT * FROM articles order by random() limit {};
              '''.format(str(e))):
            article = zlib.decompress(zarticle).decode('utf-8')  # Decompress article
            yield (pageid, title, categories, article)

class WikiInfobox:
    def __init__(self, filename: str):
        """
        Database of articles about people in Wikipedia
        Does not contain the entire article, only contains the infobox
        :param filename: Filename for your db
        """
        self.conn = sqlite3.connect(filename)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
          pageid integer,
          title text,
          categories text,
          chars integer,
          gender text,
          infobox text)""")
        self.conn.commit()
        self.pending = 0  # Counter for when to commit

    def maybe_commit(self):
        """
        Called when row is inserted
        Will check if self.pending is 100
        If so commit current data
        This improves time efficiency
        """
        self.pending += 1
        if self.pending > 100:
            self.commit()

    def commit(self):
        """
        Called every 100 self.maybe_commits() and at the end of the parsing
        """
        self.conn.commit()
        self.pending = 0

    def insert(self, pageid: int, title: str, categories: str, chars: int, gender: str, infobox: str):
        """
        Inserts values into db
        :param pageid: Unique identifier for every wiki article
        :param title: Title of wiki article
        :param categories: repr of list of categories
        :param chars: Characters in article
        :param gender: Gender of person
        :param infobox: Infobox in article
        """
        self.conn.execute("""
          INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?);
        """, (pageid, title, categories, chars, gender, infobox))
        self.maybe_commit()

    def __iter__(self) -> Iterator[Tuple[int, str, str, int, str, str]]:
        """
        Generator, iterates over every row of db
        """
        for (pageid, title, categories, chars, gender, infobox) in self.conn.execute('''
        SELECT * FROM articles;
      '''):
            yield (pageid, title, categories, chars, gender, infobox)

    def iterRandom(self, e: int) -> Iterator[Tuple[int, str, str, int, str, str]]:
        """
        Uniformly randomly iterate over e rows in db
        :param e: Amount of articles to iterate over
        """
        for (pageid, title, categories, chars, gender, infobox) in self.conn.execute('''
                SELECT * FROM articles order by random() limit {};
              '''.format(str(e))):
            yield (pageid, title, categories, chars, gender, infobox)

class WikiDBWithGenderAndInfobox:
    def __init__(self, filename: str):
        self.conn = sqlite3.connect(filename)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
          pageid integer,
          title text,
          categories text,
          chars integer,
          gender text,
          infoboxArgs text)""")
        self.conn.commit()
        self.pending = 0

    def maybe_commit(self):
        self.pending += 1
        if self.pending > 100:
            self.commit()

    def commit(self):
        self.conn.commit()
        self.pending = 0

    def insert(self, pageid, title, categories, chars, gender, infoboxArgs):
        self.conn.execute("""
          INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?);
        """, (pageid, title, categories, chars, gender, infoboxArgs))
        self.maybe_commit()

    def __iter__(self):
        for (pageid, title, categories, chars, gender, infoboxArgs) in self.conn.execute('''
        SELECT * FROM articles;
      '''):
            yield (pageid, title, categories, chars, gender, infoboxArgs)
    def iterCatergories(self):
        for categories in self.conn.execute("""
        SELECT categories FROM articles;
        """):
            yield categories
    def iterRandom(self, e):
        for (pageid, title, categories, chars, gender, infoboxArgs) in self.conn.execute('''
                SELECT * FROM articles order by random() limit {};
              '''.format(str(e))):
            yield (pageid, title, categories, chars, gender, infoboxArgs)

class WikiDBWithGenderAndInfobox2:
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
          pageid integer,
          title text,
          categories text,
          chars integer,
          gender text,
          infoboxArgs text,
          infobox text
          )""")
        self.conn.commit()
        self.pending = 0

    def maybe_commit(self):
        self.pending += 1
        if self.pending > 100:
            self.commit()

    def commit(self):
        self.conn.commit()
        self.pending = 0

    def insert(self, pageid, title, categories, chars, gender, infoboxArgs, infobox):
        self.conn.execute("""
          INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (pageid, title, categories, chars, gender, infoboxArgs, infobox))
        self.maybe_commit()

    def __iter__(self):
        for (pageid, title, categories, chars, gender, infoboxArgs, infobox) in self.conn.execute('''
        SELECT * FROM articles;
      '''):
            yield (pageid, title, categories, chars, gender, infoboxArgs, infobox)
    def iterCatergories(self):
        for categories in self.conn.execute("""
        SELECT categories FROM articles;
        """):
            yield categories
    def iterRandom(self, e):
        for (pageid, title, categories, chars, gender, infoboxArgs, infobox) in self.conn.execute('''
                SELECT * FROM articles order by random() limit {};
              '''.format(str(e))):
            yield (pageid, title, categories, chars, gender, infoboxArgs, infobox)

