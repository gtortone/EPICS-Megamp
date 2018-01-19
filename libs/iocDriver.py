
import math
import ctypes 

from libs import PVMegamp
from libs import megamp
from os import listdir
from os.path import isfile, join
from pcaspy import SimpleServer, Driver, Alarm, Severity

import ctypes
c_uint8 = ctypes.c_uint8

class Flags_bits( ctypes.LittleEndianStructure ):
    _fields_ = [
                ("InputPolarity",   c_uint8, 1 ),
                ("ShapingTime",     c_uint8, 2 ),
                ("CoarseGain",      c_uint8, 2 ),
                ("CoarseGainTime",  c_uint8, 1 ),
                ("CFD",             c_uint8, 1 ),
                ("OR",              c_uint8, 1 ),
               ]

class Flags( ctypes.Union ):
    _anonymous_ = ("bit",)
    _fields_ = [
                ("bit",    Flags_bits ),
                ("asByte", c_uint8    )
               ]

class myDriver(Driver):
  def __init__(self):
    self.pvdb = {}
    self.pvinit = []    # contains PVs initialized - only first time (bus read and PV write)
    self.MAlist = []
    self.MAlistname = []
    self.fileindex = 1  # first five filenames in setup directory
    self.filelist = []

    self.MA = megamp.Megamp("/dev/ttyUSB2", 115200, 0.5)
    self.allocatePVs()
    self.updateFilelist()

  def discoveryModules(self):
    for i in range(0,16):
      try:
        value = self.MA.read(module=i, channel=0, address=0)
      except Exception as e:
        e
      else:
        self.MAlist.append(i)

    self.MAlistname = [str('M' + str(m)) for m in self.MAlist]

  def allocatePVs(self):
    self.discoveryModules()

    PVMegamp.addStaticPVs(db=self.pvdb,MAlist=self.MAlist)

    for i in self.MAlist:
      PVMegamp.addModulePVs(db=self.pvdb, module=i)
      for j in range(0,16):
        PVMegamp.addChannelPVs(db=self.pvdb, module=i, channel=j)

  def initPV(self, pv):
    self.pvinit.append(pv)
    try:
      lvalue = self.MA.read(module=self.pvdb[pv]['MAmod'], channel=self.pvdb[pv]['MAch'], address=self.pvdb[pv]['MAaddr'])
    except Exception as e:
      print(e)
    else:
      if(hasattr(PVMegamp, self.pvdb[pv]['name'] + "PV")):  # a conversion function exists...
        func = getattr(PVMegamp, self.pvdb[pv]['name'] + "PV")
        if 'prec' in self.pvdb[pv]:
            fstr = "{:." + str(self.pvdb[pv]['prec']) + "f}"
            pvalue = float(fstr.format(func(lvalue)))  # float("{:.2f}".format(orig_float)) 
        else:
          pvalue = func(lvalue)
      else:
        pvalue = int(lvalue)

      self.setParamStatus(pv, Alarm.NO_ALARM, Severity.NO_ALARM)
      self.setParam(pv, pvalue)

  def initPVflags(self, pv):
    try:
      lvalue = self.MA.read(module=self.pvdb[pv]['MAmod'], channel=self.pvdb[pv]['MAch'], address=0) 
    except Exception as e:
      print(e)
    else:
      flags = Flags()
      flags.asByte = int(lvalue)
      pvprefix = 'M' + str(self.pvdb[pv]['MAmod']) + ':C' + str(self.pvdb[pv]['MAch']) + ':'

      pvname = pvprefix + "InputPolarity"
      self.setParamStatus(pvname, Alarm.NO_ALARM, Severity.NO_ALARM)
      self.setParam(pvname, flags.InputPolarity)
      self.pvinit.append(pvname)

      pvname = pvprefix + "ShapingTime"
      self.setParamStatus(pvname, Alarm.NO_ALARM, Severity.NO_ALARM)
      self.setParam(pvname, flags.ShapingTime)
      self.pvinit.append(pvname)

      pvname = pvprefix + "CoarseGain"
      self.setParamStatus(pvname, Alarm.NO_ALARM, Severity.NO_ALARM)
      self.setParam(pvname, flags.CoarseGain)
      self.pvinit.append(pvname)

      pvname = pvprefix + "CoarseGainTime"
      self.setParamStatus(pvname, Alarm.NO_ALARM, Severity.NO_ALARM)
      self.setParam(pvname, flags.CoarseGainTime)
      self.pvinit.append(pvname)

      pvname = pvprefix + "CFD"
      self.setParamStatus(pvname, Alarm.NO_ALARM, Severity.NO_ALARM)
      self.setParam(pvname, flags.CFD)
      self.pvinit.append(pvname)

      pvname = pvprefix + "OR"
      self.setParamStatus(pvname, Alarm.NO_ALARM, Severity.NO_ALARM)
      self.setParam(pvname, flags.OR)
      self.pvinit.append(pvname)

  def updateFilelist(self):
    self.filelist = [f for f in listdir("setup") if isfile(join("setup", f))]
    self.filelist.sort()
    print(self.filelist)

  def updateFilePVs(self):
    for i in range(0,5):
      try:
        self.setParam("FILE:" + str(i), self.filelist[self.fileindex + i - 1])
      except IndexError:
        self.setParam("FILE:" + str(i), "")
    self.updatePVs()
        
  def start(self):
    Driver.__init__(self)   # must be called after SimpleServer creation 
    self.updateFilePVs()

  def getPVdb(self):
    return self.pvdb

  def read(self, reason):
    if ('MAaddr' in self.pvdb[reason]) and (not reason in self.pvinit):   # if PV is linked to serial bus and not initialized yet...
      if (self.pvdb[reason]['MAaddr'] == 0) and (self.pvdb[reason]['MAch'] != 16):  # Megamp address 0 fills multiple PVs...
        self.initPVflags(reason) 
      else:
        self.initPV(reason)

    return(self.getParam(reason))

  def write(self, reason, pvalue):
    # check PV range
    if 'min' in self.pvdb[reason]:
      if pvalue < self.pvdb[reason]['min'] or pvalue > self.pvdb[reason]['max']:
        return(True)

    if 'MAaddr' in self.pvdb[reason]:
      if (self.pvdb[reason]['MAaddr'] == 0) and (self.pvdb[reason]['MAch'] != 16):
        self.initPVflags(reason)              
        curvalue = self.MA.read(module=self.pvdb[reason]['MAmod'], channel=self.pvdb[reason]['MAch'], address=0)
        flags = Flags()
        flags.asByte = int(curvalue)
        setattr(flags,self.pvdb[reason]['name'],pvalue)
        lvalue = flags.asByte
      elif(hasattr(PVMegamp, self.pvdb[reason]['name'] + "LV")):  # a conversion function exists...
        func = getattr(PVMegamp, self.pvdb[reason]['name'] + "LV")
        lvalue = math.ceil(func(pvalue))
      else:
        lvalue = pvalue

      try:
        self.MA.write(module=self.pvdb[reason]['MAmod'], channel=self.pvdb[reason]['MAch'], address=self.pvdb[reason]['MAaddr'], value=lvalue)
      except Exception as e:
        print(e)
        return(False)
      else:
        self.setParam(reason, pvalue)
        return(True)

    if self.pvdb[reason]['name'] == "OUT":  # output enable
      try:
        self.MA.read(module=self.pvdb[reason]['MAmod'], channel=self.pvdb[reason]['MAch'], address=1)
      except Exception as e:
        print(e)
        return(False)
      else:
        return(True)

    if self.pvdb[reason]['name'] == 'FILE:NEXTGROUP':
      if(len(self.filelist) >= self.fileindex + 5):
        self.fileindex = self.fileindex + 5
        self.updateFilePVs()
        return(True)

    if self.pvdb[reason]['name'] == 'FILE:PREVGROUP':
      if(self.fileindex - 5 > 0):
        self.fileindex = self.fileindex - 5
        self.updateFilePVs()
        return(True)

    if self.pvdb[reason]['name'] == 'FILE:LOAD':
      print("Loading file: " + str(pvalue))
      return(True)

    self.setParam(reason, pvalue)       # default action
    return(True)

