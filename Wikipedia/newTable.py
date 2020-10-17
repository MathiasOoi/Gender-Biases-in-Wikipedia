import zlib
import time
from wikidb import *
from func_timeout import func_set_timeout
from collections import defaultdict

import wikitextparser as wtp

def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)

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

def getInfobox(page):
    article = wtp.parse(page)
    infobox = getTemplate(article, "Infobox")
    return infobox

def removeNotes(s):
    """
    text <--! note
    Remove everything past the <!--
    """
    try:
        return s[:s.index("<!--")]
    except ValueError:
        return s

def getGender(page):
    male, mc = ["he", "him", "his"], 0
    female, fc = ["her", "she", "hers"], 0

    for word in page.split():
        if word in male:
            mc += 1
        elif word in female:
            fc += 1

    return "male" if mc > fc else "female"

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

@func_set_timeout(10)
def parsePage(article):
    try:
        infobox = getInfobox(article)
        if infobox is None:
            return
        infobox = infobox[infobox.find("\n") + 1: infobox.rfind("\n")]
        if infobox.count("\n") == 0: return
        notParsed = infobox
        infobox = wtp.Table(infobox)
    except AttributeError:
        return

        # Iterate over every cell and parse it
    d = defaultdict(list)
    try:
        for a in range(len(infobox.cells())):
            for b in range(len(infobox.cells(row=a))):
                parsed = parseCell(str(infobox.cells(row=a, column=b)))
                d[parsed[0]] = parsed[1]
    except IndexError:
        return

    gender = getGender(article)
    args = repr(list(zip(d.keys(), (sum(len(k) for k in i) for i in d.values()))))
    chars = len(article)

    return chars, gender, args, notParsed
def main():
    newdb = WikiDBWithGenderAndInfobox2("wikiWithArgCharCount2.db")
    db = WikiDB("wiki.db")
    pageCount = 0
    noinfobox = 0
    othererror = 0
    start_time = time.time()
    for (pageid, title, categories, article) in db:
        pageCount += 1
        if not pageCount % 100000:
            elapsed_time = time.time() - start_time
            print("{} articles parsed".format((pageCount / 100000) * 100000), end=" ")
            print("Elapsed time: {}".format(hms_string(elapsed_time)))
        try:
            x = parsePage(article)
        except BaseException as e:
            print(e)
            othererror += 1
            continue
        if x:
            chars, gender, args, infobox = x
            newdb.insert(pageid, title, categories, chars, gender, args, infobox)
        else:
            noinfobox += 1
    newdb.commit()
    elapsed_time = time.time() - start_time

    print("Elapsed time: {}".format(hms_string(elapsed_time)))
    print(noinfobox)
    print(othererror)

if __name__ == '__main__':
    main()