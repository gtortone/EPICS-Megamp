#!/usr/bin/python3

import sys
sys.path.append('../libs')

import megamp

MA = megamp.Megamp("/dev/ttyUSB0", 115200, 0.5)

MAlist = [ ]

for i in range(0,16):
    try:
        value = MA.read(module=i, channel=0, address=0)
    except Exception as e:
        e
    else:
        MAlist.append(i)

print(MAlist)
