import time

import wikitextparser as wtp

from wikidb import WikiInfobox, WikiInfoboxArgs
from wikiparse import hms_string

def main():
    source = WikiInfobox("/mnt/data/mathias/WikiInfobox.db")
    newdb = WikiInfoboxArgs("/mnt/data/mathias/WikiInfoboxArgs.db")
    start = time.time()
    pageCount = 0
    for pageid, title, categories, chars, gender, infobox in source:
        pageCount += 1
        for arg in wtp.Template(infobox).arguments:
            name, value = arg.name.strip(), arg.value.strip()
            if value:
                newdb.insert(pageid, title, categories, chars, gender, name, value)
        if not pageCount % 100000:
            print("{} articles parsed".format(pageCount), end=" ")
            print("Elapsed time: {}".format(hms_string(time.time()-start)))
    newdb.commit()
    print(hms_string(time.time()-start))
    return


if __name__ == '__main__':
    main()
