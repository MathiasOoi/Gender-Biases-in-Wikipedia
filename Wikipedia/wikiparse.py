import xml.etree.ElementTree as etree
from collections import defaultdict
import wikitextparser as wtp
from func-timeout import func_set_timeout
from wikidb import *
import os, re, sys, time, string, signal, sqlite3, zlib


def hms_string(sec_elapsed):
    # Given seconds passed return string of hours:minutes:seconds passed
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)


def strip_tag_name(t):
    # {link}tag_name -> tage_name
    return t[t.rfind("}") + 1:]


def exclude(elem):
    # Skip redirects
    if elem.find('redirect') is not None:
        return True

    # Skip non-article pages.(namespace 0 are article pages)
    # Note that you may need error handling
    if elem.find('ns') is None or elem.find('ns').text != '-1':
        return True

    # We don't have any reason to exclude it, so return
    # False (keep it).
    return False

@func_set_timeout(10)  # There are a few bad articles that cause infinite loops (no idea how)
def parsePage(elem, db=None):
    # Goes over the page and inserts (pageid, title, catergories, article)
    # Into the sqlite databse

    if exclude(elem):
        return

    pageid = elem.find("id").text
    title = elem.find('title').text
    article = elem.find('revision/text').text
    page = wtp.parse(article)
    categories = getCategories(page)
    for c in categories:
        if "births" in c: # Only insert the data if they are a person (has births in the categories)
            db.insert(pageid, title, repr(categories), article)
            return
    return

def getTemplate(page, template):
    """
    Given a parsed article return the string of given template
    :param page: 'wikitextparser._wikitext.WikiText
    :param template: String (first part of a template)
    :return: String of Template
    """
    for tm in page.templates:
        tm = str(tm)
        if tm.split("\n")[0].strip("{").startswith(template):
            return tm


def getCategories(page):
    s = page.string
    # Categories are always listed at the bottom of the wikipedia page
    # So the first "{{Category: " you find everything after it will also be categories
    categories = s[s.find("[[Category:"):].split("\n")
    return categories


def inCategories(page, value):
    # Check if some value is in the categories
    # Ex inCategories(page, births)
    for c in getCategories(page):
        if value in c:
            return True
    return False


def getGender(page):
    # Gets the gender from a page using a simple pronoun count
    # NOTE: only accounts for male and female
    male, mc = ["he", "him", "his"], 0
    female, fc = ["her", "she", "hers"], 0

    for word in page.split():
        if word in male:
            mc += 1
        elif word in female:
            fc += 1

    return "male" if mc > fc else "female"


def removeNotes(s):
    """
    text <--! note
    Remove everything past the <!--
    """
    try:
        return s[:s.index("<!--")]
    except ValueError:
        return s


def parseCell(cell):
    """
    :param cell: String (Wikipedia infobox cell)
    :return: Tuple (String, List)
    """
    cell = cell.strip("\n").strip("  ").strip("| ")
    key, value = cell[:cell.find("=")].strip(" "), cell[cell.find("=") + 2:]
    value = removeNotes(value)
    if value.startswith("{{"):
        value = value.strip("{{").strip("}}")
        if value.startswith("hlist"):
            value = value.strip("hlist").split("|")
            return key, value[1:]
        elif value.startswith("plainlist"):
            value = value.split("\n")[1:-1]
            return key, [v.strip("*{{").strip("}}") for v in value]
        else:
            return key, [value]

    else:
        return key, [value]


PATH_WIKI_XML = 'D:\\Wikipedia\\'
FILENAME_WIKI = 'enwiki-20200901-pages-articles-multistream.xml'
pathWikiXML = os.path.join(PATH_WIKI_XML, FILENAME_WIKI)
start_time = time.time()


def main(file, db):
    # Iterates over every article in the xml dump and inserts (pageid, title, categories, article)
    # Into an sqlite databse if the article is about a perosn
    # This database will later be used to get more specific information
    pageCount = 0
    for event, elem in etree.iterparse(file, events=('end',)):
        elem.tag = strip_tag_name(elem.tag)
        if elem.tag != "page": continue
        print(elem.find("title").text)
        pageCount += 1
	try:
            parsePage(elem, db)
	except BaseException as e:
	    print(e)
        elem.clear()
        if not pageCount % 100000:  # Prints out periodic progress statements
            elapsed_time = time.time() - start_time
            print("{} articles parsed".format((pageCount / 100000) * 100000), end=" ")
            print("Elapsed time: {}".format(hms_string(elapsed_time)))
    db.commit()

    elapsed_time = time.time() - start_time

    print("Elapsed time: {}".format(hms_string(elapsed_time)))


if __name__ == "__main__":
    db = WikiDB("wiki.db")  # Initialize sqlite database
    main(pathWikiXML, db)

