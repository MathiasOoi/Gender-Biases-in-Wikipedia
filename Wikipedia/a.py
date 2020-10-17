import ast
import time
from wikidb import *
from newTable import hms_string
from collections import defaultdict
from wikiparse import getTemplate
import wikitextparser as wtp

def getHeight(page):
    infobox = getTemplate(page, "Infobox")
    if infobox is None:
        return
    infobox = infobox[infobox.find("\n") + 1: infobox.rfind("\n")]
    if infobox.count("\n") == 0:  # One line infobox creates an infinite loop
        return
    infobox = wtp.Table(infobox)


with open("sample.txt") as fin:
    page = fin.read()
