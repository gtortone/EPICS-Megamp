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

if(options.speed):
  speed = options.speed

print("Megamp serial parameter: port = " + port + " speed = " + str(speed))

MA = megamp.Megamp(port, speed, 0.5)

for i in range(0,5):
    try:
        MA.bulkwrite(module=i, channel=3, values=[i,i,i,i,i])
    except Exception as e:
        print(e)
