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
