#!/usr/bin/python3

import os

filelist = [f for f in os.listdir("../setup") if os.path.isfile(os.path.join(os.path.abspath("../setup"), f))]

print(filelist)

print(os.listdir("../setup"))
