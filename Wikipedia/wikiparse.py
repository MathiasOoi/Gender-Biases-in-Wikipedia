import xml.etree.ElementTree as etree
from collections import defaultdict
import wikitextparser as wtp
from wikidb import *
import os, re, sys, time, string, signal, sqlite3, zlib

#test
def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)


def strip_tag_name(t):
    return t[t.rfind("}") + 1: len(t)]


def exclude(elem):
    # Skip redirects
    if elem.find('redirect') is not None:
        return True

    # Skip non-article pages.
    # Note that you may need error handling
    if elem.find('ns') is None or elem.find('ns').text != '0':
        return True

    # We don't have any reason to exclude it, so return
    # False (keep it).
    return False


def parsePage(elem, db=None):
    if exclude(elem):
        return

    pageid = elem.find("id").text
    title = elem.find('title').text
    article = elem.find('revision/text').text
    page = wtp.parse(article)
    categories = getCategories(page)
    for c in categories:
        if "births" in c:
            db.insert(pageid, title, repr(categories), article)
            return
    return
    # 3 Steps
    # 1) Get the infobox
    # 2) Remove the first and last lines by slicing
    # 3) Turn it into a Table
    # Note: Code skips articles without infoboxes
    # if inCategories(page, "births"):
    #     infobox = getTemplate(page, "Infobox")
    #     if infobox is None:
    #         return
    #     infobox = infobox[infobox.find("\n") + 1: infobox.rfind("\n")]
    #     if infobox.count("\n") == 0:  # One line infobox creates an infinite loop
    #         return
    #     infobox = wtp.Table(infobox)
    #
    #
    #     # Iterate over every cell and parse it
    #     d = defaultdict(list)
    #     try:
    #         for a in range(len(infobox.cells())):
    #             for b in range(len(infobox.cells(row=a))):
    #                 parsed = parseCell(str(infobox.cells(row=a, column=b)))
    #                 d[parsed[0]] = parsed[1]
    #     except IndexError:
    #         return
    #
    #     gender = getGender(article)
    #     spouse = d["spouse"]
    #     children = d["children"]
    #     occupation = d["occupation"]
    #
    #     db.insert(pageid, title, chars, gender, spouse, children, occupation)


def getTemplate(page, template):
    """
    Given a parsed article return the string of given template
    :param page: 'wikitextparser._wikitext.WikiText'
    :param template: String (first part of a template)
    :return: String of Template
    """
    for tm in page.templates:
        tm = str(tm)
        if tm.split("\n")[0].strip("{").startswith(template):
            return tm


def getCategories(page):
    s = page.string
    categories = s[s.find("[[Category:"):].split("\n")
    return categories


def inCategories(page, value):
    for c in getCategories(page):
        if value in c:
            return True
    return False


def getGender(page):
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
    pageCount = 0
    for event, elem in etree.iterparse(file, events=('end',)):
        elem.tag = strip_tag_name(elem.tag)
        if elem.tag != "page": continue
        print(elem.find("title").text)
        if elem.find("title").text in ["List of heads of government of Russia", "2014 Roger Federer tennis season", "Results of the 2019 Canadian federal election by riding"]:
            elem.clear()
            continue
        pageCount += 1
        parsePage(elem, db)
        elem.clear()
        if not pageCount % 100000:
            elapsed_time = time.time() - start_time
            print("{} articles parsed".format((pageCount / 100000) * 100000), end=" ")
            print("Elapsed time: {}".format(hms_string(elapsed_time)))
    db.commit()

    elapsed_time = time.time() - start_time

    print("Elapsed time: {}".format(hms_string(elapsed_time)))


if __name__ == "__main__":
    db = WikiDB("wiki.db")
    main(pathWikiXML, db)

