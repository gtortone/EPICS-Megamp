#!/usr/bin/python3

import epics
import time

pvdb = {}

def onChanges(pvname=None, value=None, char_value=None, **kw):
   #print("PV Changed! {} {} {}".format(pvname, char_value, time.ctime()))
   pvdb[pvname] = char_value

mypv = epics.PV('MEGAMP:MOD:SEL')
mypv.add_callback(onChanges)

print("Now wait for changes")

t0 = time.time()
while time.time() - t0 < 60.0:
    time.sleep(1.e-3)
    if pvdb.get('MEGAMP:MOD:SEL') != None:
       print(pvdb["MEGAMP:MOD:SEL"])
print("Done")
