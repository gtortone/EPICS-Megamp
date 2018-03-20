#!/usr/bin/python3

from stat import S_ISREG, ST_CTIME, ST_MODE
import os, sys, time

# get all entries in the directory w/ stats
entries = (os.path.join("../setup", fn) for fn in os.listdir("../setup"))
entries = ((os.stat(path), path) for path in entries)

# leave only regular files, insert creation date
entries = ((stat[ST_CTIME], path)
                   for stat, path in entries if S_ISREG(stat[ST_MODE]))

for cdate, path in sorted(entries, reverse=True):
        print(time.ctime(cdate), os.path.basename(path))
