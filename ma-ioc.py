#!/usr/bin/python3

from libs import iocDriver
from optparse import OptionParser

from pcaspy import SimpleServer
from pprint import pprint

prefix = 'MEGAMP:'
pvdb = { 'STATIC': {} }

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

driver = iocDriver.myDriver(port, speed)
server = SimpleServer()

server.createPV(prefix, driver.getPVdb())
driver.start()

# print(driver.getPVdb())

while True:
  server.process(1)
