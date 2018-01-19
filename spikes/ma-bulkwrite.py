#!/usr/bin/python3

import megamp

MA = megamp.Megamp("/dev/ttyUSB3", 115200, 0.5)

for i in range(1,6):
    try:
        MA.bulkwrite(module=i, channel=3, values=[i,i,i,i,i])
    except Exception as e:
        print(e)
