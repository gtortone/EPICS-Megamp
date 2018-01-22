#!/usr/bin/python3

import sys
sys.path.append('../libs')

import megamp

MA = megamp.Megamp("/dev/ttyUSB0", 115200, 0.5)

for i in range(0,17):
    for j in range(0,5):
        try:
            value = MA.read(module=0, channel=i, address=j)
        except Exception as e:
            print(e)
        else:
            print("M = 0, CH = " + str(i) + " ADDR = " + str(j) + " value = " + value)

for i in range(0,17):
    try:
        values = MA.bulkread(module=0, channel=i)
    except Exception as e:
        print(e)
    else:
        print(values)


