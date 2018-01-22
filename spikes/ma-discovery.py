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

MAlist = [ ]

for i in range(0,16):
    try:
        value = MA.read(module=i, channel=0, address=0)
    except Exception as e:
        e
    else:
        MAlist.append(i)

print(MAlist)
