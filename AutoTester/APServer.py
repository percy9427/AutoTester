import django
import sys
import os
import threading
import time
import atexit
import logging
from logging.handlers import RotatingFileHandler
import traceback
import serial


sensorList={}
effectorList={}
controlList={}
basePath=''
apc=None

class apController:
    def __init__(self, simulation=False):
        self.simulation=simulation
        self.apcLog=logging.getLogger('APCLog')
        print(basePath + 'Logs/tester.log')
        handler = RotatingFileHandler(basePath + 'Logs/tester.log', maxBytes=2000, backupCount=4)
        simpleFormatter = logging.Formatter('%(asctime)s - %(message)s')
        normalFormatter = logging.Formatter('%(asctime)s - %(threadName)s - %(message)s')
        handler.setFormatter(simpleFormatter)
        handler.setLevel(logging.INFO)
        self.apcLog.addHandler(handler)
        self.apcLog.setLevel(logging.INFO)
        self.debugLog=logging.getLogger('Debug')
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(normalFormatter)
        self.debugLog.addHandler(console)
        handler2 = RotatingFileHandler(basePath + 'Logs/debug.log', maxBytes=8000, backupCount=4)
        handler2.setFormatter(normalFormatter)
        handler2.setLevel(logging.INFO)
        self.debugLog.addHandler(handler2)
        self.debugLog.setLevel(logging.DEBUG)
    

class sensorObject:
    def __init__(self,sensorDBObject):
        self.name=sensorDBObject.sensorName
        self.dbInfo=sensorDBObject        
        
    def serialRead(self):
        if apc.simulation:
            self.currValue='7.0'
            self.isDataValid=True
            return self.currValue
        try:
            PHTIMEOUT=1
            usbport = '/dev/ttyAMA0'
            self.serialPort = serial.Serial(usbport,38400,timeout=PHTIMEOUT)
            self.serialPort.write(bytes("L0\r",'utf-8'))
            self.serialPort.write(bytes("R\r",'utf-8'))
            self.initialized=True
            while True:
                data = self.serialPort.read().decode('utf-8')
                if data == "":
                    print("NO DATA","Sensor data missing - timeout from device")
                    break
                elif (data == "\r"):
                    if DEBUG==1:
                        print("Received from sensor:" + self.rawData)
                    self.prevVal=self.currVal
                    try:
                        self.lastRawData = float(self.rawData)
                        self.currVal = self.calA*self.lastRawData+self.calB
                        if self.currVal == self.calB:
                            self.isDataValid=False
                            print("0 Data","Ph data invalid - Ph of 0 received")
                        else:
                            self.isDataValid=True            
                    except ValueError:
                        print("NO DATA","Ph data invalid - non numeric data received")
                        self.isDataValid=False
                    self.rawData = ""
                    break
                else:
                    self.rawData = str(self.rawData) + data
            self.serialPort.close()
            self.serialPort=None
        except:
            traceback.print_exc()
            self.isDataValid=False
        if self.isDataValid:
            return self.currValue
        else:
            return None
    
            


        
def constructSensorList():
    global sensorList
    sensorList={}
    sensorDBList=Sensor.objects.all()
    for sensorDB in sensorDBList:
        a=sensorObject(sensorDB)
        if a.dbInfo.sensorEnabled:
            sensorList[a.name]=a
            
def sensorLoop(name):
    try:
        sensorObj=sensorList[name]
        while True:
            if sensorObj.dbInfo.sensorIOType=='Serial':
                currValue=sensorObj.serialRead()
                print(currValue)
            else:
                print(name)
            time.sleep(5)
    except:
        apc.debugLog.exception("Error in Sensor Processing for " + name)

            
def exit_handler():
    pass
    apc.debugMessage('Done')

def launchThreads(apc):
    atexit.register(exit_handler)
    constructSensorList()
    for sensorName in sensorList:
        sensorThread=threading.Thread(target=sensorLoop,name='sensorLoop-' + sensorName,args=([sensorName]))
        sensorThread.start()
        apc.apcLog.info('Thread: ' + sensorThread.getName() + ' started')
        
def getBasePath():
    programPath=os.path.realpath(__file__)
    programPathForwardSlash=programPath.replace('\\','/')
    programPathList=programPathForwardSlash.split('/')
    numPathSegments=len(programPathList)
    basePath=''
    pathSegment=0
    while pathSegment<numPathSegments-2:
        basePath+=programPathList[pathSegment] + '/'
        pathSegment+=1
#    print(basePath)
    return basePath

if __name__ == '__main__':
    basePath=getBasePath()
    sys.path.append(os.path.abspath(basePath + 'APC'))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'APC.settings'
    django.setup()
    apc=apController(simulation=True)
    from controller.models import Sensor
    launchThreads(apc)
