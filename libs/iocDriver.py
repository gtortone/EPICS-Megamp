import io
import sys
import math
import yaml
import threading

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
    self.tid = None
    self.mutex = threading.Lock()

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
      print("INFO: Megamp modules detected: " + str(self.MAlist))

    self.updateFilelist()

  def detectModules(self):
    for i in range(0,16):
      self.mutex.acquire()
      try:
        value = self.MA.read(module=i, channel=0, address=0)
      except Exception as e:
        e
      else:
        self.MAlist.append(i)
      finally:
        self.mutex.release()

    self.MAlistname = [str('M' + str(m)) for m in self.MAlist]

  def allocatePVs(self):
    self.detectModules()

    PVMegamp.addStaticPVs(db=self.pvdb,MAlist=self.MAlist)

    for i in self.MAlist:
      self.pvdb["M" + str(i)]["value"] = 1  # set module online
      self.pvdb["M" + str(i) + ":STATUS"]["value"] = "Local EEPROM"
      PVMegamp.addModulePVs(db=self.pvdb, module=i)
      for j in range(0,16):
        PVMegamp.addChannelPVs(db=self.pvdb, module=i, channel=j)

  def initPV(self, pv):
    self.pvinit.append(pv)
    self.mutex.acquire()
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
    finally:
      self.mutex.release()

  def initPVflags(self, pv):
    self.mutex.acquire()
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
    finally:
      self.mutex.release()

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
        #raise ValueError("value out of range")
        return(True)

    if 'MAaddr' in self.pvdb[reason]:
      if (self.pvdb[reason]['MAaddr'] == 0) and (self.pvdb[reason]['MAch'] != 16):
        self.initPVflags(reason)
        self.mutex.acquire()
        curvalue = self.MA.read(module=self.pvdb[reason]['MAmod'], channel=self.pvdb[reason]['MAch'], address=0)
        self.mutex.release()
        flags = Flags()
        flags.asByte = int(curvalue)
        setattr(flags,self.pvdb[reason]['name'],pvalue)
        lvalue = flags.asByte
      elif(hasattr(PVMegamp, self.pvdb[reason]['name'] + "LV")):  # a conversion function exists...
        func = getattr(PVMegamp, self.pvdb[reason]['name'] + "LV")
        lvalue = math.ceil(func(pvalue))
      else:
        lvalue = pvalue

      self.mutex.acquire()
      try:
        self.MA.write(module=self.pvdb[reason]['MAmod'], channel=self.pvdb[reason]['MAch'], address=self.pvdb[reason]['MAaddr'], value=lvalue)
      except Exception as e:
        print(e)
        return(False)
      else:
        self.setParam(reason, pvalue)
        return(True)
      finally:
        self.mutex.release()

    if self.pvdb[reason]['name'] == "OUT":  # output enable
      self.mutex.acquire()
      try:
        self.MA.read(module=self.pvdb[reason]['MAmod'], channel=self.pvdb[reason]['MAch'], address=1)
      except Exception as e:
        print(e)
        return(False)
      else:
        return(True)
      finally:
        self.mutex.release()

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
      filename = self.getParam("FILE:" + str(pvalue))
      
      if not filename:
        return(True)
      
      self.cleanResults()
      self.setParam("FILE:RESULT:0", "Setup filename: " + str(filename))
      self.updatePVs()

      print("INFO: Loading file: " + str(filename))
      errstr = "Errors: "

      try:
        f = open("setup/" + str(filename), 'r')
      except Exception as e:
        errstr = errstr + str(e)
        self.setParam("FILE:RESULT:STATUS", 1)  # error
        self.setParam("FILE:RESULT:2", errstr)
        return(True)

      try:
        doc = yaml.safe_load(f)
      except Exception as e:
        errstr = errstr + str(e)
        self.setParam("FILE:RESULT:2", errstr)
        f.close()
        return(True)

      f.close()
      if(not(type(doc) is dict)):
        errstr = errstr + "file format error"
        self.setParam("FILE:RESULT:STATUS", 1)  # error
        self.setParam("FILE:RESULT:2", errstr)
        self.updatePVs()
        return(True)
      
      MAset_infile = set(doc.keys())
      MAset_incrate = set(self.MAlistname)
      MAset_tosetup = sorted(MAset_infile.intersection(MAset_incrate))
      MAset_infile = sorted(MAset_infile)   # convert a set to a sorted list
      MAset_incrate = sorted(MAset_incrate)
      print("INFO: Modules loaded from file: " + str(MAset_infile))
      print("INFO: Modules available in the crate: " + str(MAset_incrate))
      print("INFO: Modules to setup: " + str(MAset_tosetup))

      if(len(MAset_tosetup) == 0):
        print("INFO: no modules to setup")
        errstr = errstr + "Setup warning - Setup not restored from file"
        msg = "FILE contains(" + str(MAset_infile) + ") "
        msg = msg + " while CRATE contains(" + str(MAset_incrate) + ")"
        self.setParam("FILE:RESULT:STATUS", 2)  # warning
        self.setParam("FILE:RESULT:0", "Setup filename: " + str(filename))
        self.setParam("FILE:RESULT:1", msg)
        self.setParam("FILE:RESULT:2", errstr)
        self.updatePVs()
        return(True)
      
      print("INFO: Start loading from file " + filename + "...")
      self.setParam("FILE:RESULT:STATUS", 3)  # in progress...
      self.tid = threading.Thread(target=self.restoreModules,args=(MAset_incrate,doc,filename,))
      self.tid.start()

      self.updatePVs()
      return(True)

    if self.pvdb[reason]['name'] == 'FILE:SAVE':
      errstr = ""
      filename =  self.getParam("FILE:" + str(pvalue))
      if filename:
        print("INFO: Start saving to file: " + str(filename))
        self.cleanResults()
        self.updatePVs()
        self.setParam("FILE:RESULT:STATUS", 3)  # in progress...
        self.updatePVs()
        contents = self.dumpYAML()
        try:
          f = open("setup/" + str(filename), 'w')
        except Exception as e:
          errstr = errstr + str(e)
        else:
          f.write(str(contents))
          f.close()

        self.setParam("FILE:RESULT:0", "Setup filename: " + str(filename))
        self.setParam("FILE:RESULT:1", "MEGAMP modules saved: " + str(self.MAlistname))
        if(errstr):
          self.setParam("FILE:RESULT:STATUS", 1)  # error
          self.setParam("FILE:RESULT:2", "Errors: some errors occour")
          self.setParam("FILE:RESULT:1", errstr)
        else:
          self.setParam("FILE:RESULT:STATUS", 0)  # success
          self.setParam("FILE:RESULT:2", "Errors: none")
        
        self.setParam("FILE:SAVE", 0)
        self.setParam("FILE:5", "")
        self.updateFilelist()
        self.updateFilePVs()
      return(True)

    if self.pvdb[reason]['name'] == 'COPY':
      print("INFO: Start channel copy...")
      self.setParam("COPY:RESULT:STATUS", 3)  # in progress
      self.setParam("COPY:RESULT", "")
      self.updatePVs()
      msrc = self.getParam("COPY:MOD:SRC")
      mdest = self.getParam("COPY:MOD:DEST")
      csrc = self.getParam("COPY:CH:SRC")
      cdest = self.getParam("COPY:CH:DEST")

      self.setParam("FILE:RESULT:STATUS", 3)  # in progress...
      self.tid = threading.Thread(target=self.copyChannels,args=(msrc,csrc,mdest,cdest,))
      self.tid.start()

      self.updatePVs()
      return(True)

    self.setParam(reason, pvalue)       # default action
    self.updatePVs()
    return(True)

  def cleanResults(self):
    self.setParam("FILE:RESULT:0", "")
    self.setParamStatus("FILE:RESULT:0", Alarm.NO_ALARM, Severity.NO_ALARM)
    self.setParam("FILE:RESULT:1", "")
    self.setParamStatus("FILE:RESULT:1", Alarm.NO_ALARM, Severity.NO_ALARM)
    self.setParam("FILE:RESULT:2", "")
    self.setParamStatus("FILE:RESULT:2", Alarm.NO_ALARM, Severity.NO_ALARM)
    self.setParam("FILE:RESULT:3", "")
    self.setParamStatus("FILE:RESULT:3", Alarm.NO_ALARM, Severity.NO_ALARM)
    self.setParam("FILE:RESULT:STATUS", 0)  # success
    self.updatePVs()

  def dumpYAML(self):
    output = io.StringIO()
    for m in self.MAlist:
      output.write('M' + str(m) + ':\n')
      # module attributes
      for m_a in range(0,len(self.mod_attrlist)):
        attr = self.mod_attrlist[m_a]
        helpmsg = self.mod_attrhelp[m_a]
        key = 'M' + str(m) + ':' + str(attr)
        value = self.read(key)
        if(attr == "NAME" and len(str(value)) == 0):
          value = str('""')
        output.write('  ' + str(attr) + ': ' + str(value) + ' # ' + str(helpmsg) + '\n')
        #print(str(key) + ' - ' + str(self.read(key)))
      for c in range(0,16):
        output.write('  C' + str(c) + ':\n')
        # channel attributes
        for c_a in range(0,len(self.ch_attrlist)):
          attr = self.ch_attrlist[c_a]
          helpmsg = self.ch_attrhelp[c_a]
          key = 'M' + str(m) + ':C' + str(c) + ':' + str(attr)
          value = self.read(key)
          output.write('    ' + str(attr) + ': ' + str(value) + ' # ' + str(helpmsg) + '\n')
          #print(str(key) + ' - ' + str(self.read(key)))
      output.write('\n')

    #print(output.getvalue())
    return(output.getvalue())

  # restore modules 'mset' from yaml data 'doc' get from 'filename'
  def restoreModules(self, mset, doc, filename):
    errstr = ""
    for m in mset:
      if m in doc.keys():
        # module attributes
        for m_a in range(0,len(self.mod_attrlist)):
          attr = self.mod_attrlist[m_a]
          if attr in doc[m].keys():
            key = str(m) + ':' + str(attr)
            value = doc[m][attr]
            try:
              self.write(key, value)
            except Exception as e:
              errstr += "Attribute " + str(m) + ":" + str(attr) + " - " + str(e) + "\n"
          else:
            errstr += ("Attribute " + str(m) + ":" + str(attr) + " - missing in setup file\n")
        for c in range(0,16):
          c = 'C' + str(c)
          if c in doc[m].keys():
            # channel attributes
            for c_a in range(0,len(self.ch_attrlist)):
              attr = self.ch_attrlist[c_a]
              if attr in doc[m][c].keys():
                key = str(m) + ':' + str(c) + ':' + str(attr)
                value = doc[m][c][attr]
                if value < self.pvdb[key]['min'] or value > self.pvdb[key]['max']:
                  errstr += "Attribute " + str(m) + ":" + str(c) + ":" + str(attr) + " - " + " out of range\n"
                else:
                  self.write(key, value)
              else:
                errstr += ("Attribute " + str(m) + ":" + str(c) + ":" + str(attr) + " - missing in setup file\n")
          else:
            errstr += ("Channel " + str(m) + ":" + str(c) + " - missing in setup file\n")
        self.setParam(str(m + ":STATUS"), str("From file " + filename))
      else:
        errstr += ("Module " + str(m) + " - missing in setup file\n")
    
    print("INFO: File load finished")
    print(errstr)
    
    if(errstr):
      self.setParam("FILE:RESULT:STATUS", 2)  # warning
      self.setParam("FILE:RESULT:2", "Errors: some errors occour")
      self.setParam("FILE:RESULT:1", errstr)
    else:
      self.setParam("FILE:RESULT:STATUS", 0)  # success
      self.setParam("FILE:RESULT:2", "Errors: none")

    self.callbackPV('FILE:LOAD')
    self.updatePVs()
    self.tid = None 

  # copy channels attributes from msrc:csrc to mdest:cbdest ('cbdest' is a channel bitmask)
  def copyChannels(self, msrc, csrc, mdest, cbdest):
    mask = 1
    err = 0
    for i in range(0,16):
      if(cbdest & mask):
        err += self.copyChannel(msrc, csrc, mdest, i)
      mask = mask << 1
    if(err > 0):
      self.setParam("COPY:RESULT:STATUS", 1)  # error
      self.setParam("COPY:RESULT", "Copy ERROR")
    else:
      self.setParam("COPY:RESULT:STATUS", 0)  # success
      self.setParam("COPY:RESULT", "Copy OK")
    
    print("INFO: Copy completed")
    self.setParam("COPY:CH:DEST", 0)

    self.callbackPV('COPY')
    self.updatePVs()
    self.tid = None

  # copy channel attributes from msrc:csrc to mdest:cdest
  def copyChannel(self, msrc, csrc, mdest, cdest):
    err = 0
    srcprefix = str('M' + str(msrc) + ':' + 'C' + str(csrc) + ':')
    destprefix = str('M' + str(mdest) + ':' + 'C' + str(cdest) + ':')
    for c_a in range(0,len(self.ch_attrlist)):
      pvsrc = srcprefix + str(self.ch_attrlist[c_a])
      pvdest = destprefix + str(self.ch_attrlist[c_a])
      if(pvsrc != pvdest):  # skip source channel
        try:
          self.write(pvdest, self.read(pvsrc))
        except Exception as e:
          print(e)
          err = 1
    self.updatePVs()
    return(err)


      
        

