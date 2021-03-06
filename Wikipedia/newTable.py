import time
from collections import defaultdict
from typing import Tuple, List

import wikitextparser as wtp
from func_timeout import func_set_timeout

from wikidb import *
from profiling import *
from wikiparse import hms_string

def getTemplate(page: wtp._wikitext.WikiText, template: str) -> str:
    """
    Given a parsed article return the string of given template key
    Templates start like {{template key ...}}
    :param page: parsed page object
    :param template: Template key
    :return: Template
    """
    for tm in page.templates:
        tm = str(tm)
        if tm.split("\n")[0].strip("{").startswith(template):
            return tm

def getInfobox(page: str) -> str:
    """
    Finds the template associated with infobox
    :param page: String of entire article
    :return: Template of infobox
    """
    article = wtp.parse(page)
    infobox = getTemplate(article, "Infobox")
    return infobox

def removeNotes(s: str) -> str:
    """
    Remove notes from infobox (key, value)
    :param s: Infobox (key, value) "| key     = value"
    :return: s with notes removed
    """
    if "<!--" in s: return s[:s.index("<!--")]
    return s

def getGender(page: str) -> str:
    """
    Gets the gender of some article by doing a simple pro noun count
    :param page: String of page
    :return: "male" | "female"
    """
    male, mc = ["he", "him", "his"], 0
    female, fc = ["her", "she", "hers"], 0

    for word in page.split():
        if word.lower() in male:
            mc += 1
        elif word.lower() in female:
            fc += 1

    if mc > fc:
        return "M"
    elif mc < fc:
        return "F"
    else:
        return "D"

@func_set_timeout(10)
def parsePage(article: str) -> Tuple[int, str]:
    """
    Parses an article and returns desired values
    :param article:
    :return:
    """
    chars, gender, infobox = len(article), getGender(article), getInfobox(article)
    return chars, gender, infobox if infobox else None

def main():
    newdb = WikiInfobox("/mnt/data/mathias/WikiInfoboxRevised.db")
    source = WikiDB("/mnt/data/mathias/wikidb.db")
    pageCount = 0
    error = 0
    noinfobox = 0
    start_time = time.time()
    for (pageid, title, categories, article) in source:
        pageCount += 1
        if not pageCount % 100000:
            elapsed_time = time.time() - start_time
            print("{} articles parsed".format((pageCount / 100000) * 100000), end=" ")
            print("Elapsed time: {}".format(hms_string(elapsed_time)))
        try:
            x = parsePage(article)
        except BaseException as e:
            error += 1
            continue
        if x[2]:
            chars, gender, infobox = x
            newdb.insert(pageid, title, categories, chars, gender, infobox)
        else:
            noinfobox += 1
    newdb.commit()
    elapsed_time = time.time() - start_time

    print("Elapsed time: {}".format(hms_string(elapsed_time)))
    print(error)
    print(noinfobox)
if __name__ == '__main__':
    main()
