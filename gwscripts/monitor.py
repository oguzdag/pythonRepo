import sys
import os
import commands
from time import gmtime, strftime
import json

if sys.version_info[0]<3:
    import ConfigParser as configparser
else:
    import configparser

def runAndPrintOutput(command,output,outputType,fieldToExtract):
        if outputType=="JSON":
                mystatus, myout = commands.getstatusoutput(command)
                myjsonoutput=json.loads(myout)
                mystr = myjsonoutput[fieldToExtract]
                output=output.replace("@@OUTPUT@@",mystr)
        else:
                mystatus, myout = commands.getstatusoutput(command)
                output=output.replace("@@OUTPUT@@",str(myout))
        return output

def main(arg):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config=configparser.RawConfigParser()
        config.read(dir_path+"/commands.cfg")
        outputstyle=config.get("default","outputstyle")
        configsections=sorted(config.sections(), key=str.lower)
        outputList = []
        for eachsection in configsections:
                if eachsection=="default":
                        configsections.remove(eachsection)
        for eachsection in configsections:
                stepNum=eachsection[5:7]
                command = ""
                output = ""
                enabled = "True"
                outputType = ""
                fieldToExtract = ""
                for (eachkey,eachval) in config.items(eachsection):
                        if eachkey=="command":
                                command = eachval
                        elif eachkey=="output" :
                                output = eachval
                        elif eachkey=="enabled" :
                                enabled = eachval
                        elif eachkey=="outputtype" :
                                outputType = eachval
                        elif eachkey=="fieldtoextract":
                                fieldToExtract = eachval
                if enabled=="True":
                        outputList.append(runAndPrintOutput(command,output,outputType,fieldToExtract))
        mylogtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        if outputstyle == "sameline":
                myoutstr = mylogtime + "\t"
                for eachoutput in outputList :
                        myoutstr += eachoutput
                        myoutstr += ", "
                myoutstr=myoutstr[:-2]
                print(myoutstr)
        elif outputstyle == "seperated":
                print(mylogtime)
                for eachoutput in outputList :
                        print(eachoutput)

if __name__ == "__main__":
        main(sys.argv[1:])
