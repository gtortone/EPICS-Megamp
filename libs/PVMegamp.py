
# conversion functions
# for FineGain, PoleZero and CFDWidth
#
# LV: Logical Value     (Megamp side)
# PV: Physical Value    (IOC side)

def FineGainLV(pvalue):
  return(int((pvalue - 1)/0.015707))

def FineGainPV(lvalue):
  return(float(int(lvalue)*0.015707) + 1)

def PoleZeroLV(pvalue):
  return(int((2000-pvalue)/7.6469))

def PoleZeroPV(lvalue):
  return(2000-float(int(lvalue)*7.6469)) 

def CFDWidthLV(pvalue):
  return(int((pvalue-200) * 0.3175))

def CFDWidthPV(lvalue):
  return(float(int(lvalue)/0.3175 + 200))

# IOC PV schema:        MEGAMP:
# module  PV schema:    MEGAMP:Mm:label
# channel PV schema:    MEGAMP:Mm:Cc:label

def addStaticPVs(db, MAlist):
  mdict = {}
  # static PVs
  MAlist.sort()
  mdict['MOD:SEL'] = {'type': 'enum', 'enums': list(map(str, MAlist)), 'value': 0, 'min': 0, 'max': len(MAlist)-1, 'name': 'MOD:SEL' }
  mdict['COPY:MOD:SRC'] = { 'type': 'enum', 'enums': list(map(str, MAlist)), 'value': 0, 'min': 0, 'max': len(MAlist)-1, 'name': 'COPY:MOD:SRC' }
  mdict['COPY:MOD:DEST'] = { 'type': 'enum', 'enums': list(map(str, MAlist)), 'value': 0, 'min': 0, 'max': len(MAlist)-1, 'name': 'COPY:MOD:DEST' }
  mdict['COPY:CH:SRC'] = { 'type': 'int', 'value': 0, 'min': 0, 'max': 15, 'name': 'COPY:CH:SRC' }
  mdict['COPY:CH:DEST'] = { 'type': 'int', 'value': 0, 'min': 0, 'max': 65535, 'name': 'COPY:CH:DEST' }
  mdict['COPY'] = { 'type': 'int', 'value': 0, 'name': 'COPY' }
  mdict['COPY:RESULT'] = { 'type': 'char', 'count': 256, 'name': 'COPY:RESULT' }
  mdict['COPY:RESULT:STATUS'] = { 'type': 'enum', 'enums': [ "SUCCESS", "ERROR", "WARNING", "IN PROGRESS" ], 'value': 0, 'name': 'COPY:RESULT:STATUS' }
  mdict['FILE:0'] = { 'type': 'string', 'name': 'FILE:0' }
  mdict['FILE:1'] = { 'type': 'string', 'name': 'FILE:1' }
  mdict['FILE:2'] = { 'type': 'string', 'name': 'FILE:2' }
  mdict['FILE:3'] = { 'type': 'string', 'name': 'FILE:3' }
  mdict['FILE:4'] = { 'type': 'string', 'name': 'FILE:4' }
  mdict['FILE:5'] = { 'type': 'string', 'name': 'FILE:5' }
  mdict['FILE:PREVGROUP'] = { 'type': 'int', 'value': 0, 'name': 'FILE:PREVGROUP' }
  mdict['FILE:NEXTGROUP'] = { 'type': 'int', 'value': 0, 'name': 'FILE:NEXTGROUP' }
  mdict['FILE:LOAD'] = { 'type': 'int', 'value': 0, 'min': 0, 'max': 4, 'name': 'FILE:LOAD' }
  mdict['FILE:SAVE'] = { 'type': 'int', 'value': 0, 'min': 0, 'max': 5, 'name': 'FILE:SAVE' }
  mdict['FILE:RESULT:0'] = { 'type': 'char', 'count': 256, 'name': 'FILE:RESULT:0' }
  mdict['FILE:RESULT:1'] = { 'type': 'char', 'count': 256, 'name': 'FILE:RESULT:1' }
  mdict['FILE:RESULT:2'] = { 'type': 'char', 'count': 256, 'name': 'FILE:RESULT:2' }
  mdict['FILE:RESULT:3'] = { 'type': 'char', 'count': 256, 'name': 'FILE:RESULT:3' }
  mdict['FILE:RESULT:STATUS'] = { 'type': 'enum', 'enums': [ "SUCCESS", "ERROR", "WARNING", "IN PROGRESS" ], 'value': 0, 'name': 'FILE:RESULT:STATUS' }
  mdict['M0'] = { 'type': 'enum', 'enums': [ "OFFLINE", "ONLINE" ], 'value': 0, 'name': 'M0' }
  mdict['M1'] = { 'type': 'enum', 'enums': [ "OFFLINE", "ONLINE" ], 'value': 0, 'name': 'M1' }
  mdict['M2'] = { 'type': 'enum', 'enums': [ "OFFLINE", "ONLINE" ], 'value': 0, 'name': 'M2' }
  mdict['M3'] = { 'type': 'enum', 'enums': [ "OFFLINE", "ONLINE" ], 'value': 0, 'name': 'M3' }
  mdict['M4'] = { 'type': 'enum', 'enums': [ "OFFLINE", "ONLINE" ], 'value': 0, 'name': 'M4' }
  mdict['M5'] = { 'type': 'enum', 'enums': [ "OFFLINE", "ONLINE" ], 'value': 0, 'name': 'M5' }
  mdict['M6'] = { 'type': 'enum', 'enums': [ "OFFLINE", "ONLINE" ], 'value': 0, 'name': 'M6' }
  mdict['M7'] = { 'type': 'enum', 'enums': [ "OFFLINE", "ONLINE" ], 'value': 0, 'name': 'M7' }
  mdict['M8'] = { 'type': 'enum', 'enums': [ "OFFLINE", "ONLINE" ], 'value': 0, 'name': 'M8' }
  mdict['M9'] = { 'type': 'enum', 'enums': [ "OFFLINE", "ONLINE" ], 'value': 0, 'name': 'M9' }
  mdict['M10'] = { 'type': 'enum', 'enums': [ "OFFLINE", "ONLINE" ], 'value': 0, 'name': 'M10' }
  mdict['M11'] = { 'type': 'enum', 'enums': [ "OFFLINE", "ONLINE" ], 'value': 0, 'name': 'M11' }
  mdict['M12'] = { 'type': 'enum', 'enums': [ "OFFLINE", "ONLINE" ], 'value': 0, 'name': 'M12' }
  mdict['M13'] = { 'type': 'enum', 'enums': [ "OFFLINE", "ONLINE" ], 'value': 0, 'name': 'M13' }
  mdict['M14'] = { 'type': 'enum', 'enums': [ "OFFLINE", "ONLINE" ], 'value': 0, 'name': 'M14' }
  mdict['M15'] = { 'type': 'enum', 'enums': [ "OFFLINE", "ONLINE" ], 'value': 0, 'name': 'M15' }
  mdict['M0:STATUS'] = { 'type': 'string', 'name': 'M0:STATUS' }
  mdict['M1:STATUS'] = { 'type': 'string', 'name': 'M1:STATUS' }
  mdict['M2:STATUS'] = { 'type': 'string', 'name': 'M2:STATUS' }
  mdict['M3:STATUS'] = { 'type': 'string', 'name': 'M3:STATUS' }
  mdict['M4:STATUS'] = { 'type': 'string', 'name': 'M4:STATUS' }
  mdict['M5:STATUS'] = { 'type': 'string', 'name': 'M5:STATUS' }
  mdict['M6:STATUS'] = { 'type': 'string', 'name': 'M6:STATUS' }
  mdict['M7:STATUS'] = { 'type': 'string', 'name': 'M7:STATUS' }
  mdict['M8:STATUS'] = { 'type': 'string', 'name': 'M8:STATUS' }
  mdict['M9:STATUS'] = { 'type': 'string', 'name': 'M9:STATUS' }
  mdict['M10:STATUS'] = { 'type': 'string', 'name': 'M10:STATUS' }
  mdict['M11:STATUS'] = { 'type': 'string', 'name': 'M11:STATUS' }
  mdict['M12:STATUS'] = { 'type': 'string', 'name': 'M12:STATUS' }
  mdict['M13:STATUS'] = { 'type': 'string', 'name': 'M13:STATUS' }
  mdict['M14:STATUS'] = { 'type': 'string', 'name': 'M14:STATUS' }
  mdict['M15:STATUS'] = { 'type': 'string', 'name': 'M15:STATUS' }
  db.update(mdict)

def addModulePVs(db, module):
  mdict = {}
  # MultiplicityThreshold
  mdict['M' + str(module) + ':' + 'MultiplicityThreshold'] = {
          'type': 'int', 'value': 0,
          'MAmod': module, 'MAch': 16, 'MAaddr': 0, 'min': 0, 'max': 4095, 'name': 'MultiplicityThreshold'
  }
  # TACRange
  mdict['M' + str(module) + ':' + 'TACRange'] = {
          'type': 'int', 'value': 0,
          'MAmod': module, 'MAch': 16, 'MAaddr': 1, 'min': 0, 'max': 4095, 'name': 'TACRange'
  }
  # module name
  mdict['M' + str(module) + ':' + 'NAME'] = {
          'type': 'string', 
          'MAmod': module, 'MAch': 16, 'name': 'NAME'
  }
  db.update(mdict)

def addChannelPVs(db, module, channel):
  mdict = {}
  # InputPolarity
  mdict['M' + str(module) + ':' + 'C' + str(channel) + ':' + 'InputPolarity'] = {
          'type': 'enum', 'enums': ['neg', 'pos'], 'value': 0,
          'MAmod': module, 'MAch': channel, 'MAaddr': 0, 'bitmask': 0x01, 'min': 0, 'max': 1, 'name': 'InputPolarity'
  }
  # ShapingTime
  mdict['M' + str(module) + ':' + 'C' + str(channel) + ':' + 'ShapingTime'] = {
          'type': 'enum', 'enums': ['norm 3', 'norm 0.5', 'fast 3', 'fast 0.5'], 'unit': 'us', 'value': 0,
          'MAmod': module, 'MAch': channel, 'MAaddr': 0, 'bitmask': 0x06, 'min': 0, 'max': 3, 'name': 'ShapingTime'
  }
  # CoarseGain 
  mdict['M' + str(module) + ':' + 'C' + str(channel) + ':' + 'CoarseGain'] = {
          'type': 'enum', 'enums': ['1x', '4x', '16x', '64x'], 'value': 0,
          'MAmod': module, 'MAch': channel, 'MAaddr': 0, 'bitmask': 0x18, 'min': 0, 'max': 3, 'name': 'CoarseGain'
  }
  # CoarseGainTime
  mdict['M' + str(module) + ':' + 'C' + str(channel) + ':' + 'CoarseGainTime'] = {
          'type': 'enum', 'enums': ['4x', '1x'], 'value': 0,
          'MAmod': module, 'MAch': channel, 'MAaddr': 0, 'bitmask': 0x20, 'min': 0, 'max': 1, 'name': 'CoarseGainTime'
  }
  # CFD
  mdict['M' + str(module) + ':' + 'C' + str(channel) + ':' + 'CFD'] = {
          'type': 'enum', 'enums': ['enable', 'disable'], 'value': 0,
          'MAmod': module, 'MAch': channel, 'MAaddr': 0, 'bitmask': 0x40, 'min': 0, 'max': 1, 'name': 'CFD'
  }
  # OR
  mdict['M' + str(module) + ':' + 'C' + str(channel) + ':' + 'OR'] = {
          'type': 'enum', 'enums': ['enable', 'disable'], 'value': 0,
          'MAmod': module, 'MAch': channel, 'MAaddr': 0, 'bitmask': 0x80, 'min': 0, 'max': 1, 'name': 'OR'
  }
  # FineGain
  mdict['M' + str(module) + ':' + 'C' + str(channel) + ':' + 'FineGain'] = {
          'type': 'float', 'value': 1, 'prec': 2,
          'MAmod': module, 'MAch': channel, 'MAaddr': 1, 'min': 1, 'max': 4, 'name': 'FineGain'
  }
  # PoleZero
  mdict['M' + str(module) + ':' + 'C' + str(channel) + ':' + 'PoleZero'] = {
          'type': 'int', 'value': 0, 'unit': 'us',
          'MAmod': module, 'MAch': channel, 'MAaddr': 2, 'min': 50, 'max': 2000, 'name': 'PoleZero'
  }
  # CFDWidth
  mdict['M' + str(module) + ':' + 'C' + str(channel) + ':' + 'CFDWidth'] = {
          'type': 'int', 'value': 0, 'unit': 'ns',
          'MAmod': module, 'MAch': channel, 'MAaddr': 3, 'min': 200, 'max': 600, 'name': 'CFDWidth'
  }
  # CFDThreshold
  mdict['M' + str(module) + ':' + 'C' + str(channel) + ':' + 'CFDThreshold'] = {
          'type': 'int', 'value': 0,
          'MAmod': module, 'MAch': channel, 'MAaddr': 4, 'min': 0, 'max': 4095, 'name': 'CFDThreshold'
  }
  # output enable
  mdict['M' + str(module) + ':' + 'C' + str(channel) + ':' + 'OUT'] = {
          'type': 'int', 'value': 0,
          'MAmod': module, 'MAch': channel, 'min': 0, 'max': 1, 'name': 'OUT'
  }
  db.update(mdict)
