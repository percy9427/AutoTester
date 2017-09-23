'''
AutoTester is the controlling software to automatically run water tests
Further info can be found at: https://robogardens.com/?p=928
This software is free for DIY, Nonprofit, and educational uses.
Copyright (C) 2017 - RoboGardens.com
    
Created on Aug 9, 2017

This module is the interface towards the autotester physical hardware and the database.
The tester Class is the primary class representing the machine.

@author: Stephen Hayes
'''

import cv2   # @UnresolvedImport
import numpy as np
import math
import time
import os
#import fisheye
from FishEyeWrapper import FishEye,load_model
from ImageCheck import feature,colorSheet,swatch
import sys
import platform
import datetime
import _pickle
import copy
import logging
from logging.handlers import RotatingFileHandler
from Learn import loadModel
import traceback
import django
from django.utils.timezone import activate
from django.utils.dateparse import parse_datetime
import pytz
try:
    from picamera.array import PiRGBArray   # @UnresolvedImport
    from picamera import PiCamera   # @UnresolvedImport
except:
    pass

currentVersion="0.03"

if platform.system()=='Windows':
    existsGPIO=False
    existsDisplay=True
    existsWebCam=True
else:
    import RPi.GPIO as GPIO   # @UnresolvedImport
    existsGPIO=True
    existsDisplay=False
    existsI2C=True
    existsWebCam=True
    
plungerEnableGPIO=27
plungerStepGPIO=17
plungerDirectionGPIO=23
carouselEnableGPIO=9
carouselStepGPIO=10
carouselDirectionGPIO=22
agitatorEnableGPIO=6
agitatorStepGPIO=5
agitatorDirectionGPIO=11
ledGPIO=13
pumpGPIO=26
mixerValveGPIO=19

class testSequence:
    def __init__(self,name):
        self.testName=name

class Tester:
    CAMERATYPE_NONE=0
    CAMERATYPE_WEBCAM=1
    CAMERATYPE_PICAM=2    

    PRESENTATION_METRIC=0
    PRESENTATION_IMPERIAL=1
    
    PLUNGER_UNKNOWN=0
    PLUNGER_FULLY_CLOSED=1
    PLUNGER_MOSTLY_CLOSED=2
    PLUNGER_OPEN=3
    PLUNGER_PAST_OPEN=4
    
    PLUNGER_HIGH_SPEED=0
    PLUNGER_MEDIUM_SPEED=1
    PLUNGER_LOW_SPEED=2

    
    SET_HOME_POSITION=9999999
    TIGHTEN_PAST_HOME_POSITION=9999998
    
    def __init__(self, id):
        self.id = id
        self.simulation=(platform.system()=='Windows')
        self.basePath=getBasePath()
        self.webcam=None
        self.lowResImageGenerator=None
        self.measurementUnits=self.PRESENTATION_IMPERIAL
        if existsGPIO:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(plungerEnableGPIO,GPIO.OUT)
            GPIO.setup(plungerStepGPIO,GPIO.OUT)
            GPIO.setup(plungerDirectionGPIO,GPIO.OUT)
            GPIO.setup(carouselEnableGPIO,GPIO.OUT)
            GPIO.setup(carouselStepGPIO,GPIO.OUT)
            GPIO.setup(carouselDirectionGPIO,GPIO.OUT)
            GPIO.setup(agitatorEnableGPIO,GPIO.OUT)
            GPIO.setup(agitatorStepGPIO,GPIO.OUT)
            GPIO.setup(agitatorDirectionGPIO,GPIO.OUT)
            GPIO.setup(ledGPIO,GPIO.OUT)
            GPIO.setup(pumpGPIO,GPIO.OUT)
            GPIO.setup(mixerValveGPIO,GPIO.OUT)
            GPIO.output(plungerEnableGPIO,GPIO.HIGH)
            GPIO.output(plungerStepGPIO,GPIO.LOW)
            GPIO.output(plungerDirectionGPIO,GPIO.LOW)
            GPIO.output(carouselEnableGPIO,GPIO.HIGH)
            GPIO.output(carouselStepGPIO,GPIO.LOW)
            GPIO.output(carouselDirectionGPIO,GPIO.LOW)
            GPIO.output(agitatorEnableGPIO,GPIO.HIGH)
            GPIO.output(agitatorStepGPIO,GPIO.LOW)
            GPIO.output(agitatorDirectionGPIO,GPIO.LOW)
            GPIO.output(ledGPIO,GPIO.LOW)
            GPIO.output(pumpGPIO,GPIO.LOW)
            GPIO.output(mixerValveGPIO,GPIO.LOW)
        self.ledOn=False
        self.pumpOn=False
        self.valveClosed=False
        self.setTimeZone()
        self.loadTesterFromDB()
        self.loadProcessingParametersFromDB()
        self.loadStartupParametersFromDB()
        self.testerLog=logging.getLogger('TesterLog')
        handler = RotatingFileHandler(self.basePath+ "Logs/tester.log", maxBytes=2000, backupCount=4)
        simpleFormatter = logging.Formatter('%(asctime)s - %(message)s')
        normalFormatter = logging.Formatter('%(asctime)s - %(threadName)s - %(message)s')
        handler.setFormatter(simpleFormatter)
        handler.setLevel(logging.INFO)
        self.testerLog.addHandler(handler)
        self.testerLog.setLevel(logging.INFO)
        self.debugLog=logging.getLogger('Debug')
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(normalFormatter)
        self.debugLog.addHandler(console)
        handler2 = RotatingFileHandler(self.basePath+"Logs/debug.log", maxBytes=8000, backupCount=4)
        handler2.setFormatter(normalFormatter)
        handler2.setLevel(logging.INFO)
        self.debugLog.addHandler(handler2)
        self.debugLog.setLevel(logging.DEBUG)
        self.cameraType=self.getCameraType()
        self.undistortImage=True
        self.createDefaultBlackScreen()
        self.getCameraModel()
        self.videoLowResCaptureLock=None
        self.latestLowResImage=None
        self.streamVideo=True
        self.useImageForCalibration=False
        self.cameraCompensationTransformationMatrix=None
        self.testerScheduleRegenerate=True
        self.extruderFound=False
        self.showTraining=False
        self.captureImageLock=None
        self.currentLightingConditions='LED'
        self.lightingConditionToDisplay='LED'
        self.currentAvgColor=np.array([0,0,0])
        self.tooDark=False  
        self.infoMessage('Tester Engine version ' + currentVersion + ' loaded') 
        self.plungerEnabled=False
        self.plungerDistanceFromMaxHeight=None
        self.plungerStepsPerMM=200*2*34/12 #Stepper Motor Steps, 1/4 steps, 34 tooth outer gear, 12 tooth inner gear
        self.mmToRaiseFromOpenToFullyClosed=5
        self.plungerSteps=None
        self.plungerStepping=False
        self.plungerMoving=False
        self.distanceToMovePlunger=None
        self.movePlungerLock=None
        self.plungerState=self.PLUNGER_UNKNOWN
        self.plungerSlow=False
        self.plungerAbort=False  #Immediately stops the plunger.  Used when final drop is detected
        self.valueForStopperWhenClosed=None
        self.previousLeftStopperPosition=None
        self.stopperMovement=None
        self.carouselBaseLineImage=None
        self.carouselEnabled=False
        self.carouselDistanceFromOrigin=None
        self.carouselStepsPerRevolution=200*4*80/8 #Stepper Motor Steps, 1/4 steps, 80 tooth outer gear, 8 tooth inner gear
        self.carouselSteps=None
        self.carouselStepping=False
        self.carouselMoveQueued=False
        self.carouselCurrentSymbol=None
        self.distanceToMoveCarousel=None
        self.moveCarouselLock=None
        self.carouselSeriesLock=None
        self.agitatorEnabled=False
        self.agitatorOn=False
        self.displayDot=False
        self.avgGreenDotH=None
        self.avgGreenDotS=None
        self.avgGreenDotV=None
        self.avgRedDotH=None
        self.avgRedDotS=None
        self.avgRedDotV=None
        self.loadFeaturesFromDB()
        self.featureWindowULRow=0
        self.featureWindowULCol=0
        self.featureWindowLRRow=0
        self.featureWindowLRCol=0
        self.featureStepSize=1
        self.currentFeature=None
        self.loadTestDefinitionsFromDB()
        self.stopperState=None
        self.referenceMarkFound=False
        self.parked=True
        self.jiggleRepetitionPhotos=0  #Num of photos to take at different shifts.  If > 0 then clipping frame offset by up to + or - jiggleShiftMax
        self.jiggleShiftMax=5
        self.jigglePhoto=False  #Turns on only when training photos are to be taken
        self.seriesRunning=False
        self.maxPlungerDepthNoAgitator=79
        self.maxPlungerDepthAgitator=67
        self.lastReagentRemainingML=0
        self.lastReagentName=None
        self.suppressProcessing=False
        self.dripValueList=[]
        self.dripSamplesSoFar=0
        self.dripMinGap=4
        self.dripTopList=[]
        self.loadColorSheetsFromDB()
        self.currentColorSheet=None
        self.currentSwatch=None
        self.showSwatches=False
        self.colorTable=None
        self.runTestLock=None
        self.testStatus=None
        self.currentTest=None
        self.recordTestedImage=True
        self.abortJob=False
        self.resetJobSchedule=False
        self.diagnosticQueue=[]
        self.diagnosticLock=None
        self.systemStatus='Initializing'
        self.flashLights()
        
    def getCameraModel(self):
        self.cameraModelFile=self.basePath + '/Calibrate/FisheyeUndistort-(' + self.lensType + ',' + str(self.cameraHeightLowRes) + ' x ' + str(self.cameraWidthLowRes) + ')-' + sys.version[0] + '.pkl'
        try:
            aggregateFishEyeModel=load_model(self.cameraModelFile)
            self.cameraFisheyeModel=aggregateFishEyeModel[0]
            self.cameraFisheyeExpansionFactor=aggregateFishEyeModel[1]
            self.infoMessage('Camera Model Loaded')
        except:
            self.cameraFisheyeModel=None
            self.infoMessage('Camera Model Not Found')
            self.cameraFisheyeExpansionFactor=self.defaultFisheyeExpansionFactor
        
    def debugMessage(self,message):
        try:
            if self.enableConsoleOutput:
                self.debugLog.debug(message)
        except:  #Might not have initialized yet
            print(message)
            
    def infoMessage(self,message):
        try:
            self.debugLog.info(message)
        except:  #Might not have initialized yet
            print(message)
            
    def setTimeZone(self):
        from tester.models import TesterExternal
        te=TesterExternal.objects.get(pk=1)
        tzString=te.currentTimeZone
        try:
            activate(tzString)
        except:
            self.infoMessage('TimeZone could not be activated using string ' + str(tzString))
        
    def loadTesterFromDB(self):
        from tester.models import TesterExternal,TesterProcessingParameters
        te=TesterExternal.objects.get(pk=1)
        self.testerName=te.testerName
        self.testerVersion=te.testerVersion
        self.dbModelVersion=te.dbModelVersion
        self.virtualEnvironmentName=te.virtualEnvironmentName
        self.lensType=te.lensType
        self.cameraWidthLowRes=te.cameraWidthLowRes
        self.cameraHeightLowRes=te.cameraHeightLowRes
        self.tooDarkThreshold=te.tooDarkThreshold
        self.webPort=te.webPort
        self.videoStreamingPort=te.videoStreamingPort
        self.measurementUnits=te.measurementUnits
        self.pumpPurgeTimeSeconds=te.pumpPurgeTimeSeconds
        self.mixerCleanTimeSeconds=te.mixerCleanTimeSeconds
        self.mixerCleanCycles=te.mixerCleanCycles
        self.fillTimePerML=te.fillTimePerML
        self.reagentRemainingMLAlarmThreshold=te.reagentRemainingMLAlarmThreshold
        self.reagentAlmostEmptyAlarmEnable=te.reagentAlmostEmptyAlarmEnable
        self.pauseInSecsBeforeEmptyingMixingChamber=te.pauseInSecsBeforeEmptyingMixingChamber
        self.iftttSecretKey=te.iftttSecretKey
        self.stopperTighteningInMM=te.stopperTighteningInMM
        self.sendMeasurementReports=te.sendMeasurementReports
        self.enableConsoleOutput=te.enableConsoleOutput
        self.manageDatabases=te.manageDatabases
        
    def loadProcessingParametersFromDB(self):
        from tester.models import TesterProcessingParameters
        tpp=TesterProcessingParameters.objects.get(pk=1)
        self.framesPerSecond=tpp.framesPerSecond
        self.referenceCenterRow=tpp.defaultReferenceCenterRow
        self.referenceCenterCol=tpp.defaultReferenceCenterCol
        self.avgDotDistance=tpp.defaultAvgDotDistance
        self.defaultDotDistance=tpp.defaultAvgDotDistance
        self.skipOrientation=tpp.skipOrientation
        self.maxImageScalingWithoutAdjustment=tpp.maxImageScalingWithoutAdjustment
        self.minImageScalingWithoutAdjustment=tpp.minImageScalingWithoutAdjustment
        self.maxImageRotationWithoutAdjustment=tpp.maxImageRotationWithoutAdjustment
        self.minImageRotationWithoutAdjustment=tpp.minImageRotationWithoutAdjustment
        self.defaultFisheyeExpansionFactor=tpp.defaultFisheyeExpansionFactor
        self.gapTolerance=tpp.gapTolerance
        
    def loadStartupParametersFromDB(self):
        from tester.models import TesterStartupInfo
        tsi=TesterStartupInfo.objects.get(pk=1)
        self.seatedGap=tsi.seatedGap
        self.unseatedGap=tsi.unseatedGap
        
    def saveStartupParametersToDB(self):
        from tester.models import TesterStartupInfo
        tsi=TesterStartupInfo.objects.get(pk=1)
        tsi.seatedGap=self.seatedGap
        tsi.unseatedGap=self.unseatedGap
        tsi.save()
        
    def loadFeaturesFromDB(self):
        from tester.models import TesterFeatureExternal
        self.featureList={}
        testerFeatureList=TesterFeatureExternal.objects.all()
        for fe in testerFeatureList:
            feat=feature(name=fe.featureName)
            feat.featureDescription=fe.featureDescription
            feat.ulClipRowOffset=fe.ulClipRowOffset
            feat.ulClipColOffset=fe.ulClipColOffset
            feat.lrClipRowOffset=fe.lrClipRowOffset
            feat.lrClipColOffset=fe.lrClipColOffset
            feat.learnedWithReferenceDistance=fe.learnedWithReferenceDistance
            feat.usesRaw=fe.usesRaw
            feat.centerImage=fe.centerImage
            feat.useDlib=fe.useDlib
            feat.modelRequired=fe.modelRequired
            feat.roiSideLength=fe.roiSideLength
            feat.cParmValue=fe.cParmValue
            feat.upSampling=fe.upSampling
            feat.dlibPositionRowOffset=fe.dlibPositionRowOffset
            feat.dlibPositionColOffset=fe.dlibPositionColOffset
            feat.dlibUseRowPosition=fe.dlibUseRowPosition
            feat.positionCoefficientA=fe.positionCoefficientA
            feat.positionCoefficientB=fe.positionCoefficientB
            feat.confidenceThreshold=fe.confidenceThreshold
            feat.showConfidenceValues=fe.showConfidenceValues
            self.featureList[feat.featureName]=feat 
            loadModel(self,feat)  
            
    def saveFeaturePosition(self,feat):                  
        from tester.models import TesterFeatureExternal
        testerToUpdate=TesterFeatureExternal.objects.get(featureName=feat.featureName)
        testerToUpdate.ulClipRowOffset=round(feat.ulClipRowOffset)
        testerToUpdate.ulClipColOffset=round(feat.ulClipColOffset)
        testerToUpdate.lrClipRowOffset=round(feat.lrClipRowOffset)
        testerToUpdate.lrClipColOffset=round(feat.lrClipColOffset)
        testerToUpdate.dlibPositionRowOffset=feat.dlibPositionRowOffset
        testerToUpdate.dlibPositionColOffset=feat.dlibPositionColOffset
        testerToUpdate.learnedWithReferenceDistance=feat.learnedWithReferenceDistance
        testerToUpdate.save()
        
    def loadTestDefinitionsFromDB(self):
        from tester.models import TestDefinition
        self.testSequenceList={}
        sequenceList=TestDefinition.objects.all()
        for seq in sequenceList:
            ts=testSequence(seq.testName)
            ts.enableTest=seq.enableTest
            ts.waterVolInML=seq.waterVolInML
            ts.reagent1Slot=seq.reagent1Slot
            if not ts.reagent1Slot is None:
                ts.reagent1Slot=seq.reagent1Slot.slotName
            ts.reagent1AgitateSecs=seq.reagent1AgitateSecs
            ts.reagent1DispenseType=seq.reagent1DispenseType
            ts.reagent1DispenseCount=seq.reagent1DispenseCount
            ts.reagent2Slot=seq.reagent2Slot
            if not ts.reagent2Slot is None:
                ts.reagent2Slot=seq.reagent2Slot.slotName
            ts.reagent2AgitateSecs=seq.reagent2AgitateSecs
            ts.reagent2DispenseType=seq.reagent2DispenseType
            ts.reagent2DispenseCount=seq.reagent2DispenseCount
            ts.reagent3Slot=seq.reagent3Slot
            if not ts.reagent3Slot is None:
                ts.reagent3Slot=seq.reagent3Slot.slotName
            ts.reagent3AgitateSecs=seq.reagent3AgitateSecs
            ts.reagent3DispenseType=seq.reagent3DispenseType
            ts.reagent3DispenseCount=seq.reagent3DispenseCount
            ts.agitateMixtureSecs=seq.agitateMixtureSecs
            ts.delayBeforeReadingSecs=seq.delayBeforeReadingSecs
            ts.colorChartToUse=seq.colorChartToUse.colorSheetName
            ts.tooLowAlarmThreshold=seq.tooLowAlarmThreshold
            ts.tooLowWarningThreshold=seq.tooLowWarningThreshold
            ts.tooHighWarningThreshold=seq.tooHighWarningThreshold
            ts.tooHighAlarmThreshold=seq.tooHighAlarmThreshold
            
            self.testSequenceList[ts.testName]=ts 
        
    def loadColorSheetsFromDB(self):
        from tester.models import ColorSheetExternal,SwatchExternal
        self.colorSheetList={}
        sheetList=ColorSheetExternal.objects.all()
        for csExternal in sheetList:
            cs=colorSheet(csExternal.colorSheetName)
            cs.itemBeingMeasured=csExternal.itemBeingMeasured
            cs.minPermissableValue=csExternal.minPermissableValue
            cs.maxPermissableValue=csExternal.maxPermissableValue
            self.colorSheetList[cs.colorSheetName]= cs
            swatchListExternal=SwatchExternal.objects.filter(colorSheetName__colorSheetName=cs.colorSheetName)
            for swatchExternal in swatchListExternal: 
                sw=swatch(cs.colorSheetName)
                sw.enabled=swatchExternal.enabled
                sw.swatchRow=swatchExternal.swatchRow
                sw.valueAtSwatch=swatchExternal.valueAtSwatch
                sw.lightingConditions=swatchExternal.lightingConditions.lightingConditionName
                sw.channel1=swatchExternal.channel1
                sw.channel2=swatchExternal.channel2
                sw.channel3=swatchExternal.channel3
                sw.swatchULRow=swatchExternal.swatchULRow
                sw.swatchULCol=swatchExternal.swatchULCol
                sw.swatchLRRow=swatchExternal.swatchLRRow
                sw.swatchLRCol=swatchExternal.swatchLRCol
                cs.swatchList[str(sw.swatchRow) + '/' + sw.lightingConditions]=sw
        
    def saveColorSheetIntoDB(self,colorSheetNameToDelete):
        from tester.models import ColorSheetExternal,SwatchExternal,LightingConditionsExternal
        ColorSheetExternal.objects.filter(colorSheetName=colorSheetNameToDelete).delete()
        cse=ColorSheetExternal()
        cs=self.colorSheetList[colorSheetNameToDelete]
        cse.colorSheetName=cs.colorSheetName
        cse.itemBeingMeasured=cs.itemBeingMeasured
        cse.minPermissableValue=cs.minPermissableValue
        cse.maxPermissableValue=cs.maxPermissableValue
        cse.save()
        lightingConditionsList=LightingConditionsExternal.objects.all()
        for lc in lightingConditionsList:
            lcName=lc.lightingConditionName
            floatValueSorted={}
            for swName in cs.swatchList:
                sw=cs.swatchList[swName]
                if sw.lightingConditions==lcName and sw.enabled:
                    floatValueSorted[sw.valueAtSwatch]=sw
                rowIndex=1
            for swName in sorted(floatValueSorted):
                sw=floatValueSorted[swName]
                swe=SwatchExternal()
                swe.colorSheetName=ColorSheetExternal.objects.get(colorSheetName=colorSheetNameToDelete)
                swe.swatchRow=rowIndex
                swe.valueAtSwatch=sw.valueAtSwatch
                swe.lightingConditions=LightingConditionsExternal.objects.get(lightingConditionName=sw.lightingConditions)
                swe.channel1=sw.channel1
                swe.channel2=sw.channel2
                swe.channel3=sw.channel3
                swe.swatchULRow=sw.swatchULRow
                swe.swatchULCol=sw.swatchULCol
                swe.swatchLRRow=sw.swatchLRRow
                swe.swatchLRCol=sw.swatchLRCol
                swe.enabled=sw.enabled
                swe.save()
                rowIndex+=1
        #Rows got reordered so load up the swatches again
        cs.swatchList={}
        swatchListExternal=SwatchExternal.objects.filter(colorSheetName__colorSheetName=cs.colorSheetName)
        for swatchExternal in swatchListExternal: 
            sw=swatch(cs.colorSheetName)
            sw.enabled=swatchExternal.enabled
            sw.swatchRow=swatchExternal.swatchRow
            sw.valueAtSwatch=swatchExternal.valueAtSwatch
            sw.lightingConditions=swatchExternal.lightingConditions.lightingConditionName
            sw.channel1=swatchExternal.channel1
            sw.channel2=swatchExternal.channel2
            sw.channel3=swatchExternal.channel3
            sw.swatchULRow=swatchExternal.swatchULRow
            sw.swatchULCol=swatchExternal.swatchULCol
            sw.swatchLRRow=swatchExternal.swatchLRRow
            sw.swatchLRCol=swatchExternal.swatchLRCol
            cs.swatchList[str(sw.swatchRow) + '/' + sw.lightingConditions]=sw

        self.currentColorSheet=cs
        
    def saveTestResults(self,results):
        from tester.models import TestResultsExternal
        tre=TestResultsExternal()
        tre.testPerformed=self.currentTest
        tre.status='Completed'
        tre.results=round(results,2)
        tre.save()
        
    def saveTestSaveBadResults(self):
        from tester.models import TestResultsExternal
        tre=TestResultsExternal()
        tre.testPerformed=self.currentTest
        if self.abortJob:
            tre.status='Aborted'
        else:
            tre.status='Failed'
        tre.results=None
        tre.save()
        
    def saveReagentPosition(self,reagent):
        from tester.models import ReagentSetup
        if ReagentSetup.objects.get(slotName=reagent).hasAgitator:
            remainingML=round(self.maxPlungerDepthAgitator+self.plungerSteps/self.plungerStepsPerMM,2)
        else:
            remainingML=round(self.maxPlungerDepthNoAgitator+self.plungerSteps/self.plungerStepsPerMM,2)
        self.lastReagentRemainingML=remainingML
        reagentObj=ReagentSetup.objects.get(slotName=reagent)
        reagentObj.fluidRemainingInML=remainingML
        reagentObj.save()
        
    def setCameraRotationMatrix(self,compensationDegrees,compensationScale,centerRow,centerCol):
        self.cameraCompensationTransformationMatrix = cv2.getRotationMatrix2D((centerRow,centerCol),compensationDegrees,compensationScale)                
#        print('Col: ' + str(centerCol) + ', Row: ' + str(centerRow))
        
    def grabFrame(self):
        if not existsWebCam:
            return False
        if self.cameraType==self.CAMERATYPE_PICAM:
            lowResImage=None
            rotLowResImage=None
            if self.lowResImageGenerator==None:
                self.webcam.resolution=(self.cameraHeightLowRes,self.cameraWidthLowRes)
                self.lowResArray=PiRGBArray(self.webcam)
                self.lowResImageGenerator = self.webcam.capture_continuous(self.lowResArray,format='bgr',use_video_port=True)
            for frame in self.lowResImageGenerator:
                lowResImage=frame.array
                self.lowResArray.truncate(0)
                if self.undistortImage: 
                    rot90image=np.rot90(lowResImage)
                    if not self.cameraCompensationTransformationMatrix is None:
                        width,height,channels=rot90image.shape
                        rot90image = cv2.warpAffine(rot90image, self.cameraCompensationTransformationMatrix,(height,width),flags=cv2.INTER_LINEAR)                                            
                    rotLowResImage=self.imageUndistort(rot90image)
                else:    
                    rotLowResImage=np.rot90(lowResImage)
                break
            return rotLowResImage
        else:
            return None,None
        
    def fakeFrame(self):  #Used for simulation on windows computer
        if self.cameraType==self.CAMERATYPE_NONE:
            simulationImageFN=self.basePath + 'Simulation/NoCameraImage-' + str(self.cameraHeightLowRes) + 'x' + str(self.cameraWidthLowRes) + '.jpg'
        else:    
            simulationImageFN=self.basePath + 'Simulation/SimulationImage-' + str(self.cameraHeightLowRes) + 'x' + str(self.cameraWidthLowRes) + '.jpg'
        simulationImage=cv2.imread(simulationImageFN)
        return simulationImage
        
    def getCameraType(self):
        if self.simulation:
            return self.CAMERATYPE_NONE
        try:
            camera=PiCamera()
            self.infoMessage('Picam found')
            camera.close()
            self.infoMessage('Camera type is picamera')
            return self.CAMERATYPE_PICAM
        except:
#            traceback.print_exc()
            self.infoMessage('No camera found')
            self.systemStatus="Stopped - No Camera Found"
            self.simulation=True
            return self.CAMERATYPE_NONE
            
    def webcamInitialize(self):
        if self.cameraType==self.CAMERATYPE_PICAM:
            self.webcam=PiCamera()
            self.webcam.framerate = self.framesPerSecond  
            self.webcam.resolution=(self.cameraHeightLowRes,self.cameraWidthLowRes)
            time.sleep(.1)
            return True 
        else:
            return None      
        
    def webcamRelease(self):
        if self.cameraType==self.CAMERATYPE_PICAM:
            if self.webcam==None:
                return
            else:
                self.webcam.close()
                self.webcam=None
                return
        else:
            return

    def createDefaultBlackScreen(self):
        blackScreen=np.zeros((100,100),dtype=np.uint8)
        r,jpg = cv2.imencode('.jpg',blackScreen)
        self.dummyBlackScreen=jpg        
            
    def imageUndistort(self,image):
        height,width,colors=image.shape
        if self.cameraFisheyeModel==None:
            self.debugMessage('Cannot undistort image because camera model does not exist, returning distorted image')
            return image
        else:
            Rmat=np.array([[1.,0.,0.],[0.,1.,0.],[0.,0.,self.cameraFisheyeExpansionFactor]])
            dst = self.cameraFisheyeModel.undistort(image, undistorted_size=(width, height),R=Rmat)
            return dst
        
    def turnLedOn(self):
        if self.simulation:
            self.ledOn=True
            return
        if existsGPIO:
            GPIO.output(ledGPIO,GPIO.HIGH)
        self.ledOn=True
        return
            
    def turnLedOff(self):
        if self.simulation:
            self.ledOn=False
            return
        if existsGPIO:
            GPIO.output(ledGPIO,GPIO.LOW)
        self.ledOn=False
        return
    
    def flashLights(self):
        self.turnLedOn()
        time.sleep(.5)
        self.turnLedOff()
        time.sleep(.5)
        self.turnLedOn()
        time.sleep(.5)
        self.turnLedOff()
        time.sleep(.5)
        self.turnLedOn()
        time.sleep(.5)
        self.turnLedOff()
        
    def turnPumpOn(self):
        if self.simulation:
            self.pumpOn=True
            return
        if existsGPIO:
            GPIO.output(pumpGPIO,GPIO.HIGH)
        self.pumpOn=True
        return
            
    def turnPumpOff(self):
        if self.simulation:
            self.pumpOn=False
            return
        if existsGPIO:
            GPIO.output(pumpGPIO,GPIO.LOW)
        self.pumpOn=False
        return
    
    def openMixerValve(self):
        if self.simulation:
            self.valveClosed=False
            return
        if existsGPIO:
            GPIO.output(mixerValveGPIO,GPIO.LOW)
        self.valveClosed=False
        return
            
    def closeMixerValve(self):
        if self.simulation:
            self.valveClosed=True
            return
        if existsGPIO:
            GPIO.output(mixerValveGPIO,GPIO.HIGH)
        self.valveClosed=True
        return
    
    def movePlunger(self,mm,speed=None):
        if self.simulation:
            return
        if speed is None:
            speed=self.PLUNGER_HIGH_SPEED
        if mm==self.SET_HOME_POSITION:
            print('Setting Plunger to closed')
            self.plungerState=self.PLUNGER_FULLY_CLOSED
            self.plungerSteps=0
            return True
        if mm==self.TIGHTEN_PAST_HOME_POSITION:
            print('Tightening past home position')
            mm=self.stopperTighteningInMM
        elif self.plungerState==self.PLUNGER_FULLY_CLOSED and mm>0:
            print("Thinks is it already at top")
            return True   #already fully closed
        if not self.plungerEnabled:
            GPIO.output(plungerEnableGPIO,GPIO.LOW)
            time.sleep(.0005)
            self.plungerEnabled=True
        if mm>0:
            GPIO.output(plungerDirectionGPIO,GPIO.LOW)
            stepIncrement=1
        else:
            GPIO.output(plungerDirectionGPIO,GPIO.HIGH)
            stepIncrement=-1
        stepCountThisMove=0
        if speed==self.PLUNGER_HIGH_SPEED:
            stepDelay=.0005
        elif speed==self.PLUNGER_MEDIUM_SPEED:
            stepDelay=.005
        elif speed==self.PLUNGER_LOW_SPEED:
            stepDelay=.05            
        stepsToMove=int(abs(self.plungerStepsPerMM*mm))
        self.plungerStepping=True
        while stepCountThisMove<stepsToMove:
            if self.plungerAbort:
                self.plungerStepping=False
                break
            GPIO.output(plungerStepGPIO,GPIO.HIGH)
            if self.plungerSlow:
                time.sleep(.005)
                GPIO.output(plungerStepGPIO,GPIO.LOW)
                time.sleep(.005)
            else:
                time.sleep(stepDelay)
                GPIO.output(plungerStepGPIO,GPIO.LOW)
                time.sleep(stepDelay)
            stepCountThisMove+=1
            if not self.plungerSteps is None:
                self.plungerSteps+=stepIncrement    
                if self.plungerSteps<0:
                    self.plungerState=self.PLUNGER_MOSTLY_CLOSED
                if self.plungerSteps<-self.mmToRaiseFromOpenToFullyClosed*self.plungerStepsPerMM:
                    self.plungerState=self.PLUNGER_OPEN
                if self.plungerSteps<(-self.mmToRaiseFromOpenToFullyClosed-1)*self.plungerStepsPerMM:
                    self.plungerState=self.PLUNGER_PAST_OPEN 
        if not self.plungerSteps is None:
            if self.plungerSteps>0:
                self.plungerSteps=0
        self.plungerStepping=False       
            
    def plungerDisable(self):
        if self.simulation:
            self.plungerEnabled=False                
            return
        GPIO.output(plungerEnableGPIO,GPIO.HIGH)
        self.plungerEnabled=False                
            
    def moveCarousel(self,revolutions):
        self.carouselStepping=True
        if revolutions==self.SET_HOME_POSITION:
            print('Setting Carousel to home')
            self.carouselSteps=0
            self.carouselCurrentSymbol=='A'
            self.carouselStepping=False            
            return True
        if not self.carouselEnabled:
            GPIO.output(carouselEnableGPIO,GPIO.LOW)
            time.sleep(.0005)
            self.carouselEnabled=True
        if revolutions>0:
            GPIO.output(carouselDirectionGPIO,GPIO.LOW)
            stepIncrement=1
        else:
            GPIO.output(carouselDirectionGPIO,GPIO.HIGH)
            stepIncrement=-1
        stepCountThisMove=0
        stepsToMove=int(abs(self.carouselStepsPerRevolution*revolutions))
        while stepCountThisMove<stepsToMove:
            GPIO.output(carouselStepGPIO,GPIO.HIGH)
            time.sleep(.002)
            GPIO.output(carouselStepGPIO,GPIO.LOW)
            time.sleep(.002)
            stepCountThisMove+=1
            if not self.carouselSteps is None:
                self.carouselSteps+=stepIncrement
        self.carouselStepping=False            

            
    def carouselDisable(self):
        if self.simulation:
            self.carouselEnabled=False
            return
        GPIO.output(carouselEnableGPIO,GPIO.HIGH)
        self.carouselEnabled=False  
        
    def agitate(self,revolutions):
        if self.simulation:
            time.sleep(revolutions*.04)
            return
        if not self.agitatorEnabled:
            GPIO.output(agitatorEnableGPIO,GPIO.LOW)
            time.sleep(.0005)
            self.agitatorEnabled=True
        if revolutions>0:
            GPIO.output(agitatorDirectionGPIO,GPIO.HIGH)
        else:
            GPIO.output(agitatorDirectionGPIO,GPIO.LOW)
        stepCountThisMove=0
        stepsToMove=int(abs(4*revolutions))
        while stepCountThisMove<stepsToMove:
            GPIO.output(agitatorStepGPIO,GPIO.HIGH)
            time.sleep(.02)
            GPIO.output(agitatorStepGPIO,GPIO.LOW)
            time.sleep(.02)
            stepCountThisMove+=1        

    def agitatorDisable(self):
        if self.simulation:
            self.agitatorOn=False
            return
        GPIO.output(agitatorEnableGPIO,GPIO.HIGH)
        self.agitatorEnabled=False
        return              
            
    def getID(self):
        return self.testerName
    
    def printDetectionParameters(self):
        print('Detection parameter settings:')
    
    def quit(self):
        if self.simulation:
            return
        GPIO.cleanup()
        
    def addJobToQueue(self,jobToQueue):
        from tester.models import JobExternal,TestDefinition
        newJob=JobExternal()
        newJob.jobToRun=TestDefinition.objects.get(testName=jobToQueue)
        newJob.save()
    
    def anyMoreJobs(self):
        from tester.models import JobExternal
        jobsQueued=JobExternal.objects.filter(jobStatus='Queued')
        for job in jobsQueued:
            if job.timeStamp<=datetime.datetime.now():
                return True
        return False
    
    def getNextJob(self):
        from tester.models import JobExternal,TestResultsExternal
        jobsQueued=JobExternal.objects.filter(jobStatus='Queued')
        for job in jobsQueued:
            if job.timeStamp<=datetime.datetime.now():
                if not job.jobToRun.enableTest:
                    self.infoMessage('Job ' + job.jobToRun.testName + ' skipped since test disabled')
                    skippedTest=TestResultsExternal()
                    skippedTest.testPerformed=job.jobToRun.testName
                    skippedTest.status='Skipped'
                    skippedTest.datetimePerformed=datetime.datetime.now()
                    skippedTest.save()
                    job.delete()
                else:
                    job.jobStatus='Running'
                    job.save()                
                    return job.jobToRun.testName
        return None

    def clearRunningJobs(self):
        from tester.models import JobExternal
        JobExternal.objects.filter(jobStatus='Running').delete()
        
    def getJobDaysText(self,testName):
        from tester.models import TestSchedule
        try:
            test=TestSchedule.objects.get(testToSchedule=testName)
            return test.daysToRun
        except:
            return 'Never'
        
    def getHoursToRunList(self,testName):
        from tester.models import TestSchedule
        hourList=[]
        try:
            test=TestSchedule.objects.get(testToSchedule=testName)
            for timeOfDay in test.hoursToRun.all():
                timeSegs=str(timeOfDay).split(':')
                hourList.append(str(timeSegs[0] + ':' + timeSegs[1]))
        except:
            pass
        return hourList
        
def getBasePath():
    programPath=os.path.realpath(__file__)
    programPathForwardSlash=programPath.replace('\\','/')
    programPathList=programPathForwardSlash.split('/')
    numPathSegments=len(programPathList)
    basePath=''
    pathSegment=0
    while pathSegment<numPathSegments-1:
        basePath+=programPathList[pathSegment] + '/'
        pathSegment+=1
#    print(basePath)
    return basePath
            
        
if __name__ == '__main__':
    basePath=getBasePath()
    sys.path.append(os.path.abspath(basePath))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'AutoTesterv2.settings'
    django.setup()
    a=Tester(1)