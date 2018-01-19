#!/usr/bin/python3

import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)

ser.readline()
ser.readline()
ser.readline()

ch = 0
i = 0

while (i < 10000):

  ser.write(("*1C" + str(ch) + "R" + '\r').encode('utf-8')) 
  print(ser.readline())
  
  if ch == 16:
      ch = 0
  else:
      ch = ch + 1

  i = i + 1
