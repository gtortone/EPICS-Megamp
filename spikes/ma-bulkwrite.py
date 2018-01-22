#!/usr/bin/python3

import sys
sys.path.append('../libs')

import megamp

MA = megamp.Megamp("/dev/ttyUSB0", 115200, 0.5)

for i in range(0,5):
    try:
        MA.bulkwrite(module=i, channel=3, values=[i,i,i,i,i])
    except Exception as e:
        print(e)
