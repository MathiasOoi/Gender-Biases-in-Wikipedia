from wikidb import *
from collections import defaultdict

def getInfoboxPercentage(infobox, *args):
    pass

def frequentCategories(filename):
    db = WikiDB(filename)
    d = defaultdict(int)
    total = 0

    for categories in db.iterCatergories():
        categories = categories[0].split(",")
        categories[0] = categories[0].strip("[")
        categories[-1] = categories[-1].strip("]")
        total += len(categories)
        for c in categories:
            d[c.strip(" ").strip("'")] += 1
    print(d)
    d = {k: v for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)}
    for i, top in enumerate(d):
        if i > 9: break
        print("{}. {} {} out of {}".format(i, top, d[top], total))


frequentCategories("wiki.db")



