import io
import sys
import math
import ctypes 
import yaml

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
  def __init__(self, port, speed):
    self.pvdb = {}
    self.pvinit = []    # contains PVs initialized - only first time (bus read and PV write)
    self.MAlist = []
    self.MAlistname = []
    self.mod_attrlist = ['NAME', 'MultiplicityThreshold', 'TACRange'] 
    self.mod_attrhelp = [ 'module name', 'range: 0...4095', 'range: 0...4095']
    self.ch_attrlist = [ 'InputPolarity', 'ShapingTime', 'CoarseGain', 'CoarseGainTime', 'CFD', 'OR', 'FineGain', 'PoleZero', 'CFDWidth', 'CFDThreshold' ]
    self.ch_attrhelp = [ '0=negative, 1=positive', '0=3us, 1=0.5us, 2=3us Fast, 3=0.5us Fast', '0=1x, 1=4x, 2=16x, 3=64x', '0=4x, 1=1x', '0=enable, 1=disable', 
            '0=enable, 1=disable', 'range: 1.0...4.0, unit: X', 'range: 50...2000, unit: us', 'range: 200...600, unit: ns', 'range: 0....4095, unit: mV' ]
    self.fileindex = 1  # first five filenames in setup directory
    self.filelist = []

    try:
      self.MA = megamp.Megamp(port, speed, 0.5)
    except Exception as e:
      print("ERROR: initialization of serial bus failed")
      sys.exit(1)

    self.allocatePVs()

    if(not self.MAlist):
      print("ERROR: no Megamp module available - maybe serial is not available ?")
      sys.exit(1)
    else:
      print("INFO: Megamp modules discovered: " + str(self.MAlist))

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
    self.filelist = [f for f in listdir("setup") if isfile(join("setup", f)) and (not f.startswith('.'))]
    self.filelist.sort()

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
      self.cleanResults()
      return(True)

    if self.pvdb[reason]['name'] == 'FILE:SAVE':
      print("Saving file: " + str(pvalue))
      self.cleanResults()
      contents = self.dumpYAML()
      f = open("setup/" + str(pvalue), 'w')
      f.write(str(contents))
      f.close()
      return(True)

    self.setParam(reason, pvalue)       # default action
    return(True)

  def cleanResults(self):
    self.write("FILE:RESULT:0", "")
    self.write("FILE:RESULT:1", "")
    self.write("FILE:RESULT:2", "")
    self.write("FILE:RESULT:3", "")

  def dumpYAML(self):
    output = io.StringIO()
    for m in self.MAlist:
      output.write('M' + str(m) + ':\n')
      # module attributes
      for m_a in range(0,len(self.mod_attrlist)):
        attr = self.mod_attrlist[m_a]
        helpmsg = self.mod_attrhelp[m_a]
        key = 'M' + str(m) + ':' + str(attr)
        output.write('  ' + str(attr) + ': ' + str(self.read(key)) + ' # ' + str(helpmsg) + '\n')
        #print(str(key) + ' - ' + str(self.read(key)))
      for c in range(0,16):
        output.write('  C' + str(c) + ':\n')
        # channel attributes
        for c_a in range(0,len(self.ch_attrlist)):
          attr = self.ch_attrlist[c_a]
          helpmsg = self.ch_attrhelp[c_a]
          key = 'M' + str(m) + ':C' + str(c) + ':' + str(attr)
          output.write('    ' + str(attr) + ': ' + str(self.read(key)) + ' # ' + str(helpmsg) + '\n')
          #print(str(key) + ' - ' + str(self.read(key)))
      output.write('\n')

    #print(output.getvalue())
    return(output.getvalue())

