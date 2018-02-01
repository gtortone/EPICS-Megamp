#!/usr/bin/python3

from optparse import OptionParser

import sys
sys.path.append('../libs')
import megamp

port = "/dev/ttyUSB0"
speed = 115200

parser = OptionParser()
parser.add_option("-p", action="store", type="string", dest="port", help="specify Megamp serial port (e.g. /dev/ttyUSB0)")
parser.add_option("-s", action="store", type="string", dest="speed", help="set Megamp serial port speed (e.g. 9600)")
(options, args) = parser.parse_args()

if(options.port):
  port = options.port
else:
  if(os.environ.get("MA_PORT")):
    port = os.environ.get("MA_PORT")

if(options.speed):
  speed = options.speed
else:
  if(os.environ.get("MA_SPEED")):
    speed = os.environ.get("MA_SPEED")

print("Megamp serial parameter: port = " + port + " speed = " + str(speed))

MA = megamp.Megamp(port, speed, 0.5)

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

