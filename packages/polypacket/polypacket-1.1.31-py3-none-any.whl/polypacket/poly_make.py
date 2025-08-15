#!/usr/bin/env python
#
#@file make_protocol.py
#@brief python script to generate code for PolyPacket
#@author Jason Berger
#@date 02/19/2019
#

from doctest import OutputChecker
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
from polypacket.protocol import *
from mrtutils.mrtTemplateHelper import *
import importlib.metadata


args = None
parser = None

now = datetime.datetime.now()
path ="./"



# def buildTemplate(protocol, templateFile, outputFile):
#     template = Template(pkgutil.get_data('polypacket',templateFile) )
#     text_file = open( outputFile , "w")
#     text_file.write("\n".join(template.render(proto = protocol, args = args, t = TemplateHelper()).splitlines()))
#     #text_file.write(template.render(proto = protocol))
#     text_file.close()

def buildTemplate(object, templateFile, outputFile, userBlocks = True, overwrite= True):
    exists= False
    if not os.path.exists(outputFile):
        exists = True 

    if exists and overwrite == False:
        return 0

    outputFile = outputFile.replace(" ", "_")

    version = importlib.metadata.version("polypacket")
    cr = CodeReplacer()
    newContents =""
    headerPattern = r"@file (.*?)\n(.*?)\*/"
    handlerPattern = r" (.*?)_handler.*?\n}"
    if os.path.isfile(outputFile) and userBlocks:
        exists = True
        curFile = open(outputFile, "r")
        text = curFile.read()
        cr.loadText(text)
        cr.loadText(text,headerPattern)
        cr.loadText(text,handlerPattern)

    template = Template(pkgutil.get_data('polypacket',templateFile) )
    newContents = "\n".join(template.render(proto = object, args= args,  t = TemplateHelper(), version = version).splitlines())
    if(userBlocks):
        newContents = cr.insertBlocks(newContents)
        newContents = cr.insertBlocks(newContents,headerPattern)
        newContents = cr.insertBlocks(newContents,handlerPattern)
        cr.printDrops()
    text_file = open( outputFile , "w")
    text_file.write(newContents)
    text_file.close()

def initRepo(path):
    subprocess.check_output(['git','init',path] )


def addSubModule(gitpath, suburl, subpath):
    path = os.getcwd()
    os.chdir(gitpath)
    subprocess.check_output(['git','submodule','add', suburl,  subpath] )
    os.chdir(path)


def genUtility(protocol, inputFile, path):
    protocol.utilName = os.path.basename(path)
    path+="/"
    srcPath = path +"src/"
    libPath = path +"src/lib/"
    buildPath = path+"build/"
    docPath = path+"doc/"
    polyPath = path+"MrT/Modules/Utilities/PolyPacket"
    xmlPath = os.path.dirname(inputFile)

    if not os.path.isdir(path):
        os.makedirs(path)
        initRepo(path)
        addSubModule(path, "https://gitlab.com/mrt-public/modules/Utilities/COBS.git" ,"MrT/Modules/Utilities/COBS")
        addSubModule(path, "https://gitlab.com/mrt-public/modules/Utilities/PolyPacket.git" ,"MrT/Modules/Utilities/PolyPacket")
        addSubModule(path, "https://gitlab.com/mrt-public/modules/Utilities/JSON.git" ,"MrT/Modules/Utilities/JSON")
        addSubModule(path, "https://gitlab.com/mrt-public/modules/Platforms/Common.git" ,"MrT/Modules/Platforms/Common")
        addSubModule(path, "https://gitlab.com/mrt-public/modules/Platforms/Linux.git" ,"MrT/Modules/Platforms/Linux")
        os.makedirs(srcPath)
        os.makedirs(libPath)
        os.makedirs(buildPath)
        os.makedirs(docPath)
    os.system('cp '+ inputFile +' '+ path)
    #os.system('cp '+ script_dir+'/linux_uart/linux_uart* '+ libPath)
    #TODO commit

    protocol.genUtility = True
    buildTemplate(protocol, 'templates/cmake_template.txt', path + 'CMakeLists.txt')
    buildTemplate(protocol, 'templates/c_header_template.h', libPath + protocol.fileName+".h")
    buildTemplate(protocol, 'templates/c_source_template.c', libPath + protocol.fileName+".c")
    buildTemplate(protocol, 'templates/app_template.h', srcPath+"app_" + protocol.name.lower() +".h")
    buildTemplate(protocol, 'templates/app_template.c', srcPath+"app_" + protocol.name.lower()+".c")
    buildTemplate(protocol, 'templates/util_main_adv_template.c', srcPath+"main.c")
    buildTemplate(protocol, 'templates/doc_template.html', docPath + protocol.name+"_ICD.md")   #the html template works better, and is markdown compatible
    buildTemplate(protocol, 'templates/doc_template.html', docPath + protocol.name+"_ICD.html")
    protocol.genUtility = False #set this back in case someone does this out of order

# Initialize the argument parser
def init_args():
    global parser
    parser = argparse.ArgumentParser("Tool to generate code and documentation for PolyPacket protocol")
    parser.add_argument('-i', '--input', type=str, help='input file to parse', default="")
    parser.add_argument('-o', '--output', type=str, help='Output path', default="")
    parser.add_argument('-l', '--language', type=str, help='Output language', default="c")
    parser.add_argument('-d', '--document', type=str, help='documentation path', default="")
    parser.add_argument('-a', '--app', action='store_true', help='Generates the app layer code to fill out', default=False)
    parser.add_argument('-s', '--snippets', action='store_true', help='Adds helpful code snippets to files', default=False)
    parser.add_argument('-u', '--utility', type=str, help='Output path for Linux host utility application', default="")
    parser.add_argument('-m', '--html', action='store_true', help='Generates html doc', default=False)
    parser.add_argument('-b', '--basic', action='store_true', help='Simplified documentation', default=False)
    parser.add_argument('-t', '--template', type=str, help='Template path', default="")
    parser.add_argument('--icd', type=str, help='Spcify ICD version for the protocol', default=None)



def main():
    global path
    global parser
    global args

    init_args()
    args= parser.parse_args()
    argCount = len(sys.argv)

    inputFile = args.input
    path = args.output
    utilPath = args.utility
    docPath = args.document


    if args.template:
        print("Creating example protocol file: sample_protocol.yml!")
        f= open(args.template + ".yml","wb")
        f.write(pkgutil.get_data('polypacket','examples/sample_protocol.yml'))
        f.close()
        sys.exit()

    if inputFile == "":
        print("No input file specified, use -t to create a template file")
        sys.exit()

    if os.path.isfile(inputFile):
        fileCrc, fileHash = crc(inputFile)

        print( "Parsing " + inputFile)

        protocol = buildProtocol(inputFile)

        protocol.hash = fileHash
        protocol.crc = fileCrc

        if args.icd is not None:
            protocol.icdVersion = args.icd
        else:
            protocol.icdVersion = fileHash

        print( "Protocol "+ protocol.name+ " generated!")
        protocol.genTime = now.strftime("%m/%d/%y")

        protocol.snippets = args.snippets

        #get path of this script so we can run remotely
        script_dir = os.path.dirname(__file__)
        xmlPath = os.path.dirname(inputFile)


        if(docPath != ""):
            buildTemplate(protocol, 'templates/doc_template.rst', docPath +"/"+ protocol.name+"_ICD.rst")
            if args.html:
                buildTemplate(protocol, 'templates/doc_template.html', docPath +"/"+ protocol.name+"_ICD.html")
            #pdfkit.from_file(xmlPath + protocol.name+"_ICD.html", xmlPath + protocol.name+"_ICD.pdf" )
            
        if(utilPath != ""):
            print ("Generating Utility from:" +inputFile)
            genUtility(protocol,inputFile, utilPath)

        if(path != ""):

            if args.language == "c":
                buildTemplate(protocol, 'templates/c_header_template.h', path+"/" + protocol.fileName+".h")
                buildTemplate(protocol, 'templates/c_source_template.c', path+"/" + protocol.fileName+".c")
            elif args.language == "cpp":
                buildTemplate(protocol, 'templates/cpp_header_template.h', path+"/" + protocol.fileName+".h")
                buildTemplate(protocol, 'templates/cpp_source_template.cpp', path+"/" + protocol.fileName+".cpp")

            elif args.language == "python" or args.language == "py":
                buildTemplate(protocol, 'templates/python_template.py', path+"/" + protocol.fileName+".py")
            elif args.language == "js":
                buildTemplate(protocol,  'templates/javascript_template.js', path +"/"+ protocol.fileName+".js");

            if(args.app):
                buildTemplate(protocol,'templates/app_template.h', path+"/app_" + protocol.name.lower() +".h")
                buildTemplate(protocol, 'templates/app_template.c', path+"/app_" + protocol.name.lower()+".c")

    else:
        print(" No such file: " + inputFile)



if __name__ == "__main__":
    main()
