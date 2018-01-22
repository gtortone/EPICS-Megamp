#!/usr/bin/python3

import sys
sys.path.append('../libs')

import os
import yaml

MAlist = [ '1', '2' ]

file = open('../setup/first.yaml', 'r')

try:
  doc = yaml.safe_load(file)
except Exception as e:
  print(e)

print(yaml.dump(doc))

print(doc.keys())
print(doc['M1'].keys())
print(doc['M1']['C0'].keys())

MAlistname = [str('M' + m) for m in MAlist]
print(MAlistname)

sa = set(doc.keys())
sb = set(MAlistname)
c = sa.intersection(sb)

print(list(c))
