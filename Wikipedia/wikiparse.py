import os
import time
import xml.etree.ElementTree as etree
from itertools import chain
from typing import Tuple, List

import wikitextparser as wtp
from func_timeout import func_set_timeout

from wikidb import WikiDB


def hms_string(sec_elapsed: int) -> str:
    """
    Gets time in Hour:Minutes:Seconds
    :param sec_elapsed: seconds elapsed
    :return: Hour:Minutes:Seconds
    """
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)


def strip_tag_name(t: str) -> str:
    """
    Removes link from tag name
    {link}tag_name -> tage_name
    :param t: {link}tag_name
    :return: Stripped tag name
    """
    return t[t.rfind("}") + 1:]


def exclude(elem: etree.Element) -> bool:
    """
    Called at the start of parsePage() used to exclude non-article pages
    :param elem: Article element in the xml file
    :return: True | False
    """
    # Skip redirects
    if elem.find('redirect') is not None:
        return True

    # Skip non-article pages.(namespace 0 are article pages)
    # Note that you may need error handling
    if elem.find('ns') is None or elem.find('ns').text != '0':
        return True

    # We don't have any reason to exclude it, so return
    # False (keep it).
    return False

@func_set_timeout(10)
def parsePage(elem, db: WikiDB = None, filter: str = "births") -> None:
    """
    Parses a page (id, title, categories, article)
    Put it into a given sqlite3 database
    :param elem: Article element in the xml file
    :param db: sqlite3 db
    :param filter: Categories to filter by separated by commas
    """
    if exclude(elem): return  # Only iterate over articles

    # Parse out basic information
    pageid = elem.find("id").text
    title = elem.find('title').text
    article = elem.find('revision/text').text

    # Only insert the data if the categories fit the filter
    page = wtp.parse(article)
    categories = list(chain.from_iterable(getCategories(page)))
    if all(i in categories for i in filter):
            db.insert(pageid, title, repr(categories), article)

def getCategories(page: wtp._wikitext.WikiText) -> List[str]:
    """
    Gets the lists of categories for a wiki article page
    :param page: Parsed article using wikitextparser
    :return: List of categories
    """
    # Categories are always listed at the bottom of the wikipedia article
    # So the first "[[Category: ...]]" you find everything after it will be categories
    s = page.string
    categories = s[s.find("[[Category:"):].split("\n")
    return categories

PATH_WIKI_XML = 'path\\to\\file'
FILENAME_WIKI = 'enwiki-20200901-pages-articles-multistream.xml'  # Dump you are using
pathWikiXML = os.path.join(PATH_WIKI_XML, FILENAME_WIKI)  # Creates path to wiki xml dump
start_time = time.time()

def main(file: str, db: WikiDB, filter: str = "births") -> None:
    """
    Sequentially iterates over xml file and parses it
    Creates a db with only the articles you want
    Can use the db as a source for more specific things
    :param file: Path to xml file
    :param db: sqlite3 db
    :param filter: Category filters separated by commas (default is for any person)
    """
    pageCount = 0
    for event, elem in etree.iterparse(file, events=('end',)):
        elem.tag = strip_tag_name(elem.tag)
        if elem.tag != "page": continue  # Only parses a page once you finish getting all the elem attrib
        # print(elem.find("title").text)  # For debugging
        pageCount += 1
        try:
            parsePage(elem, db, filter)
        # Some articles throw an exception
        # Other articles run forever and hit the time limit, which throws a keyboard interrupt
        except BaseException as e:
            print(e)
        elem.clear()  # Clear elem for next use
        if not pageCount % 100000:  # Prints out periodic progress statements
            elapsed_time = time.time() - start_time
            print("{} articles parsed".format((pageCount / 100000) * 100000), end=" ")
            print("Elapsed time: {}".format(hms_string(elapsed_time)))
    db.commit()

    elapsed_time = time.time() - start_time

    print("Elapsed time: {}".format(hms_string(elapsed_time)))


if __name__ == "__main__":
    db = WikiDB("wiki.db")  # Initialize sqlite database
    main(pathWikiXML, db)   # Takes a few hours to run

