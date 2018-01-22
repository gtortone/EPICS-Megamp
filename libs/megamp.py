import serial
import re

class MegampError(Exception):
    """Base class for other exceptions"""
    pass

class MegampSerialOpenError(MegampError):
    """Raised if a serial port open error occours"""
    pass

class MegampSerialWriteError(MegampError):
    """Raised if a serial write error occours"""
    pass

class MegampSerialReadError(MegampError):
    """Raised if a serial read error occours"""
    pass

class MegampProtocolResultError(MegampError):
    """Raised if a protocol error *ERR occours"""
    pass

class MegampProtocolUnknownError(MegampError):
    """Raised if an unknown protocol error occours"""
    pass

class MegampProtocolParseError(MegampError):
    """Raised if a protocol parse error occours"""
    pass

class MegampFunctionArgumentError(MegampError):
    """Raised if a method argument error occours"""
    pass

class Megamp():

    def __init__(self, port, speed, tout):

        self.port = port
        self.speed = speed

        try:
            self.ser = serial.Serial(port, speed, timeout=tout)
        except:
            raise MegampSerialOpenError("Megamp serial port error, opening " + port + " with speed " + speed)

        # read some data to empty serial buffer
        self.ser.readline()
        self.ser.readline()
        self.ser.readline()

    def read(self, module, channel, address):

        cmd = '*' + str(module).zfill(2) + 'C' + str(channel).zfill(2) + 'A' + str(address).zfill(2) + '\r'

        try:
            self.ser.write(cmd.encode('utf-8'))
        except:
            raise MegampSerialWriteError("Megamp serial port write error: " + cmd)

        try:
            line = self.ser.readline().decode('utf-8')
        except:
            raise MegampSerialReadError("Megamp serial port read error: " + line)

        matchobj = re.match('\*OK(\d*)', line)

        if (matchobj):
            return(matchobj.group(1))
        elif re.match('\*ERR', line):
            raise MegampProtocolResultError("Megamp protocol error *ERR: " + line)
        else:
            raise MegampProtocolParseError("Megamp protocol parse error: " + line)

    def bulkread(self, module, channel):

        cmd = '*' + str(module).zfill(2) + 'C' + str(channel).zfill(2) + 'R' + '\r'

        try:
            self.ser.write(cmd.encode('utf-8'))
        except:
            raise MegampSerialWriteError("Megamp serial port write error: " + cmd)

        try:
            line = self.ser.readline().decode('utf-8')
        except:
            raise MegampSerialReadError("Megamp serial port read error: " + line)

        if channel != 16:
            matchobj = re.match('\*OK(\d*),(\d*),(\d*),(\d*),(\d*)', line)
        else:
            matchobj = re.match('\*OK(\d*),(\d*)', line)

        if (matchobj):
            if channel != 16:
                return [ matchobj.group(1), matchobj.group(2), matchobj.group(3), matchobj.group(4), matchobj.group(5) ]
            else:
                return [ matchobj.group(1), matchobj.group(2) ]
        elif re.match('\*ERR', line):
            raise MegampProtocolResultError("Megamp protocol error *ERR: " + line)
        else:
            raise MegampProtocolParseError("Megamp protocol parse error: " + line)
 
    def write(self, module, channel, address, value):

        cmd = '*' + str(module).zfill(2) + 'C' + str(channel).zfill(2) + 'A' + str(address).zfill(2) + ',' + str(value) + '\r'

        try:
            self.ser.write(cmd.encode('utf-8'))
        except:
            raise MegampSerialWriteError("Megamp serial port write error: " + cmd)

        try:
            line = self.ser.readline().decode('utf-8')
        except:
            raise MegampSerialReadError("Megamp serial port read error: " + line)

        matchobj = re.match('\*OK', line)

        if (matchobj):
            return(True)
        elif re.match('\*ERR', line):
            raise MegampProtocolResultError("Megamp protocol error *ERR: " + line)
        else:
            raise MegampProtocolParseError("Megamp protocol parse error: " + line)

    def bulkwrite(self, module, channel, values):

        if channel != 16:
            if(len(values) != 5):
                raise MegampFunctionArgumentError("Megamp bulkwrite argument error: " + str(len(values)) + " arguments instead of 5")
            else:
                cmd = '*' + str(module).zfill(2) + 'C' + str(channel).zfill(2) + 'W' + str(values[0]) + ',' + str(values[1]) + ',' + str(values[2]) + ',' + str(values[3]) + ',' + str(values[4]) + '\r'
        else:
            if(len(values) != 2):
                raise MegampFunctionArgumentError("Megamp bulkwrite argument error: " + str(len(values)) + " arguments instead of 2")
            else:
                cmd = '*' + str(module).zfill(2) + 'C' + str(channel).zfill(2) + 'W' + str(values[0]) + ',' + str(values[1]) + '\r'

        try:
            self.ser.write(cmd.encode('utf-8'))
        except:
            raise MegampSerialWriteError("Megamp serial port write error: " + cmd)

        try:
            line = self.ser.readline().decode('utf-8')
        except:
            raise MegampSerialReadError("Megamp serial port read error: " + line)

        matchobj = re.match('\*OK', line)

        if (matchobj):
            return(True)
        elif re.match('\*ERR', line):
            raise MegampProtocolResultError("Megamp protocol error *ERR: " + line)
        else:
            raise MegampProtocolParseError("Megamp protocol parse error: " + line)
