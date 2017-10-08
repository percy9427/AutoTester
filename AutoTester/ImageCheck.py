'''
AutoTester is the controlling software to automatically run water tests
Further info can be found at: https://robogardens.com/?p=928
This software is free for DIY, Nonprofit, and educational uses.
Copyright (C) 2017 - RoboGardens.com
    
Created on Aug 9, 2017

This module performs image recognition tasks.

@author: Stephen Hayes
'''

from __future__ import division
import cv2   # @UnresolvedImport
import numpy as np
import math
import os
import datetime
import random
import warnings
import traceback
import operator
warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=FutureWarning) 

def getAvgCIELabFromBGRImage(image):            
    img32=image.astype(np.float32)
    img01=img32/255
    labimg=cv2.cvtColor(img01,cv2.COLOR_BGR2Lab)
    cols,rows,colors=labimg.shape
    numPixels=cols*rows
    l=np.sum(labimg[:,:,0])/numPixels
    a=np.sum(labimg[:,:,1])/numPixels
    b=np.sum(labimg[:,:,2])/numPixels
    return l,a,b

class feature:
    def  __init__(self,name):
        self.featureName=name
        self.description=''
        self.ulClipRowOffset=None
        self.ulClipColOffset=None
        self.lrClipRowOffset=None
        self.lrClipColOffset=None
        self.learnedWithReferenceDistance=None
        self.usesRaw=False
        self.model=None
        self.lastVisualState=None
        self.referenceClip=None
        self.centerImage=False
        self.boundingBoxList=None
        self.previousDarkPixelCount=None
        
    def setTesterClipFromFeature(self,tester):
        tester.featureWindowULRow=int(round(self.ulClipRowOffset+tester.referenceCenterRow))
        tester.featureWindowULCol=int(round(self.ulClipColOffset+tester.referenceCenterCol))
        tester.featureWindowLRRow=int(round(self.lrClipRowOffset+tester.referenceCenterRow))
        tester.featureWindowLRCol=int(round(self.lrClipColOffset+tester.referenceCenterCol))
        tester.currentFeature=self
        tester.featureShow=True
        
    def clipImage(self,tester,image,rowOffset=0,colOffset=0):
        if tester.jigglePhoto:
            rowShift=randomDest=random.randint(-tester.jiggleShiftMax,tester.jiggleShiftMax)
            colShift=randomDest=random.randint(-tester.jiggleShiftMax,tester.jiggleShiftMax)
        else:
            rowShift=0
            colShift=0
#        distanceScaling=tester.avgDotDistance/self.learnedWithReferenceDistance
        ulRow=int(round(self.ulClipRowOffset+tester.referenceCenterRow))+rowShift+rowOffset
        ulCol=int(round(self.ulClipColOffset+tester.referenceCenterCol))+colShift+colOffset
        lrRow=int(round(self.lrClipRowOffset+tester.referenceCenterRow))+rowShift+rowOffset
        lrCol=int(round(self.lrClipColOffset+tester.referenceCenterCol))+colShift+colOffset
        box=image[ulRow:lrRow,ulCol:lrCol,:]
        return box

    def saveFeatureWindow(self,tester):
        self.ulClipRowOffset=tester.featureWindowULRow-tester.referenceCenterRow
        self.ulClipColOffset=tester.featureWindowULCol-tester.referenceCenterCol
        self.lrClipRowOffset=tester.featureWindowLRRow-tester.referenceCenterRow
        self.lrClipColOffset=tester.featureWindowLRCol-tester.referenceCenterCol
        self.learnedWithReferenceDistance=tester.avgDotDistance
        tester.saveFeaturePosition(self)

    def snapPhoto(self,tester,suffix=None):
        pathToImageFolder=tester.basePath + 'Images'
        tester.videoLowResCaptureLock.acquire()
        tester.videoLowResCaptureLock.wait()
        imageCopy=tester.latestLowResImage.copy()
        tester.videoLowResCaptureLock.release()
        clipped=self.clipImage(tester,imageCopy)
        pathToClipping=pathToImageFolder + '/' + self.featureName
        if not os.path.isdir(pathToClipping):
            os.mkdir(pathToClipping)
        if suffix is None:
            fn=pathToClipping + '/' + self.featureName + '-' + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + '.jpg'
        else:
            fn=pathToClipping + '/' + self.featureName + '-' + suffix + '-' + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + '.jpg'
        cv2.imwrite(fn,clipped)
        tester.debugMessage('Clipped image saved at: ' + fn)
    
    def computeGapDarkness(self,image):
        imageBW=255-cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        bW01=cv2.normalize(imageBW.astype('float'), None, 0.0, 1.0, cv2.NORM_MINMAX)
        rowSummation=np.sum(bW01,1)
        firstDerivative=np.diff(rowSummation)
        minValue=-999999
        minIndex=None
        rowIndex=0
        for rowSum in rowSummation:
            if rowSum>minValue:
                minValue=rowSum
                minIndex=rowIndex
            rowIndex+=1
        preceedingRow=minIndex-1
        while preceedingRow>=0:
            if firstDerivative[preceedingRow]<=1:
                break
            else:
                preceedingRow-=1
        followingRow=minIndex+1
        while followingRow<len(firstDerivative):
            if firstDerivative[followingRow]>=-1:
                break
            else:
                followingRow+=1
        baseIntensity=rowSummation[preceedingRow]*(followingRow-preceedingRow)
        rowIndex=preceedingRow
        intensity=0
        while rowIndex<followingRow:
            rowIntensity=rowSummation[rowIndex]-rowSummation[preceedingRow]
            if rowIntensity>0:
                intensity+=rowIntensity
            rowIndex+=1
        return intensity
    
    def getDarkPixelCount(self,image):
        bwImage=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        ret2,th2 = cv2.threshold(bwImage,100,255,cv2.THRESH_BINARY_INV)
#        cv2.imshow("th2",th2)
#        cv2.waitKey(0)
        darkCount=np.sum(th2)
        print(darkCount)
        return darkCount
    
    def initiateDarkPixelCount(self):
        self.previousDarkPixelCount=None
        
    def getDarkPixelChange(self,image):
        latestDarkPixelCount=self.getDarkPixelCount(image)
        if self.previousDarkPixelCount is None:
            self.previousDarkPixelCount=latestDarkPixelCount
            return latestDarkPixelCount,0
        else:
            delta=latestDarkPixelCount-self.previousDarkPixelCount
            self.previousDarkPixelCount=latestDarkPixelCount
            return latestDarkPixelCount,delta                    
        
    def getMixerLevelBasedOnDifference(self,image):
        try:
            if not self.featureName == "MixerLevel":
                return False
            subtractionImage=cv2.absdiff(image,self.referenceClip)
            imageBW=cv2.cvtColor(subtractionImage,cv2.COLOR_BGR2GRAY)
            bW01=cv2.normalize(imageBW.astype('float'), None, 0.0, 1.0, cv2.NORM_MINMAX)
            ret2,th2 = cv2.threshold(imageBW,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            mixerCol=np.sum(th2,1)
            mixerSum=np.sum(mixerCol)
            weightedCol=mixerCol/mixerSum
            numRows=len(mixerCol)
            mixerHeight=range(numRows)
            heightArray=np.asarray(mixerHeight)
            centroidHeight=np.inner(weightedCol,heightArray)
            #Test 1 - Is the centroid below the center?
            if centroidHeight<=(numRows/2-20):
                return 0
            im2, contours, hierarchy = cv2.findContours(th2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            maxArea=0
            secondToMaxArea=0
            maxContour=None
            secondToMaxContour=None
            #Get the 2 biggest contours
            for contour in contours:
                area=cv2.contourArea(contour)
                if area>maxArea:
                    secondToMaxArea=maxArea
                    secondToMaxContour=maxContour
                    maxArea=area
                    maxContour=contour
                elif area>secondToMaxArea:
                    secondToMaxArea=area
                    secondToMaxContour=contour
            x1,y1,w1,h1 = cv2.boundingRect(maxContour)
            maxRect=w1*h1    
            x2,y2,w2,h2 = cv2.boundingRect(secondToMaxContour)
            secondToMaxRect=w2*h2    
            #Test 2 - Does one of the two biggest centroids extend to the bottom:
            if y1+h1>=numRows-1:
        #        print('Max Contour extends to bottom')
                bottomContour=maxContour
                bottomX=x1
                bottomY=y1
                bottomH=h1
                bottomW=w1
                topContour=secondToMaxContour
                topX=x2
                topY=y2
                topH=h2
                topW=w2
            elif y2+h2>=numRows-1:
        #        print('Second to Max Contour extends to bottom')
                bottomContour=secondToMaxContour
                bottomX=x2
                bottomY=y2
                bottomH=h2
                bottomW=w2
                topContour=maxContour
                topX=x1
                topY=y1
                topH=h1
                topW=w1
            else:
                return 0 #Neither conntour goes to the bottom
            minimumWidth=20
            #Test 3 - Is the bottom box wide enough:
            if bottomW<minimumWidth:
                return 0
            addTopContour=True
            if topW<minimumWidth:
                addTopContour=False
            #Test 4 does top contour abut lower contour
            maxTopToBottomSkew=2
            if abs((topY+topH)-bottomY)>maxTopToBottomSkew:
                addTopContour=False
            #Test 5 is the horizontal center of the top contour near the center of the bottom contour
            maxSideToSideSkew=4
            if abs((topX+topW/2)-(bottomX+bottomW/2))>maxSideToSideSkew:
                addTopContour=False            
            if addTopContour:
                pixelHeight=topY
            else:
                pixelHeight=bottomY
            ml=self.positionCoefficientA*pixelHeight+self.positionCoefficientB
            return ml
        except:
            traceback.print_exc()
            return 0

    def isMixerOverflowing(self,image):
        if not self.featureName == "MixerOverflow":
            return False
        subtractionImage=cv2.absdiff(image,self.referenceClip)
        imageBW=cv2.cvtColor(subtractionImage,cv2.COLOR_BGR2GRAY)
        bW01=cv2.normalize(imageBW.astype('float'), None, 0.0, 1.0, cv2.NORM_MINMAX)
        ret2,th2 = cv2.threshold(imageBW,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        mixerCol=np.sum(th2,1)
        mixerSum=np.sum(mixerCol)
        weightedCol=mixerCol/mixerSum
        numRows=len(mixerCol)
        mixerHeight=range(numRows)
        heightArray=np.asarray(mixerHeight)
        centroidHeight=np.inner(weightedCol,heightArray)
        #Test 1 - Is the centroid below the center?
        if centroidHeight<=(numRows/2):
            return False
        im2, contours, hierarchy = cv2.findContours(th2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        maxAreaWideRectangle=0
        maxContourWideRectangle=None
        #Get the biggest contours
        for contour in contours:
            minWidth=20
            minWidthToHeightRatio=2
            area=cv2.contourArea(contour)
            x1,y1,w1,h1 = cv2.boundingRect(contour)
            if area>maxAreaWideRectangle and w1>=minWidth and w1/h1>=minWidthToHeightRatio:
                maxAreaWideRectangle=area
                maxContourWideRectangle=contour
        if maxContourWideRectangle is None:
            return False
        return True

class colorSheet:
    def __init__(self,name):
        self.colorSheetName=name
        self.swatchList={}
        self.tableWidth=80
        self.tableRowHeight=40
        self.tableStartPosition=300
        
    def generateColorTableDisplay(self,tester,width=80,height=40):
        numSwatches=len(self.swatchList)
        if numSwatches<=0:
            return None
        index=0
        for swatchName in sorted(self.swatchList):
            swatch=self.swatchList[swatchName]
            if swatch.lightingConditions==tester.lightingConditionToDisplay:
                index+=1
        colorTable=np.zeros((height*index,width,3),dtype=np.uint8)
        index=0
        for swatchName in sorted(self.swatchList):
            swatch=self.swatchList[swatchName]
            if swatch.lightingConditions==tester.lightingConditionToDisplay:
                colorTable[index*height:(index+1)*height,:,]=swatch.generateBGRRect(width,height)
                index+=1
        return colorTable
    
    def loadSwatchesImage(self,tester,xCoord,yCoord,swatchValue):
        font = cv2.FONT_HERSHEY_SIMPLEX        
        if tester.simulation:
            imageFile=tester.basePath+'Simulation/SimulationImage-640x480.jpg'
            clickableImage=cv2.imread(imageFile)
        else:
            tester.videoLowResCaptureLock.acquire()
            tester.videoLowResCaptureLock.wait()
            clickableImage=tester.latestLowResImage.copy()
            tester.videoLowResCaptureLock.release()
        swatchDelRow=self.getInsideSwatchTablePosition(xCoord,yCoord)
        if not xCoord==-1:
            if swatchDelRow is None:
                #See if the value is the same as an existing swatch
                newSwatch=swatch(tester.currentColorSheet.colorSheetName)
                newSwatch.swatchULRow=yCoord-tester.referenceCenterRow-newSwatch.defaultHalfSideSize
                newSwatch.swatchULCol=xCoord-tester.referenceCenterCol-newSwatch.defaultHalfSideSize
                newSwatch.swatchLRRow=yCoord-tester.referenceCenterRow+newSwatch.defaultHalfSideSize
                newSwatch.swatchLRCol=xCoord-tester.referenceCenterCol+newSwatch.defaultHalfSideSize
                ch1,ch2,ch3=newSwatch.getAvgCIELabImage(tester,clickableImage)
                valueMatch=False
                for swatchName in tester.currentColorSheet.swatchList:
                    sw=tester.currentColorSheet.swatchList[swatchName]
                    if sw.valueAtSwatch==swatchValue:
                        sw.channel1=ch1
                        sw.channel2=ch2
                        sw.channel3=ch3
                        valueMatch=True
                        cv2.putText(clickableImage,'Swatch with Value ' + str(swatchValue) + ' updated',(20,30), font, .75,(255,255,255),2,cv2.LINE_AA)                                            
                        break
                if not valueMatch:
                    newSwatch.channel1=ch1
                    newSwatch.channel2=ch2
                    newSwatch.channel3=ch3
                    newSwatch.valueAtSwatch=swatchValue
                    newSwatch.swatchRow=0
                    tester.currentColorSheet.swatchList['0/LED']=newSwatch
                    cv2.putText(clickableImage,'New Swatch created with Value ' + str(swatchValue),(20,30), font, .75,(255,255,255),2,cv2.LINE_AA)                                                            
                tester.saveColorSheetIntoDB(tester.currentColorSheet.colorSheetName)            
                        
            else:
                for swatchName in tester.currentColorSheet.swatchList:
                    sw=tester.currentColorSheet.swatchList[swatchName]
                    if sw.swatchRow==swatchDelRow and sw.lightingConditions=='LED':
                        sw.enabled=False
                try:
                    tester.saveColorSheetIntoDB(tester.currentColorSheet.colorSheetName)
                except:
                    traceback.print_exc()
                cv2.putText(clickableImage,'Swatch Deleted ' + str(swatchDelRow),(20,30), font, .75,(255,255,255),2,cv2.LINE_AA)                                            
        colorTable=self.generateColorTableDisplay(tester,width=self.tableWidth,height=self.tableRowHeight)
        if not colorTable is None:
            showTableRows,showTableCols,showTableColors=colorTable.shape
            clickableImage[self.tableStartPosition:self.tableStartPosition+showTableRows,:showTableCols,:] =  colorTable
        clickableImageFilename=tester.basePath + '/tester/static/tester/SwatchImage-' + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + '.jpg'
        cv2.rectangle(clickableImage,(2,2),(tester.cameraWidthLowRes-2,tester.cameraHeightLowRes-2),(0,0,255),2)
        cv2.imwrite(clickableImageFilename,clickableImage)
        
    def getInsideSwatchTablePosition(self,xCoordRaw,yCoordRaw):
        for swatchName in self.swatchList:
            swatch=self.swatchList[swatchName]
            swatchTableStartRow=self.tableStartPosition+(swatch.swatchRow-1)*self.tableRowHeight
            swatchTableEndRow=self.tableStartPosition+(swatch.swatchRow)*self.tableRowHeight
            if yCoordRaw>=swatchTableStartRow and yCoordRaw<swatchTableEndRow and xCoordRaw<self.tableWidth:
                return swatch.swatchRow
        return None    
    
class swatch:
    def __init__(self,name):
        self.colorSheetName=name
        self.swatchRow=None
        self.valueAtSwatch=0
        self.lightingConditions='LED'
        self.channel1=0
        self.channel2=0
        self.channel3=0
        self.swatchULRow=-25
        self.swatchULCol=-25
        self.swatchLRRow=25
        self.swatchLRCol=25
        self.enabled=True
        self.defaultHalfSideSize=5
        
    def getAvgCIELabImage(self,tester,imageToBeClipped):
        swatchWindowULRow=int(round(self.swatchULRow+tester.referenceCenterRow))
        swatchWindowULCol=int(round(self.swatchULCol+tester.referenceCenterCol))
        swatchWindowLRRow=int(round(self.swatchLRRow+tester.referenceCenterRow))
        swatchWindowLRCol=int(round(self.swatchLRCol+tester.referenceCenterCol))
        clippedImage=imageToBeClipped[swatchWindowULRow:swatchWindowLRRow,swatchWindowULCol:swatchWindowLRCol,:]
        return getAvgCIELabFromBGRImage(clippedImage)
    
    def generateBGRRect(self,width,height,showValues=True):
        labBlock=np.zeros((height,width,3),dtype=np.float32)
        labBlock[:,:,0]=self.channel1 
        labBlock[:,:,1]=self.channel2 
        labBlock[:,:,2]=self.channel3
        bgrImage=cv2.cvtColor(labBlock,cv2.COLOR_Lab2BGR)*255
        if showValues:
            font = cv2.FONT_HERSHEY_SIMPLEX        
            cv2.putText(bgrImage,str(self.valueAtSwatch),(int(width/2-20),int(height/2)+10), font, .75,(0,0,0),2,cv2.LINE_AA)
        return bgrImage   
    
class resultsSwatch:
    def __init__(self):
        self.swatchDropCount=None
        self.valueAtSwatch=0
        self.lightingConditions='LED'
        self.channel1=0
        self.channel2=0
        self.channel3=0
        
    def generateSwatchImage(self):
        if self.swatchDropCount is None:
            dropStr='' 
        else:
            dropStr='Drop: ' + str(self.swatchDropCount) + ': '  
        swatchStr=dropStr+ str(round(self.valueAtSwatch,2))  
        rowSize=30
        colSize=200
        labBlock=np.ones((rowSize,colSize,3),dtype=np.float32)
        labBlock[:,:,0]=self.channel1
        labBlock[:,:,1]=self.channel2
        labBlock[:,:,2]=self.channel3
        bgrImage=cv2.cvtColor(labBlock,cv2.COLOR_Lab2BGR)*255
        font = cv2.FONT_HERSHEY_SIMPLEX 
        cv2.putText(bgrImage,swatchStr,(10,20), font, .7,(0,0,0),2,cv2.LINE_AA)
        return bgrImage

    def generateSwatchResultList(self,resultSwatchList):
        dropsIsNone=False
        totalNumRows=0
        for rs in resultSwatchList:
            swatchImage=rs.generateSwatchImage()
            numRows,numCols,numChannels=swatchImage.shape
            totalNumRows+=numRows
            if rs.swatchDropCount is None:
                dropsIsNone=True
        listStruct=np.zeros((totalNumRows,numCols,3),dtype=np.float32)
        currentRow=0
        if dropsIsNone:
            sortedResultList=sorted(resultSwatchList,key=operator.attrgetter('valueAtSwatch'))
        else:
            sortedResultList=sorted(resultSwatchList,key=operator.attrgetter('swatchDropCount'))    
        for rs in sortedResultList:
            swatchImage=rs.generateSwatchImage()
            numRows,numCols,numChannels=swatchImage.shape
            listStruct[currentRow:currentRow+numRows,:,:]=swatchImage
            currentRow+=numRows
        return listStruct

def matchMarkers(image,tester):
    bwImage=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    cols,rows=bwImage.shape
    params = cv2.SimpleBlobDetector_Params()
    params.filterByColor=True
    params.blobColor=0
    params.filterByArea=True
    params.minArea=200
    params.maxArea=1000
    params.filterByCircularity=True
    params.minCircularity=.75    
    params.maxCircularity=1
    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(bwImage)
    if len(keypoints)<2:
        print('Not enough keypoints detected.  Storing Bad image in Keypoints directory')
        notEnoughKeypoints = cv2.drawKeypoints(image, keypoints, None, color=(0,255,0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)        
        cv2.imwrite(tester.basepath + "Keypoints/NotEnoughKeypoints-" + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + '.jpg',notEnoughKeypoints)
        return False
#    if len(keypoints)>2:
#        print('More than 2 keypoints detected.  Using 2 darkest ones')
#        tooManyKeypoints = cv2.drawKeypoints(image, keypoints, None, color=(0,255,0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)        
#        cv2.imwrite("/home/pi/testerdata/Keypoints/TooManyKeypoints-" + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + '.jpg',tooManyKeypoints)
    smallestIntensityArea=999999
    smallestIntensitykpX=0
    smallestIntensitykpY=0
    nextSmallestIntensityArea=999999
    nextSmallestIntensitykpX=0
    nextSmallestIntensitykpY=0
    for key in keypoints:
        blackMask=np.zeros((cols,rows),dtype=np.uint8)
        (kpX,kpY)=key.pt
        cv2.circle(blackMask,(int(kpX),int(kpY)),10,(255,255,255),-1)
        intensityInCircle=cv2.bitwise_and(bwImage,bwImage,mask=blackMask)
        intensityInCircleSum=np.sum(intensityInCircle)
        if intensityInCircleSum<smallestIntensityArea:
            nextSmallestIntensityArea=smallestIntensityArea
            nextSmallestIntensitykpX=smallestIntensitykpX
            nextSmallestIntensitykpY=smallestIntensitykpY
            smallestIntensityArea=intensityInCircleSum
            smallestIntensitykpX=kpX
            smallestIntensitykpY=kpY
        elif intensityInCircleSum<nextSmallestIntensityArea:
            nextSmallestIntensityArea=intensityInCircleSum
            nextSmallestIntensitykpX=kpX
            nextSmallestIntensitykpY=kpY            
#        print(intensityInCircleSum)
    if nextSmallestIntensitykpX<=smallestIntensitykpX:
        leftMarkerX=nextSmallestIntensitykpX
        leftMarkerY=nextSmallestIntensitykpY
        rightMarkerX=smallestIntensitykpX
        rightMarkerY=smallestIntensitykpY
    else:
        leftMarkerX=smallestIntensitykpX
        leftMarkerY=smallestIntensitykpY
        rightMarkerX=nextSmallestIntensitykpX
        rightMarkerY=nextSmallestIntensitykpY
#    print(leftMarkerX,leftMarkerY,rightMarkerX,rightMarkerY)
    return leftMarkerX,leftMarkerY,rightMarkerX,rightMarkerY


def getLABValuesOfColorCheckRegion(tester,image):
    box=tester.featureList['ColorCheck'].clipImage(tester,image)
    return getAvgCIELabFromBGRImage(box)

def getLABDistance(l1,a1,b1,l2,a2,b2):
    diff=math.sqrt((l1-l2)**2 + (a1-a2)**2 + (b1-b2)**2)
    return diff

def addIntermediateValues(l1,a1,b1,v1,l2,a2,b2,v2,candidateList,increments=10):
    index=0
    while index<increments:
        intermediateL=((increments-index)*l1+index*l2)/increments
        intermediateA=((increments-index)*a1+index*a2)/increments
        intermediateB=((increments-index)*b1+index*b2)/increments
        intermediateV=((increments-index)*v1+index*v2)/increments
        candidateList.append([intermediateL,intermediateA,intermediateB,intermediateV])
        index+=1
    
    
def prepareMatchCandidateList(tester,colorSheetName):
    #this assumes that the swatches are numbered in linear and consecutive number (run a quick check)
    try:
        consecutive=True
        enoughSamples=True
        i=1
        for swatchRowAndCondition in sorted(tester.colorSheetList[colorSheetName].swatchList):
            potentialSwatch=tester.colorSheetList[colorSheetName].swatchList[swatchRowAndCondition]
            if potentialSwatch.lightingConditions==tester.currentLightingConditions:
                if not potentialSwatch.swatchRow==i:
                    consecutive=False
                i+=1
        if i<2:
            enoughSamples=False
        if not consecutive:
            tester.debugLog.info('Aborting because swatches for color sheet: ' + colorSheetName + ' are not consecutive')
        if not enoughSamples:
            tester.debugLog.info('Aborting because there are <2 swatches for color sheet: ' + colorSheetName)
        candidateList=[]
        currentSwatchNumber=1
        currentSwatch=tester.colorSheetList[colorSheetName].swatchList[str(currentSwatchNumber) + '/' + tester.currentLightingConditions]
        startDiffChannel1=tester.colorSheetList[colorSheetName].swatchList['1/' + tester.currentLightingConditions].channel1-tester.colorSheetList[colorSheetName].swatchList['2/' + tester.currentLightingConditions].channel1
        startDiffChannel2=tester.colorSheetList[colorSheetName].swatchList['1/' + tester.currentLightingConditions].channel2-tester.colorSheetList[colorSheetName].swatchList['2/' + tester.currentLightingConditions].channel2
        startDiffChannel3=tester.colorSheetList[colorSheetName].swatchList['1/' + tester.currentLightingConditions].channel3-tester.colorSheetList[colorSheetName].swatchList['2/' + tester.currentLightingConditions].channel3
        startDiffValue=tester.colorSheetList[colorSheetName].swatchList['1/' + tester.currentLightingConditions].valueAtSwatch-tester.colorSheetList[colorSheetName].swatchList['2/' + tester.currentLightingConditions].valueAtSwatch
        addIntermediateValues(currentSwatch.channel1+startDiffChannel1,currentSwatch.channel2+startDiffChannel2,currentSwatch.channel3+startDiffChannel3,currentSwatch.valueAtSwatch+startDiffValue,currentSwatch.channel1,currentSwatch.channel2,currentSwatch.channel3,currentSwatch.valueAtSwatch,candidateList)
        nextSwatch=tester.colorSheetList[colorSheetName].swatchList[str(currentSwatchNumber+1) + '/' + tester.currentLightingConditions]
        try:
            while True:
                addIntermediateValues(currentSwatch.channel1,currentSwatch.channel2,currentSwatch.channel3,currentSwatch.valueAtSwatch,nextSwatch.channel1,nextSwatch.channel2,nextSwatch.channel3,nextSwatch.valueAtSwatch,candidateList)
                currentSwatch=nextSwatch
                currentSwatchNumber+=1
                nextSwatch=tester.colorSheetList[colorSheetName].swatchList[str(currentSwatchNumber+1) + '/' + tester.currentLightingConditions]
        except:
            lastDiffSwatchNumber=currentSwatchNumber
            endDiffChannel1=tester.colorSheetList[colorSheetName].swatchList[str(lastDiffSwatchNumber) + '/' + tester.currentLightingConditions].channel1-tester.colorSheetList[colorSheetName].swatchList[str(lastDiffSwatchNumber-1) + '/' + tester.currentLightingConditions].channel1
            endDiffChannel2=tester.colorSheetList[colorSheetName].swatchList[str(lastDiffSwatchNumber) + '/' + tester.currentLightingConditions].channel2-tester.colorSheetList[colorSheetName].swatchList[str(lastDiffSwatchNumber-1) + '/' + tester.currentLightingConditions].channel2
            endDiffChannel3=tester.colorSheetList[colorSheetName].swatchList[str(lastDiffSwatchNumber) + '/' + tester.currentLightingConditions].channel3-tester.colorSheetList[colorSheetName].swatchList[str(lastDiffSwatchNumber-1) + '/' + tester.currentLightingConditions].channel3
            endDiffValue=tester.colorSheetList[colorSheetName].swatchList[str(lastDiffSwatchNumber) + '/' + tester.currentLightingConditions].valueAtSwatch-tester.colorSheetList[colorSheetName].swatchList[str(lastDiffSwatchNumber-1) + '/' + tester.currentLightingConditions].valueAtSwatch
            addIntermediateValues(currentSwatch.channel1,currentSwatch.channel2,currentSwatch.channel3,currentSwatch.valueAtSwatch,currentSwatch.channel1+endDiffChannel1,currentSwatch.channel2+endDiffChannel2,currentSwatch.channel3+endDiffChannel3,currentSwatch.valueAtSwatch+endDiffValue,candidateList)
#        for item in candidateList:
#            print(item)
    except:
        tester.debugLog.exception("Creating candidates...") 
    return candidateList 
  
    
def findClosestSwatchMatch(tester,colorSheetName,l,a,b):
    minDistance=99999
    closestSwath=None
    closestIndex=0
    candidateList=prepareMatchCandidateList(tester,colorSheetName)
    for labValues in candidateList:
        swatchDistance=getLABDistance(l,a,b,labValues[0],labValues[1],labValues[2])
        if swatchDistance<minDistance:
            closestValue=labValues[3]
            minDistance=swatchDistance
    return  closestValue
        
def evaluateColor(tester,image,colorSheetName):
    l,a,b=getLABValuesOfColorCheckRegion(tester,image)
    closestValue=findClosestSwatchMatch(tester,colorSheetName,l,a,b)
    resultSwatch=resultsSwatch()
    resultSwatch.swatchDropCount=None
    resultSwatch.valueAtSwatch=closestValue
    resultSwatch.lightingConditions='LED'
    resultSwatch.channel1=l
    resultSwatch.channel2=a
    resultSwatch.channel3=b
    return resultSwatch

def prepareBinaryMatchCandidateList(tester,colorSheetName):
    #this assumes that the swatches are numbered in linear and consecutive number (run a quick check)
    try:
        consecutive=True
        enoughSamples=True
        i=1
        for swatchRowAndCondition in sorted(tester.colorSheetList[colorSheetName].swatchList):
            potentialSwatch=tester.colorSheetList[colorSheetName].swatchList[swatchRowAndCondition]
            if potentialSwatch.lightingConditions==tester.currentLightingConditions:
                if not potentialSwatch.swatchRow==i:
                    consecutive=False
                i+=1
        if i<2:
            enoughSamples=False
        if not consecutive:
            tester.debugLog.info('Aborting because swatches for color sheet: ' + colorSheetName + ' are not consecutive')
        if not enoughSamples:
            tester.debugLog.info('Aborting because there are <2 swatches for color sheet: ' + colorSheetName)
#        currentSwatchNumber=1
#        currentSwatch=tester.colorSheetList[colorSheetName].swatchList[str(currentSwatchNumber) + '/' + tester.currentLightingConditions]
        startChannel1=tester.colorSheetList[colorSheetName].swatchList['1/' + tester.currentLightingConditions].channel1
        startChannel2=tester.colorSheetList[colorSheetName].swatchList['1/' + tester.currentLightingConditions].channel2
        startChannel3=tester.colorSheetList[colorSheetName].swatchList['1/' + tester.currentLightingConditions].channel3
        startValue=tester.colorSheetList[colorSheetName].swatchList['1/' + tester.currentLightingConditions].valueAtSwatch
        candidateList=[]
        endChannel1=tester.colorSheetList[colorSheetName].swatchList['2/' + tester.currentLightingConditions].channel1
        endChannel2=tester.colorSheetList[colorSheetName].swatchList['2/' + tester.currentLightingConditions].channel2
        endChannel3=tester.colorSheetList[colorSheetName].swatchList['2/' + tester.currentLightingConditions].channel3
        endValue=tester.colorSheetList[colorSheetName].swatchList['2/' + tester.currentLightingConditions].valueAtSwatch
        addIntermediateValues(startChannel1,startChannel2,startChannel3,startValue,endChannel1,endChannel2,endChannel3,endValue,candidateList,increments=100)
        candidateList.append([endChannel1,endChannel2,endChannel3,endValue])
    except:
        tester.debugLog.exception("Creating candidates...") 
    return candidateList 
  
def findClosestBinarySwatchMatch(tester,colorSheetName,l,a,b):
    minDistance=99999
    closestSwath=None
    closestIndex=0
    candidateList=prepareBinaryMatchCandidateList(tester,colorSheetName)
    for labValues in candidateList:
        swatchDistance=getLABDistance(l,a,b,labValues[0],labValues[1],labValues[2])
        if swatchDistance<minDistance:
            closestValue=labValues[3]
            minDistance=swatchDistance
    return  closestValue
        
def evaluateColorBinary(tester,image,colorSheetName):
    l,a,b=getLABValuesOfColorCheckRegion(tester,image)
    closestValue=findClosestBinarySwatchMatch(tester,colorSheetName,l,a,b)
    resultSwatch=resultsSwatch()
    resultSwatch.swatchDropCount=None
    resultSwatch.valueAtSwatch=closestValue
    resultSwatch.lightingConditions='LED'
    resultSwatch.channel1=l
    resultSwatch.channel2=a
    resultSwatch.channel3=b
    return resultSwatch

def findLightingEnvironment(tester):    
    tester.videoLowResCaptureLock.acquire()
    tester.videoLowResCaptureLock.wait()
    imageCopy=tester.latestLowResImage.copy()
    tester.videoLowResCaptureLock.release()
    baselineColorSheet=tester.colorSheetList['baseline']
    swatch=baselineColorSheet.swatchList['1/LED']
    l,a,b=swatch.getAvgCIELabImage(tester,imageCopy)
    bestMatchDistance=99999
    bestLightingCondition='LED'
    for swatchNameAndCondition in baselineColorSheet.swatchList:
        swatch=baselineColorSheet.swatchList[swatchNameAndCondition]
        swatchDistance=getLABDistance(l,a,b,swatch.channel1,swatch.channel2,swatch.channel3)
        if swatchDistance<bestMatchDistance:
            bestLightingCondition=swatch.lightingConditions
            bestMatchDistance=swatchDistance
    tester.currentLightingCondition=bestLightingCondition
    tester.lightingConditionToDisplay=bestLightingCondition
    print('Lighting Environment Set to ' + bestLightingCondition)
    return bestLightingCondition
    


if __name__ == '__main__':
    pass
