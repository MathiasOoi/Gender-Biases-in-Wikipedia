import zlib
import sqlite3


class WikiDB:
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
          pageid integer,
          title text,
          categories text,
          zarticle text)""")
        self.conn.commit()
        self.pending = 0

    def maybe_commit(self):
        self.pending += 1
        if self.pending > 100:
            self.commit()

    def commit(self):
        self.conn.commit()
        self.pending = 0

    def insert(self, pageid, title, categories, article):
        zarticle = zlib.compress(article.encode('utf-8'))
        self.conn.execute("""
          INSERT INTO articles VALUES (?, ?, ?, ?);
        """, (pageid, title, categories, zarticle))
        self.maybe_commit()

    def __iter__(self):
        for (pageid, title, categories, zarticle) in self.conn.execute('''
        SELECT * FROM articles;
      '''):
            article = zlib.decompress(zarticle).decode('utf-8')
            yield (pageid, title, categories, article)
    def iterCatergories(self):
        for categories in self.conn.execute("""
        SELECT categories FROM articles;
        """):
            yield
    def iterRandom(self, e):
        for (pageid, title, categories, zarticle) in self.conn.execute('''
                SELECT * FROM articles order by random() limit {};
              '''.format(str(e))):
            article = zlib.decompress(zarticle).decode('utf-8')
            yield (pageid, title, categories, article)

class WikiDBWithGenderAndInfobox:
    def __init__(self, filename):
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

