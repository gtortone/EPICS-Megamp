#!/usr/bin/python3

import megamp

MA = megamp.Megamp("/dev/ttyUSB1", 115200, 0.5)

for i in range(0,17):
    for j in range(0,5):
        try:
            value = MA.read(module=1, channel=i, address=j)
        except Exception as e:
            print(e)
        else:
            print("M = 1, CH = " + str(i) + " ADDR = " + str(j) + " value = " + value)

for i in range(0,17):
    try:
        values = MA.bulkread(module=1, channel=i)
    except Exception as e:
        print(e)
    else:
        print(values)


