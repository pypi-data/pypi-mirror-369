import threading
import errno
import socket
import serial
from .Transport import Transport
from termcolor import colored



class SerialTransport(Transport):
    def __init__(self, port, baud=115200, stopbits=serial.STOPBITS_ONE, 
                 databits=serial.EIGHTBITS, parity=serial.PARITY_NONE, callback=None): 
        super().__init__(callback)
        
        self.port = port
        self.baud = baud
        self.opened = False
        self._running = True  # Add flag for clean shutdown
        
        try:
            self.serialPort = serial.Serial(
                port=port,
                baudrate=baud,
                parity=parity,
                stopbits=stopbits,
                bytesize=databits,
                timeout=0.1  # Add timeout to prevent blocking
            )
            self.opened = True
            print(f"Opened {port} at {baud} baud")
            self.serialPort.flushInput()
            self.serialPort.flushOutput()
            self.start()
        except serial.SerialException as e:
            print(f"Failed to open {port} at {baud} baud: {e}")

    def __del__(self):
        self.close()
        self.join()

    def close(self):
        self._running = False
        if self.opened:
            self.serialPort.close()
            self.opened = False

    def send(self, data):
        if self.opened:
            try:
                bytes_written = self.serialPort.write(data)
                self.serialPort.flush()  # Ensure data is sent
                return bytes_written
            except serial.SerialException as e:
                print(f"Error sending data: {e}")
                self.close()
                return 0

    def run(self):
        if not self.opened:
            return
            
        while self._running:
            try:
                # Read in chunks instead of single bytes
                data = self.serialPort.read(64)
                if data:
                    if self.callback:
                        self.callback(data)
            except serial.SerialException as e:
                print(f"Error reading from serial port: {e}")
                self.close()
                break


serialConnectionHelp = """

    Invalid serial connection string.

    serial:/dev/ttyUSB0:115200
    serial:/dev/ttyUSB0:115200-E-8-1
"""

def parseSerialConnectionString(connString):
    """
    Parse a serial connection string and return a dictionary of the parameters

    Examples: 
        SERIAL:/dev/ttyUSB0:115200  
        SERIAL:/dev/ttyUSB0:115200-E-8-1

    """
    try:

        
        parts = connString.split(":")


        port = parts[1]
        baud = 115200
        stopbits = serial.STOPBITS_ONE
        databits = serial.EIGHTBITS
        parity = serial.PARITY_NONE

        if len(parts) > 2:
            params = parts[2].split("-")
            baud = int(params[0])

            if len(params) > 1:
                if params[1] == 'E':
                    parity = serial.PARITY_EVEN
                elif params[1] == 'O':
                    parity = serial.PARITY_ODD
                elif params[1] == 'N':
                    parity = serial.PARITY_NONE

            if len(params) > 2:
                databits = int(params[2])
            
            if len(params) > 3:
                stopbits = int(params[3])


        out = {
            'port': port,
            'baud': baud,
            'stopbits': stopbits,
            'databits': databits,
            'parity': parity
        }

        return out
    except:
        return None
