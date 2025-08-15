import sys
import xml.etree.ElementTree as ET
import re
import io
import os
import copy
import datetime
import zlib
import argparse
#import pdfkit
from shutil import copyfile
from mako.template import Template
import pkgutil
import polypacket
import subprocess
import yaml
import requests
import validators


sizeDict = {
    "uint8" : 1,
    "int8" : 1,
    "char" : 1,
    "string" : 1,
    "uint16" : 2,
    "int16" : 2,
    "uint32" : 4,
    "int32" : 4,
    "int64" : 8,
    "uint64" : 8,
    "int" : 4,
    "float": 4,
    "double": 8,
}

cNameDict = {
    "uint8" : "uint8_t",
     "int8" : "int8_t",
     "char" : "char",
     "string" : "char",
     "uint16" : "uint16_t",
     "int16" : "int16_t",
     "uint32" : "uint32_t",
     "int32" : "int32_t",
     "int64" : "int64_t",
     "uint64" : "uint64_t",
     "int" : "int",
     "float" : "float",
     "double" : "double",
     "enum" : "uint8_t",
     "flag" : "uint8_t"
 }

pyNameDict = {

    "uint8" : "int",
    "int8" : "int",
    "char" : "str",
    "string" : "str",
    "uint16" : "int",
    "int16" : "int",
    "uint32" : "int",
    "int32" : "int",
    "int64" : "int",
    "uint64" : "int",
    "int" : "int",
    "float" : "float",
    "double" : "float",
    "enum" : "int",
    "flag" : "int"
}



formatDict = {
    "hex" : "FORMAT_HEX",
    "dec" : "FORMAT_DEC",
    "default" : "FORMAT_DEFAULT",
    "ascii" : "FORMAT_ASCII",
    "none" : "FORMAT_NONE"
}

pyFormatDict = {
        "uint8" : "B",
        "int8" : "b",
        "char" : "c",
        "string" : "s",
        "uint16" : "H",
        "int16" : "h",
        "uint32" : "L",
        "int32" : "l",
        "int64" : "q",
        "uint64" : "Q",
        "int" : "l",
        "float": "f",
        "double": "d",
}


def crc(fileName):
    prev = 0
    for eachLine in open(fileName,"rb"):
        prev = zlib.crc32(eachLine, prev)


    return prev,"%X"%(prev & 0xFFFFFFFF)


class agentCommandArg:
    def __init__(self, argItem):
        self.name = ""
        self.desc = ""
        self.handler = ""
        self.default = None

        self.name = list(argItem.keys())[0]
        val = list(argItem.values())[0]

        #check if its a string 
        if type(val) is str:
            self.handler = val
        else:
            if 'desc' in val:
                self.desc = val['desc']

            if 'default' in val:
                self.default = val['default']
        

class agentCommand:
    def __init__(self, name, cmdItem):
        self.name = name
        self.desc = ""
        self.args = []
        self.handler = ""

        self.name = list(cmdItem.keys())[0]
        val = list(cmdItem.values())[0]

        if type(val) is str:
            self.handler = val
        else:
            if 'args' in val:
                for arg in val['args']:
                    self.args.append(agentCommandArg(arg))

            if 'desc' in val:
                self.desc = val['desc']


            if 'handler' in val:
                self.handler = val['handler']

    def getHelpString(self):
        helpStr = "Command: "+self.name+"\n"
        helpStr += "  desc: "+self.desc+"\n"
        helpStr += "  Args:\n"

        for arg in self.args:
            helpStr += "    "+arg.name+" - "+arg.desc+"\n"

        return helpStr


class agent:
    def __init__(self,namespace, name, agentItem):
        self.init =""
        self.handlers = {}
        self.commands = []
        self.name = name
        self.namespace = namespace
        
        if 'init' in agentItem:
            self.init = agentItem['init']

        if 'handlers' in agentItem:
            for handler in agentItem['handlers']:
                name = list(handler.keys())[0]
                code  = list(handler.values())[0]
                self.handlers[name] = code
        
        if 'commands' in agentItem:
            for command in agentItem['commands']:
                self.commands.append(agentCommand(name,command))

class fieldVal:
    def __init__(self, name):
        self.name = name.upper()
        self.desc = ""
        self.val = None
        

class fieldDesc:
    def __init__(self, name, strType):
        self.vals = []
        self.valDict = {}
        self.arrayLen = 1
        self.isEnum = False
        self.isMask = False
        self.valsFormat = "0x%0.2X"
        self.valIndex = 0
        self.namespace = None
        self.standard = False

        self.format = 'FORMAT_DEFAULT'

        if strType in ['flag','flags','mask','bits']:
            self.format = 'FORMAT_HEX'
            self.isMask = True
            strType = 'uint8_t'

        if strType in ['enum','enums']:
            self.format = 'FORMAT_HEX'
            self.isEnum = True
            strType = 'uint8_t'

        m = re.search('\*([0-9]*)', strType)
        if(m):
            if(m.group(1) != ''):
                self.arrayLen = int(m.group(1))
            strType = strType[0:m.start()]
        

        strType = strType.lower().replace('_t','')

        self.setType(strType, self.arrayLen)

        self.id = 0
        self.name = name
        self.globalName = "PP_FIELD_"+self.name.upper()
        self.isVarLen = False
        self.isRequired = False
        self.desc = ""
        self.memberName = "m"+ self.name.capitalize()

    def isPlugin(self):
        return self.namespace != self.protocol.namespace

    def camel(self):
            
            if self.isPlugin():
                return self.namespace[:1].capitalize() + self.namespace[1:] + self.name[:1].capitalize() + self.name[1:]
            else:
                return self.name[:1].capitalize() + self.name[1:]

    def setType(self, type, len):

        if not (type in cNameDict):
            print( "INVALID DATA TYPE!:  " + type)

        self.arrayLen = len
        self.type = type
        self.size = sizeDict[self.type] * self.arrayLen
        self.objSize = sizeDict[self.type]
        self.pyFormat = pyFormatDict[self.type]
        self.cType = cNameDict[self.type]
        self.pyType = pyNameDict[self.type]
        self.cppType = self.cType

        self.isString = False
        self.isArray = False

        if(self.arrayLen > 1):
            self.isArray = True

        if(self.type == 'string'):
            self.cppType = "string"
            self.isString = True
            self.isArray = True
            if(self.arrayLen == 1):
                self.arrayLen = 32 #if no arraylen is specified default 32
        else:
            if(self.isArray):
                self.cppType = self.cppType +"*"

    def addVal(self, val):
 
        self.valDict[val.name] = len(self.vals) -1

        if self.isMask:
            val.val = 1 << self.valIndex
            self.valIndex+=1
            strType = 'uint8'
            if len(self.vals) > 8:
                self.valsFormat = "0x%0.4X"
                strType = 'uint16'
            if len(self.vals) > 16:
                self.valsFormat = "0x%0.8X"
                strType = 'uint32'
            if len(self.vals) > 32:
                print( "Error maximum flags per field is 32")
            self.setType(strType,1)
        
        elif self.isEnum:
            val.val =  self.valIndex
            self.valIndex+=1

        self.valDict[val.name] = val.val
        self.vals.append(val)
    

    def setNamespace(self, namespace):
        self.namespace  = namespace
        self.globalName = namespace.upper()+"_FIELD_"+self.name.upper()

    def getFieldDeclaration(self):
        output = io.StringIO()
        output.write("{0} field_{1}".format(self.cType, self.name))
        if(self.arrayLen > 1):
            output.write("["+str(self.arrayLen)+"]")

        return output.getvalue()

    def getParamType(self):
        if self.isArray:
            return self.cType +"*"
        else:
            return self.cType;

    def getDeclaration(self):

        nsName = self.name

        if self.isPlugin():
            nsName = self.namespace + self.name[:1].capitalize() + self.name[1:]

        if self.isArray:
            return self.cType +" "+nsName+"["+ str(self.arrayLen)+"]"
        else:
            return self.cType + " " + nsName

    def getFormat(self):
        if self.isString:
            return "%s"
        else:
            return "%i"



class packetDesc:
    def __init__(self,name, protocol):
        self.name = name
        self.globalName =  "PP_PACKET_"+self.name.upper()
        self.className = name.capitalize() +"Packet"
        self.desc =""
        self.fields = []
        self.sruct = False
        self.fieldCount=0
        self.respondsTo = {}
        self.requests = {}
        self.standard = False
        self.structName = name.lower() + '_packet_t'
        self.hasResponse = False
        self.protocol = protocol
        self.requiredFields = []
        self.requiredFieldCount = 0
        self.namespace = protocol.namespace

    def isPlugin(self):
        return self.namespace != self.protocol.namespace

    def extName(self):
        return self.namespace + ":" + self.name
    
    def camel(self, lowerNS = False):

        if self.isPlugin():
            #make lower case 
            if lowerNS:
                return self.namespace.lower() + self.name[:1].capitalize() + self.name[1:]
            else:
                return self.namespace[:1].capitalize() + self.namespace[1:] + self.name[:1].capitalize() + self.name[1:]
        else:            
            return self.name[:1].capitalize() + self.name[1:]

    def setNamespace(self, namespace):
        self.namespace = namespace
        self.globalName = namespace.upper()+"_PACKET_"+self.name.upper()

    def addField(self, field):
        field.id = self.fieldCount
        self.fields.append(field)
        self.fieldCount+=1

    def addYAMLField(self, pfieldItem):

        if type(pfieldItem) is dict:
            pfname = list(pfieldItem.keys())[0]
            pfield = list(pfieldItem.values())[0]
        else:
            pfname = pfieldItem
            pfield = {}

        strReq =""
        if not (pfname in self.protocol.fieldIdx):
            print( 'ERROR Field not declared: ' + pfname)

        #get id of field and make a copy
        idx = self.protocol.fieldIdx[pfname]
        fieldCopy = copy.copy(self.protocol.fields[idx])

        if('req' in pfield):
            fieldCopy.isRequired = pfield['req']

        if('desc' in pfield):
            fieldCopy.desc = pfield['desc']

        fieldCopy.id = self.fieldCount
        self.fields.append(fieldCopy)
        self.fieldCount+=1

    def postProcess(self):
        if len(self.requests) > 0:
            self.hasResponse = True;
            self.response = self.protocol.getPacket(next(iter(self.requests.keys())))

        for field in self.fields:
            if field.isRequired:
                self.requiredFields.append(field)
                self.requiredFieldCount += 1

    def tableSize(self):
        sum =0;
        for field in self.fields:
            if field.size > 4:
                sum+=4
            else:
                sum += field.size

        return sum


    def getDocMd(self):
        output = io.StringIO()
        idHex = "%0.2X" % self.packetId
        output.write('### '  + self.name + '\n')
        output.write(self.desc + '\n\n')
        output.write('* Packet ID: *['+idHex+']*\n')
        requestCount = len(self.requests)
        respondsToCount = len(self.respondsTo)

        #write response packets
        if(requestCount > 0):
            output.write('* *Requests: ')
            first = True
            for req in self.requests:
                if(first):
                    first = False
                else:
                    output.write(', ')
                output.write(req)
            output.write('*\n\n')

        #write request packets
        if(self.name == 'Ack'):
            output.write('* *Responds To: Any Packet without a defined response*\n\n')
        else:
            if(respondsToCount > 0):
                output.write('* *Responds To: ')
                first = True
                for resp in self.respondsTo:
                    if(first):
                        first = False
                    else:
                        output.write(', ')
                    output.write(resp)
                output.write('*\n')

        output.write('\n')

        rowBytes = io.StringIO()
        rowBorder = io.StringIO()
        rowFields = io.StringIO()
        rowTypes = io.StringIO()


        if(len(self.fields) > 0):
            rowBytes.write('|***Byte***|')
            rowBorder.write('|---|')
            rowFields.write('|***Field***')
            rowTypes.write('|***Type***')

            count =0

            for pfield in self.fields:

                #write bytes
                if(pfield.size > 4):
                    rowBytes.write(str(count)+'| . . . . . . . |'+str(count+pfield.size -1))
                    count+=pfield.size
                else:
                    for x in range(pfield.size):
                        rowBytes.write(str(count) + '|')
                        count+=1

                #write border
                span = pfield.size
                if(span > 4):
                    span = 4
                for x in range(span):
                    rowBorder.write('---|')

                #write fields
                span = pfield.size
                if(span > 4):
                    span = 4
                rowFields.write('<td colspan=\''+str(span)+'\'>')
                if(pfield.isRequired):
                    rowFields.write('***'+pfield.name+'***')
                else:
                    rowFields.write(pfield.name)

                #write types
                span = pfield.size
                if(span > 4):
                    span = 4
                rowTypes.write('<td colspan=\''+str(span)+'\'>')
                rowTypes.write(pfield.cType)
                if(pfield.isArray):
                    if(pfield.isVarLen):
                        rowTypes.write('[0-'+ str(pfield.size)+' ]')
                    else:
                        rowTypes.write('['+str(pfield.size)+']')

            #combine rows for table
            output.write(rowBytes.getvalue() + "\n");
            output.write(rowBorder.getvalue() + "\n");
            output.write(rowFields.getvalue() + "\n");
            output.write(rowTypes.getvalue() + "\n");

            output.write('\n\n')
            output.write('Fields:\n')
            #write field description table
            for pfield in self.fields:
                output.write('>***'+ pfield.name+'*** : ' + pfield.desc +'<br/>\n')
                if pfield.isMask:
                    for idx,val in enumerate(pfield.vals):
                        strVal = pfield.valsFormat % (1 << idx)
                        output.write('>> **{0}** : {1} - {2}<br/>\n'.format(strVal, val.name, val.desc))
                    output.write('>\n')

                if pfield.isEnum:
                    for idx,val in enumerate(pfield.vals):
                        strVal = pfield.valsFormat % (idx)
                        output.write('>> **{0}** : {1} - {2}<br/>\n'.format(strVal, val.name, val.desc))
                    output.write('>\n')
        else:
            output.write('>This Packet type does not contain any data fields\n\n')

        output.write('\n------\n')

        return output.getvalue();


class protocolDesc:
    def __init__(self, name):
        self.name = name
        self.fileName = name+"Service"
        self.cppFileName = name+"Service"
        self.desc = ""
        self.hash = ""
        self.fields = []
        self.fieldIdx = {}
        self.fieldId =0
        self.fieldGroups = {}
        self.packets = []
        self.packetIdx ={}
        self.packetId =0
        self.structs =[]
        self.structsAndPackets=[]
        self.structIdx ={}
        self.structId =0
        self.namespace = "pp"
        self.snippets = False
        self.genUtility = False
        self.utilName =""
        self.agents = {}
        self.defaultResponse = ""
        self.plugins = []
        self.crc = None
        self.icdVersion = None

        self.raw = None

    def hasPacket(self, name):

        if not ':' in name:
            name = self.namespace + ":" + name

        return name in self.packetIdx

    def getExtName(self, name):
        
        extName = name
        if not ':' in name:
            extName = self.namespace + ":" + name
        else:
            name = name.split(':')[1]

        if extName in self.packetIdx:
            return extName
        else: 
            for k,v in self.packetIdx.items():
                if k.endswith(name):
                    return k 
        
        return None

    def service(self):
        return self.namespace.upper() +'_SERVICE'

    def descFromId(self, typeId):
        return self.packets[typeId-len(self.structs)]

    def fieldDescFromId(self, typeId):
        return self.fields[typeId]

    def camelNamespace(self):
        return self.namespace[:1].capitalize() + self.namespace[1:]

    def addField(self,field):
        field.id = self.fieldId
        field.protocol = self

        #If field is being added from a plugin, we want to keep the original namespace
        if field.namespace is None:
            field.setNamespace(self.namespace)

        self.fields.append(field)
        self.fieldIdx[field.name] = self.fieldId
        self.fieldId+=1

    def addGroup(self, name, fields):
        self.fieldGroups[name] = fields

    def addPacket(self,packet):
        packet.packetId = self.packetId
        packet.protocol = self

        for field in packet.fields:
            field.protocol = self

        #If packet is being added from a plugin, we want to keep the original namespace
        if packet.namespace is None:
            packet.setNamespace(self.namespace)

        self.packets.append(packet)
        self.structsAndPackets.append(packet)

        #Add entry to packet index with name and extendedname
        self.packetIdx[packet.extName()] = self.packetId

        self.packetId+=1

    def addStruct(self,struct):
        struct.packetId = self.packetId
        struct.protocol = self
        struct.struct = True

        #If struct is being added from a plugin, we want to keep the original namespace
        if struct.namespace is None:
            struct.setNamespace(self.namespace)

        struct.globalName = self.namespace.upper()+"_STRUCT_"+struct.name.upper()
        self.structs.append(struct)
        self.structsAndPackets.append(struct)
        self.structIdx[struct.name] = self.packetId
        self.packetId+=1
    
    def addAgent(self, agent):
        
        #If agent is being added from a plugin, we want to keep the original namespace
        if agent.namespace is None:
            agent.namespace = self.namespace

        self.agents[agent.name] = agent

    def getPacket(self, name):
        
        extName = name
        if not ':' in name:
            extName = self.namespace + ":" + name
        else:
            name = name.split(':')[1]

        if extName in self.packetIdx:
            return self.structsAndPackets[self.packetIdx[extName]]
        else: 
            for k,v in self.packetIdx.items():
                if k.endswith(name):
                    return self.structsAndPackets[v]
    




def addStandardPackets(protocol):
    ping = packetDesc("Ping", protocol)
    ack = packetDesc("Ack", protocol)
    icd = fieldDesc("icd", "string*16")

    ping.setNamespace(protocol.namespace)
    ack.setNamespace(protocol.namespace)
    icd.setNamespace(protocol.namespace)
    icd.isRequired = True
    #icd.format = 'FORMAT_HEX'
    icd.setNamespace(protocol.namespace)
    icd.desc = "ICD version of protocol description. This is used to verify endpoints are using the same protocol"
    ping.desc = "This message requests an Ack from a remote device to test connectivity"
    ping.response = ack
    ping.hasResponse = True
    ping.requests['Ack'] =0
    ack.desc ="Acknowledges any packet that does not have an explicit response"
    ping.standard = True
    ack.standard = True
    icd.standard = True
    protocol.addField(icd)
    ping.addField(icd)
    ack.addField(icd)
    protocol.addPacket(ping)
    protocol.addPacket(ack)


def parseYAMLField(protocol, fieldItem):
    try:
        name = list(fieldItem.keys())[0]
        field = list(fieldItem.values())[0]
    except: 
        print("Error parsing: " + str(fieldItem))

    strType = field['type'].replace("(","[").replace(")","]");

    newField = fieldDesc(name, strType)
    newField.setNamespace(protocol.namespace)

    if('format' in field):
        format = field['format'].lower()
        if not format in formatDict:
            print( "INVALID FORMAT :" + format)

        newField.format = formatDict[format]

    if 'req' in field:
        newField.isRequired = field['req']

    if 'required' in field:
        newField.isRequired = field['required']

    if('desc' in field):
        newField.desc = field['desc']

    if(name in protocol.fields):
        print( 'ERROR Duplicate Field Name!: ' + name)

    #get vals if any
    if "vals" in field:
        for valItem in field['vals']:
            if type(valItem) is dict:
                name = list(valItem.keys())[0]
                val = list(valItem.values())[0]
            else:
                name = valItem
                val = {}

            newVal = fieldVal(name)

            if('val' in val):
                newVal.val = val['val']

            if('desc' in val):
                newVal.desc = val['desc']

            newField.addVal(newVal)

    protocol.addField(newField)
    return newField


def mergePlugin(protocol, plugin):
    
            pluginPath = None
            namespace = None

            #if plugin is a string, assume it is a local file
            if type(plugin) is str:
                pluginPath = plugin
            else:
                #use key 
                pluginPath = list(plugin.keys())[0]

                if 'namespace' in plugin:
                    namespace = plugin['namespace']
            

            pluginYaml = None


            #determine if plugin is local file or url 
            if (pluginPath.endswith('.yaml') or pluginPath.endswith('.yml')) and os.path.isfile(pluginPath):
                pluginData = open(pluginPath)
                pluginYaml = yaml.load(pluginData , Loader=yaml.FullLoader)
            elif validators.url(pluginPath):

                pluginData = requests.get(pluginPath).text
                pluginYaml = yaml.load(pluginData , Loader=yaml.FullLoader)
            else:
                # check if plugin is in plugins folder
                #load plugin from plugins folder using pkg util
                pluginData = pkgutil.get_data('pyProtocol', 'plugins/' + pluginPath + '.yml')

                if pluginData is None:
                    print("Error loading plugin: " + pluginPath)
                    return
                else :
                    pluginYaml = yaml.load(pluginData , Loader=yaml.FullLoader)

                    if 'redirect' in pluginYaml:
                        pluginData = requests.get(pluginYaml['redirect']).text
                        pluginYaml = yaml.load(pluginData , Loader=yaml.FullLoader)
            
            pluginProtocol = parseYAML(pluginYaml)
            if namespace is None:
                namespace = pluginProtocol.namespace

            #merge groups 
            for key, group in pluginProtocol.fieldGroups.items():
                protocol.fieldGroups[key] = group

            #merge in fields
            for field in pluginProtocol.fields:
                if not field.standard:
                    field.setNamespace(namespace)
                    protocol.addField(field)
            
            #merge in packets
            for packet in pluginProtocol.packets:
                if not packet.standard:
                    packet.setNamespace(namespace)
                    protocol.addPacket(packet)
            
            #merge in structs
            for struct in pluginProtocol.structs:
                struct.setNamespace(namespace)
                protocol.addStruct(struct)

            #merge in agents
            for key, agent in pluginProtocol.agents.items():
                protocol.addAgent(agent)


            
                
            


def parseYAML(objProtocol):

    protocol = protocolDesc(objProtocol['name'])
    protocol.raw = objProtocol

    if "namespace" in objProtocol:
        protocol.namespace = objProtocol['namespace']
    elif "prefix" in objProtocol:
        protocol.namespace = objProtocol['prefix']  #support legacy prefix keyword
    else:
        protocol.namespace = objProtocol['name']

    if "desc" in objProtocol:
        protocol.desc = objProtocol['desc']

    if "defaultResponse" in objProtocol:
        protocol.defaultResponse = objProtocol['defaultResponse']

    addStandardPackets(protocol)



    for fieldItem in objProtocol['fields']:

        nodeType = list(fieldItem.values())[0]

        #all fields must have a 'type', so if it doesnt, then it is a field group
        if not 'type' in list(fieldItem.values())[0]:
            groupName = list(fieldItem.keys())[0]
            fieldGroupItems = list(fieldItem.values())[0]
            groupFields = []
            for fieldGroupItem in fieldGroupItems:
                newField = parseYAMLField(protocol, fieldGroupItem)
                groupFields.append(newField.name)
            protocol.addGroup(groupName, groupFields)
        else:
            parseYAMLField(protocol, fieldItem)

    if 'structs' in  objProtocol:
        for structItem in objProtocol['structs']:
            name = list(structItem.keys())[0]
            struct = list(structItem.values())[0]
            desc =""
            newStruct = packetDesc(name,protocol)


            if(name in protocol.structIdx):
                print( 'ERROR Duplicate Struct Name!: ' + name)

            if('desc' in struct):
                desc = struct['desc']

            #get all fields declared for packet
            if "fields" in struct:
                for pfieldItem in struct['fields']:

                    if type(pfieldItem) is dict:
                        pfname = list(pfieldItem.keys())[0]
                        pfield = list(pfieldItem.values())[0]
                    else:
                        pfname = pfieldItem
                        pfield = {}


                    if pfname in protocol.fieldGroups:
                        for pfFieldGroupItem in protocol.fieldGroups[pfname]:
                            newStruct.addYAMLField(pfFieldGroupItem)
                    else:
                        newStruct.addYAMLField(pfieldItem)

            newStruct.desc = desc

            protocol.addStruct(newStruct)

    if 'packets' in  objProtocol:
        for packetItem in objProtocol['packets']:
            name = list(packetItem.keys())[0]
            packet = list(packetItem.values())[0]
            desc =""
            newPacket = packetDesc(name, protocol)
            newPacket.setNamespace(protocol.namespace)

            try:

                if(name in protocol.packetIdx):
                    print( 'ERROR Duplicate Packet Name!: ' + name)

                if('desc' in packet):
                    desc = packet['desc']

                if('response' in packet):
                    if (packet['response'] != "none"):
                        newPacket.requests[packet['response']] = 0
                else:
                    if not protocol.defaultResponse == "" and not  protocol.defaultResponse == newPacket.name :
                        newPacket.requests[protocol.defaultResponse] = 0

                #get all fields declared for packet
                if "fields" in packet:
                    for pfieldItem in packet['fields']:

                        if type(pfieldItem) is dict:
                            pfname = list(pfieldItem.keys())[0]
                            pfield = list(pfieldItem.values())[0]
                        else:
                            pfname = pfieldItem
                            pfield = {}


                        if pfname in protocol.fieldGroups:
                            for pfFieldGroupItem in protocol.fieldGroups[pfname]:
                                newPacket.addYAMLField(pfFieldGroupItem)
                        else:
                            newPacket.addYAMLField(pfieldItem)

                newPacket.desc = desc

                protocol.addPacket(newPacket)
            
            except: 
                print("Error parsing: " + str(packetItem))

    #support legacy files using sims keyword
    if 'sims' in objProtocol:
        objProtocol['agents'] = objProtocol['sims']

    if 'agents' in  objProtocol: 
        for agentItem in objProtocol['agents']:
            name = list(agentItem.keys())[0]
            agentObj = list(agentItem.values())[0]
            protocol.agents[name] = agent(protocol.namespace, name,agentObj)
         

    for packet in protocol.packets:
        for request in packet.requests.keys():
            protocol.getPacket(request).respondsTo[packet.name] = 0


    for packet in protocol.packets:
        packet.postProcess()
    
    #add in plugins 
    if 'plugins' in  objProtocol:
        for plugin in objProtocol['plugins']:
            mergePlugin(protocol, plugin)


    if 'crc' in objProtocol:
        protocol.crc = objProtocol['crc']

    if 'hash' in objProtocol:
        protocol.hash = objProtocol['hash']

    # return news items list
    return protocol

def buildProtocol(desc):

    protocol = None


    if isinstance(desc, str):

        objProtocol = None

        if desc.startswith("http"):
            response = requests.get(desc)
            objProtocol = yaml.load(response.text , Loader=yaml.FullLoader)
        
        else:

            relativePath = os.path.dirname(os.path.abspath(desc))
            if not os.path.isfile(desc):
                print("Error: File not found: " + desc)
                return 0

            data = open(desc)
            objProtocol = yaml.load(data , Loader=yaml.FullLoader)

            def addIfNotDuplicate(lista, listb):
                for item in listb:
                    if not item in lista:
                        lista.append(item)
                    else:
                        print(f"Duplicate item: {item}" )


            if 'include' in objProtocol:
                for include in objProtocol['include']:
                    with open(os.path.join(relativePath, include), 'r') as stream:
                        includeData = yaml.load(stream, Loader=yaml.FullLoader)
                        if 'fields' in includeData:
                            addIfNotDuplicate(objProtocol['fields'], includeData['fields'])
                        if 'packets' in includeData:
                            addIfNotDuplicate(objProtocol['packets'], includeData['packets'])
                        if 'structs' in includeData:
                            addIfNotDuplicate(objProtocol['structs'], includeData['structs'])
                        if 'agents' in includeData:
                            addIfNotDuplicate(objProtocol['agents'], includeData['agents'])
                    


        fileCrc, fileHash = crc(desc)

        objProtocol['crc'] = fileCrc
        objProtocol['hash'] = fileHash

        protocol = parseYAML(objProtocol)

    else:
        protocol = parseYAML(desc)

    return protocol

def PolyProtocol(desc):

    return buildProtocol(desc)


