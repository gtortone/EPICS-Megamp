#!/usr/bin/python3

import megamp

MA = megamp.Megamp("/dev/ttyUSB3", 115200, 0.5)

for i in range(0,17):
    for j in range(0,5):
        try:
            MA.write(module=1, channel=i, address=j, value=42)
        except Exception as e:
            print(e)

try:
    MA.bulkwrite(module=1, channel=3, values=[10,20,30,40,50])
except Exception as e:
    print(e)

try:
    MA.bulkwrite(module=1, channel=16, values=[88,99])
except Exception as e:
    print(e)

