#!/usr/bin/python3

from libs import iocDriver

from pcaspy import SimpleServer
from pprint import pprint

prefix = 'MEGAMP:'
pvdb = { 'STATIC': {} }

driver = iocDriver.myDriver()
server = SimpleServer()

server.createPV(prefix, driver.getPVdb())
driver.start()

# print(driver.getPVdb())

while True:
  server.process(1)
