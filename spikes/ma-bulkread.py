#!/usr/bin/python3

import sys
sys.path.append('../libs')

import megamp

MA = megamp.Megamp("/dev/ttyUSB0", 115200, 0.5)

for m in range(0,5):
    print("MODULE = " + str(m))
    for i in range(0,17):
        try:
            values = MA.bulkread(module=m, channel=i)
        except Exception as e:
            print(e)
        else:
            print(values)


