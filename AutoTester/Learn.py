'''
AutoTester is the controlling software to automatically run water tests
Further info can be found at: https://robogardens.com/?p=928
This software is free for DIY, Nonprofit, and educational uses.
Copyright (C) 2017 - RoboGardens.com
    
Created on Aug 9, 2017

This module implements feature training and testing functions

@author: Stephen Hayes
'''
from skimage.feature import hog
from sklearn import svm
from sklearn.externals import joblib
import cv2
import numpy as np
import os
import dlib
import traceback

categoryList=[]
dataList=[]
targetList=[]

def getFDForClipping(tester,image,centerImage=False):
    if centerImage:
        imageBW=centerLetter(image)
    else:
        imageBW=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    if tester.recordTestedImage:
        cv2.imwrite(tester.basePath + 'Images/lastTestedImage.jpg',imageBW)
    fd = hog(imageBW, orientations=8, pixels_per_cell=(8, 8),cells_per_block=(1, 1), block_norm="L2-Hys",visualise=False)
    return fd
    
def centerLetter(image):
    imgbw=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    ret2,thresh = cv2.threshold(imgbw,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)  #Thresh - white letter, black background
    im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) 
    largestContour=None
    largestContourArea=0 
    contourIndex=0 
    for contour in contours:
        if cv2.contourArea(contour)>largestContourArea: 
            largestContour=contour
            largestContourIndex=contourIndex
            largestContourArea=cv2.contourArea(contour)
        contourIndex+=1
    M=cv2.moments(largestContour)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    invMask=255-thresh  # black letter, white background
    background=invMask*imgbw  #grey background, black letter
    totalIntensity=np.sum(background)
    nonzeroPixels=np.count_nonzero(invMask)
    avgIntensity=round(totalIntensity/nonzeroPixels)
    palate=np.ones((80,80),dtype=np.uint8)*int(avgIntensity)
    cv2.drawContours(palate[40-cY:,40-cX:],contours,largestContourIndex,(0,0,0),-1,hierarchy=hierarchy,maxLevel=1)    
    return palate

def getListOfDlibSamples(pathToTrainingDirectory):
    sampleList=[]
    potentialSampleList=sorted(os.listdir(pathToTrainingDirectory))
    for potentialSampleFilename in potentialSampleList:
        fileNameParts=potentialSampleFilename.split('%')
        if not len(fileNameParts)==3:
            print('Too many segments (separated by %) in sample file: ' + potentialSampleFilename) + ' - Ignoring File'
        else:
            testingFlags=fileNameParts[1]
            if not len(testingFlags)==3:
                print('Too many testing Flags: ' + testingFlags + 'Ignoring File')
            else:
                if testingFlags[0]=='1' and testingFlags[2]=='0':
                    sampleList.append(pathToTrainingDirectory + '/' + potentialSampleFilename)
    return sampleList

def getBoundingBoxList(file):
    fileNameParts=file.split('%')
    boxList=[]
    if not len(fileNameParts)==3:
        print('Too many segments (separated by %) in sample file: ' + file) + ' - Ignoring File'
        return None
    boxListString=fileNameParts[2]
    if boxListString=='.jpg':
        return boxList
    boxListBoxString=boxListString.split('(')
    for boxListComponent in boxListBoxString:
        if len(boxListComponent)>4:
            try:
                boxULCoordStr=boxListComponent.split(')')[0]
                boxXLeft=int(boxULCoordStr.split(',')[0])
                boxYTop=int(boxULCoordStr.split(',')[1])
                boxList.append([boxXLeft,boxYTop])
            except:
                traceback.print_exc()
    return boxList

def learnFeatureDlib(feat,tester):
    testImages=[]
    testImageBoxes=[]
    featureName=feat.featureName
    pathToClippingDirectory=tester.basePath + "Training/" + featureName + '/TrainDlib'
    pathToTrainingDirectory=pathToClippingDirectory + '/' + 'dlibTraining'
    trainingList=getListOfDlibSamples(pathToTrainingDirectory)
    for file in trainingList:
        testImageColor=cv2.imread(file)
        testImages.append(cv2.cvtColor(testImageColor,cv2.COLOR_BGR2GRAY))
        numRows,numCols,numColors=testImageColor.shape
        boxList=getBoundingBoxList(file)
        boxesForThisImage=[]
        if not boxList is None:            
            for box in boxList:
                left=box[0]
                right=left+feat.roiSideLength
                top=box[1]
                bottom=top+feat.roiSideLength
                print("Left: " + str(left) + ", Top: " + str(top) + "Right: " + str(right) + ", Bottom: " + str(bottom))
    #            if left<0 or top<0 or right>=numCols or bottom>=numRows:
    #                print("Tossed box: Left: " + str(left) + ", Top: " + str(top) + "Right: " + str(right) + ", Bottom: " + str(bottom))
    #            else:
    #            testBox=dlib.rectangle(left=box.xLeft,top=box.yTop,right=box.xRight,bottom=box.yBottom)
                testBox=dlib.rectangle(left=left,top=top,right=right,bottom=bottom)
                boxesForThisImage.append(testBox)
        testImageBoxes.append(boxesForThisImage)
    # Now let's do the training.  The train_simple_object_detector() function has a
    # bunch of options, all of which come with reasonable default values.  The next
    # few lines goes over some of these options.
    options = dlib.simple_object_detector_training_options()
    # Since faces are left/right symmetric we can tell the trainer to train a
    # symmetric detector.  This helps it get the most value out of the training
    # data.
    # The trainer is a kind of support vector machine and therefore has the usual
    # SVM C parameter.  In general, a bigger C encourages it to fit the training
    # data better but might lead to overfitting.  You must find the best C value
    # empirically by checking how well the trained detector works on a test set of
    # images you haven't trained on.  Don't just leave the value set at 5.  Try a
    # few different C values and see what works best for your data.
    options.C = feat.cParmValue
    options.U = feat.upSampling
    # Tell the code how many CPU cores your computer has for the fastest training.
    options.num_threads = 4
    options.be_verbose = True
    detector = dlib.train_simple_object_detector(testImages, testImageBoxes, options)
    # We could save this detector to disk by uncommenting the following.
    detectorLocation=pathToClippingDirectory + "/detector.svm"
    detector.save(detectorLocation)
    print('Dlib Training Done')
    feat.model=detector
        
#    win_det = dlib.image_window()
#    win_det.set_image(detector)
#    dlib.hit_enter_to_continue()

def learnFeatureSciKit(feat,tester):
    global categoryList
    global featureList
    featureName=feat.featureName
    pathToClippingDirectory=tester.basePath + "Training/" + featureName + '/TrainSciKit'
    pathToTrainingDirectory=pathToClippingDirectory + '/' + 'Train'
    categoryList=[]
    dataList=[]
    targetList=[]
    numSamples=0
    for category in sorted(os.listdir(pathToTrainingDirectory)):
        if os.path.isdir(pathToTrainingDirectory + '/' + category):
            categoryList.append(category)
            for file in sorted(os.listdir(pathToTrainingDirectory + '/' + category)):
                if os.path.isfile(pathToTrainingDirectory + '/' + category + '/' + file):
                    if file[len(file)-4:]==".jpg":  #Use only jpg files
                        trainingImage=cv2.imread(pathToTrainingDirectory + '/' + category + '/' + file)
                        fd=getFDForClipping(tester,trainingImage,centerImage=feat.centerImage)
                        dataList.append(fd)
                        targetList.append(category)
                        numSamples+=1
    print('Started Training with ' + str(numSamples) + ' samples')
    model = svm.SVC(kernel='linear', C = feat.cParmValue , probability=True)
    data=np.array(dataList)
    target=np.array(targetList)
    model.fit(data, target)
    joblib.dump(model, pathToClippingDirectory + '/' + featureName + '-model.pkl') 
    print('SciKit Training Done')
    feat.model=model

def learnFeature(feature,tester):
    if feature.useDlib:
        learnFeatureDlib(feature,tester)
    else:
        learnFeatureSciKit(feature,tester)
    
def loadModel(tester,feature):
    featureName=feature.featureName
    if feature.useDlib:
        pathToFeatureDirectory=tester.basePath + 'Training/' + featureName + '/TrainDlib'
        try:
            modelFilePath=pathToFeatureDirectory + '/detector.svm'
            feature.model=dlib.simple_object_detector(modelFilePath)
        except:
            if feature.modelRequired:
                traceback.print_exc()
                print('Could not load: ' + modelFilePath)
            feature.model=None
    else:
        pathToFeatureDirectory=tester.basePath + 'Training/' + featureName + '/TrainSciKit'
        try:
            modelFilePath=pathToFeatureDirectory + '/' + featureName + '-model.pkl'
            feature.model=joblib.load(modelFilePath)
        except:
            if feature.modelRequired:
                print('Could not load: ' + modelFilePath)
            feature.model=None

def testDlib(feat,image):
    img=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    dets = feat.model(img)
    feat.boundingBoxList=[]
    print("Number of targets detected: {}".format(len(dets)))
    for k, d in enumerate(dets):
#        print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(k, d.left(), d.top(), d.right(), d.bottom()))
#        bbox=[d.left(),d.top(),d.right()-d.left(),d.bottom()-d.top()]
        ulCol=int(d.left())
        ulRow=int(d.top())
        feat.boundingBoxList.append([ulCol,ulRow])
    
def testDlibForVerticalPosition(feat,image):
    testDlib(feat,image)
    possibleVerticalValues=[]
    if feat.boundingBoxList is None:
        return possibleVerticalValues
    for box in feat.boundingBoxList:
        foundAtVertPosition=box[1]*feat.positionCoefficientA+feat.positionCoefficientB
        possibleVerticalValues.append(foundAtVertPosition)
    return possibleVerticalValues
    
def testDlibForHorizontalPosition(feat,image):
    testDlib(feat,image)
    possibleHorizontalValues=[]
    if feat.boundingBoxList is None:
        return possibleHorizontalValues
    for box in feat.boundingBoxList:
        foundAtHorizPosition=box[0]*feat.positionCoefficientA+feat.positionCoefficientB
        possibleHorizontalValues.append(foundAtHorizPosition)
    return possibleHorizontalValues
    
def testFeature(tester,feat,image):
    if feat.model is None:
        print('No model for ' + feat.featureName)
        return None
    else:
        if feat.useDlib:
            testDlib(feat,image)
            return feat.boundingBoxList
        else:
            fd=getFDForClipping(tester,image,centerImage=feat.centerImage)
            fdReshaped=fd.reshape(1,-1)
            classification=feat.model.predict(fdReshaped)[0]
            try:
                # Inverting the values so they are positive.  Smallest value is selected
                categoryConfidence=-feat.model.predict_log_proba(fdReshaped)
                bestConfidence=np.min(categoryConfidence)
                if bestConfidence>feat.confidenceThreshold:
                    badImageFileName=tester.basePath + "Image/UnrecognizedFeatures/feat.featureName-(" + str(bestConfidence) + ')-'+ datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + '.jpg'
                    tester.infoMessage('Confidence too low on feature: ' + feat.featureName + ', confidence: ' + str(bestConfidence) + '. Image saved as ' + badImageFileName)
                    cv2.imwrite(badImageFileName,image)
                    return None
                if feat.showConfidenceValues:
                    print(categoryConfidence)
            except:
                pass            
            feat.lastVisualState=classification
            return classification
        
def insertTrainingGraphic(tester,image):
    try:
        #This inserts a training overlay into the video stream
        font = cv2.FONT_HERSHEY_SIMPLEX        
        cv2.rectangle(image,(tester.featureWindowULCol,tester.featureWindowULRow),(tester.featureWindowLRCol,tester.featureWindowLRRow),(255,255,255),2)
        cv2.putText(image,'Feature: ' + tester.currentFeature.featureName,(20,55), font, .75,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(image,'Current Step Size: ' + str(tester.featureStepSize),(20,85), font, .75,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(image,'(' + str(tester.featureWindowULCol) + ',' + str(tester.featureWindowULRow) + ')',(tester.featureWindowULCol,tester.featureWindowULRow-20), font, .75,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(image,'(' + str(tester.featureWindowLRCol) + ',' + str(tester.featureWindowLRRow) + ')',(tester.featureWindowLRCol-110,tester.featureWindowLRRow+30), font, .75,(255,255,255),2,cv2.LINE_AA)
        if not tester.currentFeature is None:
            if tester.currentFeature.useDlib:
                if tester.currentFeature.boundingBoxList is None:
                    cv2.putText(image,"None",(20,115), font, .75,(255,255,255),2,cv2.LINE_AA)                                
                else:
                    if len(tester.currentFeature.boundingBoxList)==0:    
                        cv2.putText(image,"None",(20,115), font, .75,(255,255,255),2,cv2.LINE_AA) 
                    else:                               
                        for box in tester.currentFeature.boundingBoxList:
                            boxULCol=int(round(box[0]+tester.featureWindowULCol))
                            boxULRow=int(round(box[1]+tester.featureWindowULRow))
                            cv2.rectangle(image,(boxULCol,boxULRow),(boxULCol+tester.currentFeature.roiSideLength,boxULRow+tester.currentFeature.roiSideLength),(0,0,255),2)
                            print('Col Shift: ' + str(box[0]*tester.currentFeature.positionCoefficientA+tester.currentFeature.positionCoefficientB) + ', Row Shift: ' + str(box[1]*tester.currentFeature.positionCoefficientA+tester.currentFeature.positionCoefficientB))
            else:
                if not tester.currentFeature.lastVisualState is None:
                    cv2.putText(image,tester.currentFeature.lastVisualState,(20,115), font, .75,(255,255,255),2,cv2.LINE_AA)                                
    except:
        traceback.print_exc()

if __name__ == '__main__':
    learnClipping(21)