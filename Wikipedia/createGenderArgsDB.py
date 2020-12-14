import sqlite3
import re
from collections import defaultdict
from wikidb import WikiInfoboxArgs, GenderArgs

top = defaultdict(lambda: defaultdict(int))
to_check = ["birth", "death"]  # Special arg cases

for (_, _, _, _, gender, name, _) in WikiInfoboxArgs("/mnt/data/mathias/WikiInfoboxArgs.db"):
    for s in to_check:
        # Groups special cases together
        # e.g. "birth_date" and "birth_name" go into "birth"
        if name.startswith(s):
            top[gender][s] += 1
            break
    if any(name.startswith(s) for s in to_check): continue
    m = re.search(r"\d+$", name)  # Find args with trailing digits
    if m:
        # Group case1 and case2 into case
        top[gender][name[:m.span()[0]-1]] += 1
    else:
        top[gender][name] += 1

dash = "-"*50
db = GenderArgs("/mnt/data/mathias/GenderArgs.db")
for gender, data in top.items():
    data = sorted(data.items(), key=lambda x: -x[1])  # Sorts (arg, count) by decreasing count
    # print(dash)
    # print(gender.upper())
    for (i, (k, v)) in enumerate(data):
        db.insert(gender, k, v)
    #    print("{:<2} {:<15} {}".format(i+1, k, v))
db.commit()

