import ast
import time
from wikidb import *
from newTable import hms_string
from collections import defaultdict
db = WikiDBWithGenderAndInfobox("wikiWithArgCharCount.db")

def top(dict, n, d):
    x = []
    for i, kv in enumerate(dict.items()):
        if i == n: return x
        x.append(kv[0])
    return x


m = defaultdict(int)
f = defaultdict(int)
tm, tf = 0, 0
start = time.time()
for (pageid, title, categories, chars, gender, infoboxArgs) in db:
    infoboxArgs = ast.literal_eval(infoboxArgs)
    t = sum(i[1] for i in infoboxArgs)
    if gender == "male":
        tm += t
        for kv in infoboxArgs:
            if kv[0] == "image" or any(kv[0].startswith(i) for i in ["birth", "death"]): continue
            m[kv[0]] += kv[1]
    else:
        tf += t
        for kv in infoboxArgs:
            if kv[0] == "image" or any(kv[0].startswith(i) for i in ["birth", "death"]): continue
            f[kv[0]] += kv[1]
mtop = top({k: v for k, v in sorted(m.items(), key=lambda item: -item[1])}, 100, tm)
ftop = top({k: v for k, v in sorted(f.items(), key=lambda item: -item[1])}, 100, tf)
print("Elapsed time: {}".format(hms_string(time.time()-start)))

x = []
for key in set(mtop).union(set(ftop)):
    x.append((key, m[key], f[key]))
x = sorted(x, key=lambda tup: -tup[2])
y = sorted(x, key=lambda tup: -tup[1])
for a, b, c in y:
    print("{}: Male:{} Female:{}".format(a, b/tm, c/tf))
print("\n\n")
for a, b, c in x:
    print("{}: Male:{} Female:{}".format(a, b/tm, c/tf))

