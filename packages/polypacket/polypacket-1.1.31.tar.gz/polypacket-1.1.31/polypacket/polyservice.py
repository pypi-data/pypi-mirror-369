#!/usr/bin/python3
#
#@file polyservice.py
#@brief python module to run a command line utility for a protocol
#@author Jason Berger
#@date 02/19/2019
#

import sys
import pkgutil
import subprocess
from polypacket.protocol import *
from collections import deque
from cobs import cobs
import struct
import random
import threading
import errno
import socket
import serial
import json
import websockets
import websocket
import asyncio
from polypacket.transport.SerialTransport import *
from polypacket.transport.TcpTransport import *




def packVarSize(value):
    bytes = bytearray([])
    tmp =0
    size =0

    while( value > 0):
        tmp = value & 0x7F
        value = value >> 7
        if value > 0:
            tmp |= 0x80
        bytes.append(tmp)

    if len(bytes) == 0:
        bytes.append(0)

    return bytes

def readVarSize(bytes):
    tmp =0
    val =0
    size =0

    for i in range(4):
        tmp = bytes[i]
        size+= 1
        val = val << 7
        val |= tmp & 0x7F
        if (tmp & 0x80) == 0:
            break

    return int(val), int(size)

class BasePacket:
    """"
        Base class for packet classes generated with poly-make
    """
    def __init__(self, packetType ):
        self._packetType = packetType

    def toPacket(self, protocol):
        packet = PolyPacket(protocol)


        if self._packetType in protocol.packetIdx:
            typeId = protocol.packetIdx[self._packetType]
        else:
            raise Exception("Packet Type \"" + self._packetType + "\", not found!")
    
        packet.build(typeId)
        packet.setFields(self.__dict__)

        return packet

class PolyField:
    def __init__(self, desc):
        self.desc = desc
        self.id = desc.id
        self.isPresent = False
        self.values = [-1]
        self.len = 0

    def set(self,val):
        self.isPresent = True


        if isinstance(val,bytes): 
            self.values = []
            for i in range(len(val)):
                self.values.append(int(val[i]))
            self.len = len(val)
            return


        if not isinstance(val, str):
            val = str(val)

        if val in self.desc.valDict:
            self.len = 1
            self.values[0] = self.desc.valDict[val]
        else:
            if self.desc.isArray and not self.desc.isString:
                val = val.replace('[','').replace(']','')
                arrVal = val.split(',')
                self.len = len(arrVal)
                self.values = []
                for v in arrVal:
                    self.values.append( int(v, 0))
            else:
                if self.desc.isString:
                    self.len = len(val)
                    self.values[0] = val

                elif self.desc.isMask and '|' in val:
                    self.len = 1
                    self.values[0] = 0
                    arrVals = val.split('|')
                    for v in arrVals:
                        v = v.strip()
                        if v in self.desc.valDict:
                            self.values[0] = self.values[0] | self.desc.valDict[v]
                else:
                    self.len = 1
                    self.values[0] = int(val, 0)


    def copyTo(self, field ):
        field.values = self.values
        field.isPresent = self.isPresent 
        field.len = self.len 

    def get(self):
        if self.isPresent :
            if self.desc.isArray and not self.desc.isString :
                return self.values
            else:
                return self.values[0]
        else:
            return -1

    def parse(self, bytes):
        self.isPresent = True
        strFormat = "%s"+ self.desc.pyFormat
        idx =0
        if self.desc.isArray and not self.desc.isString:
            self.len, idx = readVarSize(bytes)
            self.len = int(self.len / self.desc.objSize)
        else:
            if self.desc.isString:
                self.len, idx = readVarSize(bytes)
            else:
                self.len = 1

        if self.len == 0:
            if self.desc.isString:
                self.values[0] =""
            else:
                self.values[0] = 0

        dataLen = int(self.len * self.desc.objSize)

        strFormat = "<" + str(self.len) + self.desc.pyFormat;

        try:
            if self.desc.isString:
                self.values[0] = struct.unpack(strFormat, bytes[idx:idx+dataLen ])[0].decode("utf-8")
            else:
                self.values = struct.unpack(strFormat, bytes[idx:idx+dataLen])
        except:
            print(strFormat)
            print(idx)
            print (dataLen)
            print(len(bytes))
            print(" Error Parsing: " + self.desc.name+ '-->' + ''.join(' {:02x}'.format(x) for x in bytes[idx:idx+dataLen]))
        return idx + dataLen

    def pack(self, id):
        byteArr = bytes([])

        strFormat = "<" + str(self.len)+ self.desc.pyFormat

        byteArr += packVarSize(id)

        if self.desc.isArray :
            byteArr += packVarSize(self.len * self.desc.objSize)


        if self.desc.isString:
            byteArr+= struct.pack("<" +str(self.len) + "s", self.values[0].encode('utf-8'))
        else:
            byteArr+= struct.pack(strFormat, *self.values)

        return byteArr

    def toJSON(self):
        json =""
        json += "\"" + self.desc.name +"\" : "
        if self.desc.isArray and not self.desc.isString:
            json+= "[" + ''.join(' 0x{:02x},'.format(x) for x in self.values) + "]"
        else:
            if self.desc.isString :
                json+= "\"" + str(self.values[0]) +"\""
            elif self.desc.format == 'FORMAT_HEX':
                json+= "0x" + '{:02x}'.format(self.values[0])
            else:
                json+= str(self.values[0])

        return json

class PolyPacket:
    def __init__(self, protocol, type = None ):
        self.protocol : protocolDesc = protocol
        self.fields  = []
        self.seq =0
        self.dataLen = 0
        self.token = random.randint(1, 32767)
        self.checksum = 0
        self.typeId = 0
        self.packet_handler = ''
        self.autoAck = True
        self.ackFlag = False
        self.sent = False #used to mark if a packet has already been sent and is being reused

    def setField(self, fieldName, value):
        for field in self.fields:
            if fieldName.lower() == field.desc.name.lower():
                field.set(value)
                break

    def getField(self, fieldName):
        for field in self.fields:
            if fieldName.lower() == field.desc.name.lower():
                return field.get()
        return -1
    
    def toBasePacket(self):
        basePacket = BasePacket(self.desc.extName())
        for field in self.fields:
            val = field.get()
            if type(val) == tuple:
                val = list(val)
            setattr(basePacket, field.desc.name, val)
        return basePacket
    
    def checkFieldFlag(self, fieldName, flags):

        #get flag value
        flagMask = 0
        field = None

        if type(flags) == str:
            flags = [flags]


        for field in self.fields:
            if fieldName.lower() == field.desc.name.lower():
                field = field
                for flag in flags:
                    if flag in field.desc.flagMap:
                        flagMask |= field.desc.flagMap[flag]
                break

        
        if field == None or not field.isPresent:
            return False
        
        return (field.values[0] & flagMask) == flagMask

            
    def hasField(self, fieldName):
        for field in self.fields:
            if fieldName.lower() == field.desc.name.lower():
                if (field.isPresent):
                    return True
        return False

    def setFields(self, dict):
        for key, value in dict.items():
            if value != None:
                self.setField(key,value)

    def build(self, typeId):
        self.typeId = typeId
        self.desc = self.protocol.structsAndPackets[typeId]
        for fieldDesc in self.desc.fields:
            self.fields.append( PolyField(fieldDesc))

    def copyTo(self, packet):
        for field in self.fields:
                for dstField in packet.fields:
                    if(field.isPresent):
                        if(dstField.desc.name.lower() == field.desc.name.lower()):
                            field.copyTo(dstField)
        return 0

    def handler(self, iface):

        #dont respond to acks
        if self.ackFlag:
            if self.desc.extName() in iface.service.handlers:
                iface.service.handlers[self.desc.extName()](iface.service,self,None )
            elif 'default' in iface.service.handlers:
                iface.service.handlers['default'](iface.service, self,None)
            return 0

        if not iface.service.autoAck:
            return 0

        resp = 0

        if self.desc.hasResponse:
            resp =  iface.service.newPacket(self.desc.response.extName())
        elif iface.service.autoAck:
            resp = iface.service.newPacket('Ack')
        
        #acks responding to pings get an icd field
        if self.typeId == 0:
                resp.setField('icd', str(self.protocol.crc))

        if self.desc.extName() in iface.service.handlers:
            iface.service.handlers[self.desc.extName()](iface.service,self,resp)
        elif self.desc.name in iface.service.handlers:
            iface.service.handlers[self.desc.name](iface.service,self,resp)
        elif 'default' in iface.service.handlers:
            iface.service.handlers['default'](iface.service, self,resp)
        else:
            pass
            #iface.service.print(f"No handler for {self.desc.extName()}/{self.desc.name}")



        if not resp == 0:
            resp.ackFlag = True
            resp.token = self.token | 0x8000

        return resp

    def parse(self, rawBytes):
        self.raw = rawBytes
        idx =0
        #pull in header
        self.typeId = rawBytes[0]
        self.seq = rawBytes[1]
        self.dataLen = (rawBytes[3] << 8) | rawBytes[2]
        self.token =   (rawBytes[5] << 8) | rawBytes[4]
        if rawBytes[5] & 0x80:
            self.ackFlag = True
        self.checksum =   (rawBytes[7] << 8) | rawBytes[6]

        idx = 8

        #look up desc
        self.build(self.typeId)

        #parse fields
        while idx < (len(rawBytes)-1):
            fieldId, varLenSize = readVarSize(rawBytes[idx:])
            idx+= varLenSize
            idx+= self.fields[fieldId].parse(rawBytes[idx:])


        return True

    def pack(self):
        byteArr =  bytes([])
        dataArr = bytes([])
        self.checksum = 1738

        for i,field in enumerate(self.fields):
            if field.isPresent:
                dataArr += field.pack(i)

        for dat in dataArr:
            self.checksum += dat

        #simulate uint16_t overflow 
        self.checksum = self.checksum & 0xFFFF

        self.dataLen = len(dataArr)


        byteArr = struct.pack('<BBHHH', self.typeId, self.seq, self.dataLen, self.token, self.checksum)
        self.raw = byteArr + dataArr


        return self.raw

    def toJSON(self, meta= False):
        json = ""
        #json += ''.join(' {:02x}'.format(x) for x in self.raw) + "\n"
        json +="{ \"packetType\" : \""+ self.desc.name + "\""

        if meta:
            json+= ", \"typeId\": "  + str(self.typeId)
            json+= ", \"token\": \"" + '{:04x}'.format(self.token) + "\""
            json+= ", \"checksum\": \"" + '{:04x}'.format(self.checksum) + "\""
            json+= ", \"len\": "  + str(self.dataLen) + " "


        for field in self.fields:
            if field.isPresent:
                json+= ", " + field.toJSON()

        json += "}"
        return json

class PolyStruct(PolyPacket):
    pass

class PolyIface:
    def __init__(self, connStr, service):
        self.connStr = connStr
        self.service = service
        self.bytesIn = deque([])
        self.frameCount =0
        self.packetsIn = deque([])
        self.name = ""
        self.lastToken = 0
        self.connType = None
        self.sendCallback = None
        self.transport = None


        if not connStr == "":

            parts = connStr.split(":")

            type = parts[0].upper()


            if type == "SERIAL":

                params = parseSerialConnectionString(connStr)
                if params:
                    self.transport = SerialTransport( **params, callback=self.feedEncodedBytes)
                    
                else:
                    print(serialConnectionHelp)
                    return False

            elif type == "TCP":

                params = parseTcpConnectionString(connStr)
                if params:
                    self.transport = TcpTransport( params['localPort'], self.feedEncodedBytes)
                    if params['remoteHost']:
                        self.transport.connect(params['remoteHost'], params['remotePort'])
                        self.connected = True
                    else:
                        self.transport.listen()
                else:
                    print(tcpConnectionHelp)
                    return False

                pass
            
                    
    def close(self):
        if hasattr(self, 'coms'):
            self.transport.close()

    def setSendCallback(self, callback):
        self.sendCallback = callback

    def print(self, text):
        if not self.service.print == '':
            self.service.print( text)

    def isConnected(self): 

        if self.connType == "TCP":
            return self.transport.opened
        elif self.connType == "UDP":
            if self.transport.host != 0:
                return True
        elif self.connType == "SERIAL":
            return self.transport.opened
        
        return False

    def feedEncodedBytes(self, encodedBytes):

        silent = False

        for i in encodedBytes:
            self.bytesIn.append(i)
            if i == 0:
                self.frameCount +=1

        while self.frameCount > 0:
            encodedPacket = bytes([])
            newPacket = PolyPacket(self.service.protocol)
            while(1):
                x = self.bytesIn.popleft()
                if x == 0:
                    self.frameCount -=1
                    break
                else:
                    encodedPacket+= bytes([x])

            #print(f"Encoded Frame: {encodedPacket}")

            decoded = cobs.decode(encodedPacket)

            try:
                newPacket.parse(decoded)
            except Exception  as e:
                self.print( "Exception: " +str(e))
                
            if self.service.silenceAll or self.service.silenceDict[newPacket.desc.name] :
                silent = True

            if not silent:
                if self.service.showBytes:
                    self.print(" PARSE HDR: " + ''.join(' {:02x}'.format(x) for x in decoded[:8]))
                    self.print(" PARSE DATA: " + ''.join(' {:02x}'.format(x) for x in decoded[8:]))
                if (newPacket.token & 0x7FFF) != (self.lastToken & 0x7FFF):
                    self.print("")

                self.print( " <-- " + newPacket.toJSON(self.service.showMeta))

            resp = newPacket.handler(self)
            self.lastToken = newPacket.token
            if resp:
                self.sendPacket(resp, silent)
            #self.packetsIn.append(newPacket)

    def sendPacket(self, packet, silent = False):


        #if packet was already sent and is being re-used, assign it a new token
        if packet.sent :
            packet.token = random.randint(1, 32767)

        if self.service.silenceAll or self.service.silenceDict[packet.desc.name]:
            silent = True

        if packet.desc.name == "Ping":
            packet.setField('icd', str(self.service.protocol.crc))


        if not silent:
            if (packet.token & 0x7FFF) != (self.lastToken & 0x7FFF):
                self.print("")

            self.print( " --> " + packet.toJSON(self.service.showMeta))

        raw = packet.pack()

        if self.service.showBytes and not silent:
            self.print(" PACK HDR: " + ''.join(' {:02x}'.format(x) for x in raw[:8]))
            self.print(" PACK DATA: " + ''.join(' {:02x}'.format(x) for x in raw[8:]))

        encoded = cobs.encode(bytearray(raw))
        encoded += bytes([0])




        if self.transport is not None:
            self.transport.send(encoded)
        elif self.sendCallback:
            self.sendCallback(encoded)

        self.lastToken = packet.token
        packet.sent = True

        return encoded


    def getPacket(self):
        if len(packetsIn) > 0:
            return packetsIn.popleft()


def null_print(str):
    pass

class PolyService:
    def __init__(self, protocol):

        #If protocol is just a path to a file, we can build the protocol
        if type(protocol) is str: 
            protocol = buildProtocol(protocol)

        self.protocol : protocolDesc = protocol
        self.interfaces = []
        self.print = null_print
        self.showMeta = False
        self.autoAck = True
        self.handlers = {}
        self.silenceDict = {}
        self.silenceAll = False
        self.showBytes = False
        self.dataStore = {}
        self.defaultInterface : PolyIface = None

        if hasattr(protocol, 'packets'):
            for packet in protocol.packets:
                self.silenceDict[packet.name] = False

        self.addIface("") #add dummy interface that just prints
        self.defaultInterface = self.interfaces[0]

    def setProtocol(self, protocol):
        self.protocol = protocol

        if hasattr(protocol, 'packets'):
            for packet in protocol.packets:
                self.silenceDict[packet.name] = False

    def sendPacket(self,packet , fieldDict = {}, iface = None):
        """Sends a packet on the default interface.

        :param polypacket/str packet: built polypacket, or string with packet type
        :param obj fieldDict: dictionary of fields to set for packet
        :return: token of sent packet
        """

        if self.defaultInterface == None:
            raise Exception("Null interface on PolyService")
        
        if isinstance(packet, str):
            packet = self.newPacket(packet)
        elif isinstance(packet, BasePacket):
            packet = packet.toPacket(self.protocol)
        
        packet.setFields(fieldDict)


        if iface: 
            self.interfaces[iface].sendPacket(packet)
        else:
            #send on all 
            for iface in self.interfaces:
                iface.sendPacket(packet)

        return self.defaultInterface.lastToken
    
    def isConnected(self):

        if self.defaultInterface != None:
            return self.defaultInterface.isConnected()
        
        return False

    def close(self):
        for iface in self.interfaces:
            iface.close()

    def addIface(self, connStr):
        self.interfaces.append(PolyIface(connStr, self))

    def connect(self,connStr):
        self.interfaces[0].close()
        self.interfaces[0] = PolyIface(connStr, self)
        self.defaultInterface = self.interfaces[0]

    def setComms(self, coms):
        self.defaultInterface.coms = coms
        self.defaultInterface.coms.iface = self.defaultInterface


    def toggleAck(self):
        if self.autoAck:
            self.autoAck = False
            self.print( "AutoAck turned OFF")
        else:
            self.autoAck = True
            self.print( "AutoAck turned ON")

    def toggleSilence(self, packetType):

        if not packetType in self.silenceDict:
            self.print( "Can not find: " + packetType)

        if self.silenceDict[packetType]:
            self.silenceDict[packetType] = False
            self.print( "Un-Silencing: " + packetType)
        else:
            self.silenceDict[packetType] = True
            self.print( "Silencing: " + packetType)

    def newPacket(self, type : str, fields = {}) -> PolyPacket:
        packet = PolyPacket(self.protocol)

        # We can get types as "namespace:packetName" or just "packetName"
        # if namespace is not specified, we use the default namespace
        namespace = self.protocol.namespace
        packetName = type 

        if ':' in packetName:
            words = type.split(':')
            namespace = words[0]
            packetName = words[1]
        
        type = namespace + ':' + packetName
        
        if type in self.protocol.packetIdx:
            packet.build(self.protocol.packetIdx[type])
            packet.setFields(fields)
        else:
            self.print(" Packet Type \"" + type + "\", not found!")

        return packet

    def newStruct(self, type):
        struct = PolyPacket(self.protocol)

        if type in self.protocol.structIdx:
            struct.build(self.protocol.structIdx[type])
        else:
            self.print(" Struct Type \"" + type + "\", not found!")

        return struct

    def pack(self, packet: str, fields: dict):
        packet = self.newPacket(packet, fields)
        return packet.pack()
    
    def parse(self, raw: bytes, output: str='json'):
        packet = PolyPacket(self.protocol)
        packet.parse(raw)
        
        if output == 'json':
            return json.loads(packet.toJSON())

        return packet
    
    def addHandler(self, packetType, handler):
        self.handlers[packetType] = handler
        

    #
    # def process(self):
    #     for iface in self.interfaces:
    #         if iface.frameCount > 0:
