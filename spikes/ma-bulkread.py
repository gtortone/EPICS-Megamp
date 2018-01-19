#!/usr/bin/python3

import megamp

MA = megamp.Megamp("/dev/ttyUSB1", 115200, 0.5)

for m in range(1,6):
    for i in range(0,17):
        try:
            values = MA.bulkread(module=m, channel=i)
        except Exception as e:
            print(e)
        else:
            print(values)


