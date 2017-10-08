'''
AutoTester is the controlling software to automatically run water tests
Further info can be found at: https://robogardens.com/?p=928
This software is free for DIY, Nonprofit, and educational uses.
Copyright (C) 2017 - RoboGardens.com
    
Created on Aug 9, 2017

This module configures the autotester views for django.

@author: Stephen Hayes
'''

from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse
from django.contrib import messages
from django.forms import formset_factory
from django.forms.models import modelformset_factory
from TesterCore import getBasePath
from django.contrib.auth.decorators import login_required
#from django.utils.timezone import activate
import time
import glob
import os
import rpyc
import traceback
# Create your views here.
from django.http import HttpResponse,Http404,HttpResponseRedirect
from .models import TestDefinition,TestResultsExternal,JobExternal,TestResultsExternal, \
    TesterFeatureExternal,SwatchExternal,ColorSheetExternal,TesterExternal,JobEntry,TestSchedule, \
    ReagentSetup,TesterExternal
    
#from .forms import ScheduleFormSet
from .forms import ScheduleForm,TestDefinitionForm, ReagentForm, TesterForm
    
def sendCmdToTester(cmd):
    try:
        c=rpyc.connect("localhost",18861)
        res=c.root.testerOperation(cmd)
        print('Sent: ' + cmd) 
    except:
        print('Cmd: ' + cmd + 'failure reported') 
        
    
def getDisplayInfo(request):
    requestHost=request.get_host()
    testerDBInfo=TesterExternal.objects.get(pk=1)
    streamingPort=testerDBInfo.videoStreamingPort
    hostParts=requestHost.split(':')
    hostWithoutURL=hostParts[0]
    width=testerDBInfo.cameraWidthLowRes
    height=testerDBInfo.cameraHeightLowRes
    return hostWithoutURL + ':' + str(streamingPort), width, height
    
def index(request,formResult):
    return home(request,formResult)   

def navigate(request):
    jumpLoc=None
    try:
        whereToGo=request.GET['navButton']
        sendCmdToTester('CLEAR') 
        jumpLoc="/tester/" + whereToGo + "/"
        return jumpLoc
    except:
        pass
    
   
@login_required
def home(request,formResult):
    if request.method=='GET':
        jumpLoc=navigate(request) 
        if not jumpLoc is None:
            return redirect(jumpLoc)    
    streamingURL,imageWidth,imageHeight=getDisplayInfo(request)
    pageName='Home'
    formToProcess=None
    try:
        testSequenceNameToRun=request.POST['testName']
        formToProcess = 'queueJob'
    except:
        try:
            updateQueueAction=request.POST['jobAction']
            formToProcess = 'updateQueue'
        except:
            pass
    if formToProcess == 'queueJob':
        try:
            te=TesterExternal.objects.get(pk=1)
            newJob=JobExternal()
            newJob.jobToRun=TestDefinition.objects.get(testName=testSequenceNameToRun)
            newJob.save()
#                return HttpResponseRedirect('run')
        except: 
            traceback.print_exc()
            print('Key error:' + testSequenceNameToRun)
    if formToProcess == 'updateQueue':
        print(updateQueueAction)
        updateIndex=updateQueueAction.split('-')
        updateID=int(updateIndex[1])
        if updateIndex[0]=='REMOVE':
            try:
                JobExternal.objects.get(pk=updateID).delete()
            except:
                pass
        elif updateIndex[0]=='DELETE':
            TestResultsExternal.objects.get(pk=updateID).delete()
        elif updateIndex[0]=='CANCEL':
            sendCmdToTester('HOME/Abort')
        else:
            print('Error, unknown action')
#            return HttpResponse("")
    testList=TestDefinition.objects.all()
    jobQueue=JobExternal.objects.all()
    jobList=[]
    for job in reversed(jobQueue):
        newJob=JobEntry()
        newJob.jobName=job.jobToRun.testName
        newJob.jobText=job.jobStatus
        newJob.jobAction= 'REMOVE'
        if job.jobStatus=='Running':
            newJob.jobAction='CANCEL'
        newJob.timeStamp=job.timeStamp
        newJob.jobIndex=job.pk
        jobList.append(newJob)
    maxResultsToShow=10
    currentResult=0
    resultsQueue=TestResultsExternal.objects.all()
    for result in reversed(resultsQueue):
        if currentResult>=maxResultsToShow:
            break
        newJob=JobEntry()
        newJob.jobName=result.testPerformed
        if result.status=='Completed':
            if result.results is None:
                newJob.jobText ='Failed'
            else:
                newJob.jobText='Completed (' + str(round(result.results,2)) + ')'
        elif result.status=='Failed':
            newJob.jobText='Failed'
        else:
            newJob.jobText='Unknown'
        newJob.jobAction='DELETE'
        newJob.timeStamp=result.datetimePerformed
        newJob.jobIndex=result.pk
        jobList.append(newJob)
        currentResult+=1
    context={'pageName':pageName,'streamingURL':streamingURL, 'testList':testList,'jobList':jobList}
    return render(request,'tester/home.html',context)

@login_required
def history(request,formResult):
    pageName='History'
    if request.method=='GET':
        jumpLoc=navigate(request) 
        if not jumpLoc is None:
            return redirect(jumpLoc)    
    if request.method=='POST':
        test="All"
        cmd=request.POST['display']
        test=request.POST['toDisplay']
        sendCmdToTester('Train/' + cmd + '/' + test)
    else:
        test="All"
    testList=TestDefinition.objects.all()
    currentlySelected=test
    if currentlySelected is None or currentlySelected=="All":
        resultsList=TestResultsExternal.objects.all()
    else:
        resultsList=TestResultsExternal.objects.filter(testPerformed=currentlySelected)
    context={'pageName':pageName,'currentlySelected':currentlySelected,'testList':testList,'resultsList':resultsList}
    return render(request,'tester/history.html',context)
   
@login_required
def control(request,formResult):
    pageName='Control'
    if request.method=='GET':
        jumpLoc=navigate(request) 
        if not jumpLoc is None:
            return redirect(jumpLoc)    
    streamingURL,imageWidth,imageHeight=getDisplayInfo(request)
    if request.method=='POST':
        try:
            cmd=request.POST['button']
            lastStepSize=request.POST['stepSize']
            sendCmdToTester('CONTROL/' + cmd + '/' + lastStepSize)
        except:
            pass
        try:
            cmd=request.POST['diag-button']
            lastStepSize=request.POST['stepSize']
            sendCmdToTester('DIAGNOSTIC/' + cmd + '/' + lastStepSize)
        except:
            pass
    else:
        lastStepSize='1'
    stepSizeList=['1','5','10','30','90']
    context={'pageName':pageName,'streamingURL':streamingURL,'lastStepSize':lastStepSize,'stepSizeList':stepSizeList}
    return render(request,'tester/control.html',context)


def generateFeatureOptionsX(featureBeingUsed):
    if featureBeingUsed is None:
        return None
    try:
        feat=TesterFeatureExternal.objects.get(featureName=featureBeingUsed)
        if not feat.userTrainable:
            return None
        if feat.useDlib:
            trainingDirectory=getBasePath() + 'Training/' + featureBeingUsed + '/TrainDlib/dlibTraining'
        else:    
            trainingDirectory=getBasePath() + 'Training/' + featureBeingUsed + '/TrainSciKit/Train'
         
    except:
        return None  

@login_required
def calibrate(request,formResult):
    pageName='Calibration'
    if request.method=='GET':
        jumpLoc=navigate(request) 
        if not jumpLoc is None:
            return redirect(jumpLoc)    
    streamingURL,imageWidth,imageHeight=getDisplayInfo(request)
    if request.method=='POST':
        try:
            cmd=request.POST['button']
        except:
            cmd=""
        try:
            feat=request.POST['toTrain']
        except:
            feat=""
        try:
            lastStepSize=request.POST['stepSize']
        except:
            cmd=""
        sendCmdToTester('CALIBRATE/' + cmd + '/' + feat +'/' + lastStepSize)
    else:
        feat=None
        lastStepSize='1'
    featureList=TesterFeatureExternal.objects.exclude(userTrainable=False)
    currentlySelected=feat
    stepSizeList=['1','5','10','30']
    context={'pageName':pageName,'streamingURL':streamingURL,'currentlySelected':currentlySelected,'featureList':featureList,'lastStepSize':lastStepSize,'stepSizeList':stepSizeList}
    return render(request,'tester/calibrate.html',context)

def createColorSheet(newColorSheetName):
    csNew=ColorSheetExternal()
    csNew.colorSheetName=newColorSheetName
    csNew.save()

def renameColorSheet(oldColorSheetName,newColorSheetName):
    csClone=ColorSheetExternal.objects.get(colorSheetName=oldColorSheetName)  
    csClone.colorSheetName=newColorSheetName
    csClone.save()

def deleteColorSheet(colorSheetNameToDelete):
    csList=ColorSheetExternal.objects.all()
    if len(csList)==1:
        return False
    csClone=ColorSheetExternal.objects.get(colorSheetName=colorSheetNameToDelete).delete() 
    return True

def removeExistingSwatchImageFiles(staticFolderPath):
    fileList=os.listdir(staticFolderPath)
    for file in fileList: 
#        print('found file ' + file)
        if file[0:12]=='SwatchImage-':
            fileToRemove=staticFolderPath + '/' + file
#            print('removed file ' + fileToRemove)
            os.remove(fileToRemove)       
    
def getSwatchImageFile(staticFolderPath):
    fileList=os.listdir(staticFolderPath)
    for file in fileList: 
        if file[0:12]=='SwatchImage-':
            return(file)       
    
@login_required
def colorsheet(request,formResult):
    pageName='Setup ColorSheets'
    if request.method=='GET':
        jumpLoc=navigate(request) 
        if not jumpLoc is None:
            return redirect(jumpLoc)    
    colorSheetImage=None
    streamingURL,imageWidth,imageHeight=getDisplayInfo(request)
    if request.method=='POST':
        setSwatch=False
        colorSheetToUse=None
        try:
            colorSheetToUse=request.POST['csToUse']
        except:
            colorSheetToUse=None
        try:
            actionToPerform=request.POST['csAction']
        except:
            actionToPerform=None
        try:
            newCSName=request.POST['newName']
        except:
            newCSName=None
        try:
            swatchAction=request.POST['swatchAction']
            if swatchAction=='Done':
                colorSheetImage=None
        except:
            setSwatch=False
        try:
            xCoord=request.POST['x']
            yCoord=request.POST['y']
            setSwatch=True
        except:
            xCoord=None
            yCoord=None
        print('colorSheetToUse: ' + str(colorSheetToUse) + ', actionToPerform: ' + str(actionToPerform) + ', newCSName: ' + str(newCSName))
        if actionToPerform=='VIEW':
            sendCmdToTester('SWATCH/SetSheet/' + colorSheetToUse)
            sendCmdToTester('SWATCH/ShowTable')
        elif actionToPerform=='EDIT':
            staticPath=getBasePath() + 'tester/static/tester'
            removeExistingSwatchImageFiles(staticPath)
            sendCmdToTester('SWATCH/SetSheet/' + colorSheetToUse)
            colorSheetImage = None
            count=0
            while colorSheetImage is None and count<10:
                time.sleep(.1)
                colorSheetImage=getSwatchImageFile(staticPath)
                count+=1
        elif actionToPerform=='DELETE':
            res=deleteColorSheet(colorSheetToUse)
            if res:
                oldColorSheet=colorSheetToUse
                sendCmdToTester('SWATCH/Reload')
                colorSheetToUse=ColorSheetExternal.objects.all().first().colorSheetName
                sendCmdToTester('SWATCH/SetSheet/' + colorSheetToUse)
                setSwatch=False
                messages.success(request,'ColorSheet: ' + oldColorSheet + ' deleted')
            else:
                messages.error(request,'Unable to delete ColorSheet: ' + colorSheetToUse + ' (maybe because the last one cannot be deleted)')
        elif actionToPerform=='NEW':
            try:
                newSheetName=request.POST['newName']
                if newSheetName=="":
                    messages.error(request,"Blank names are not permitted")
                elif newSheetName=="New Name":
                    messages.error(request,"Choose a better name than New Name")
                else:
                    matchingColorSheetList = ColorSheetExternal.objects.filter(colorSheetName=newSheetName)
                    if len(matchingColorSheetList)>0:
                        messages.error(request,"Name: " + newSheetName + " already used")
                    else:
                        createColorSheet(newSheetName)
                        colorSheetToUse=newSheetName
                        messages.success(request,'ColorSheet: ' + newSheetName + ' successfully created')
                        sendCmdToTester('SWATCH/Reload')
            except:
                traceback.print_exc()
                messages.error(request,"Choose a New Name")
            sendCmdToTester('SWATCH/SetSheet/' + colorSheetToUse)
        elif actionToPerform=='RENAME AS':
            try:
                newSheetName=request.POST['newName']
                if newSheetName=="":
                    messages.error(request,"Blank names are not permitted")
                elif newSheetName=="New Name":
                    messages.error(request,"Choose a better name than New Name")
                else:
                    matchingColorSheetList = ColorSheetExternal.objects.filter(colorSheetName=newSheetName)
                    if len(matchingColorSheetList)>0:
                        messages.error(request,"Name: " + newSheetName + " already used")
                    else:
                        renameColorSheet(colorSheetToUse,newSheetName)
                        colorSheetToUse=newSheetName
                        sendCmdToTester('SWATCH/Reload')
                        messages.success(request,'Empty ColorSheet created with name ' + newSheetName)
            except:
                messages.error(request,"Choose a New Name")
            sendCmdToTester('SWATCH/SetSheet/' + colorSheetToUse)
        elif not xCoord is None:
            staticPath=getBasePath() + 'tester/static/tester'
            removeExistingSwatchImageFiles(staticPath)
            swatchValue=request.POST['swatchValue']
            sendCmdToTester('SWATCH/Click/' + xCoord + ',' + yCoord + '/'+ str(swatchValue))
            colorSheetImage = None
            count=0
            while colorSheetImage is None and count<10:
                time.sleep(.1)
                colorSheetImage=getSwatchImageFile(staticPath)
                count+=1
    else:
        colorSheetToUse=ColorSheetExternal.objects.all().first().colorSheetName
        colorSheetImage=None
    colorSheetList=ColorSheetExternal.objects.exclude(colorSheetName='baseline')
    if not colorSheetImage is None:
        print(getBasePath())
        context={'pageName':pageName,'streamingURL':streamingURL,'imageWidth':imageWidth, 'imageHeight':imageHeight, \
                 'colorSheetToUse':colorSheetToUse,'colorSheetImage':colorSheetImage}
    else:
        context={'pageName':pageName,'streamingURL':streamingURL,'imageWidth':imageWidth, 'imageHeight':imageHeight,'colorSheetToUse':colorSheetToUse,'colorSheetList':colorSheetList}
    return render(request,'tester/colorsheet.html',context)
    
@login_required
def schedule(request,formResult):
    pageName='Setup Schedules'
    if request.method=='GET':
        jumpLoc=navigate(request) 
        if not jumpLoc is None:
            return redirect(jumpLoc)    
    if request.method=='POST':
        ScheduleFormSet=modelformset_factory(TestSchedule, form=ScheduleForm,extra=0)
        schedFormSet=ScheduleFormSet(request.POST)
        try:
            whatToDoWithFormset=request.POST['actionButton']
        except:
            whatToDoWithFormset='CANCEL'
        if whatToDoWithFormset=='CANCEL':
            schedFormSet=ScheduleFormSet()
            messages.success(request,'Changes Reset')
        if (schedFormSet.is_valid()):
            if whatToDoWithFormset=='UPDATE':
                schedFormSet.save() 
                sendCmdToTester('SCHEDULE/reloadSchedules')           
                messages.success(request,'Schedules updated')
        else:
            messages.error(request,schedFormSet.errors)
    else:
        ScheduleFormSet=modelformset_factory(TestSchedule, form=ScheduleForm,extra=0)
        schedFormSet=ScheduleFormSet()
    context={'pageName':pageName,'schedFormSet':schedFormSet}
    return render(request,'tester/schedule.html',context)
    

@login_required
def testdef(request,formResult):
    pageName='Define Test Sequences'
    if request.method=='GET':
        jumpLoc=navigate(request) 
        if not jumpLoc is None:
            return redirect(jumpLoc)    
    if request.method=='POST':
        try:
            testListButtonStr=request.POST['testListAction']
            testAction=testListButtonStr.split(' ')[0]
            testToChange=testListButtonStr[len(testAction)+1:]
        except:
            testAction=None
            testToChange=None
        try:
            testButtonStr=request.POST['testAction']
        except:
            testButtonStr=None
        try:
            originalTestName=request.POST['originalTestName']
        except:
            originalTestName=None
        if testAction=='EDIT':
            testBeingEdited=TestDefinition.objects.get(testName=testToChange)
            testDef=TestDefinitionForm(instance=testBeingEdited)
            originalTestName=testToChange
            context={'originalTestName':originalTestName,'testToChange':testToChange,'testDef':testDef}
        elif testAction=='DELETE':
            testBeingEdited=TestDefinition.objects.get(testName=testToChange).delete()
            testDefList=TestDefinition.objects.all()
            try:
                TestSchedule.objects.get(testToSchedule=testToChange).delete()
                sendCmdToTester('RELOAD/TestDefs')           
            except:
                pass
            context={'testDefList':testDefList}
            messages.success(request,'Test ' + testToChange + ' deleted')
        elif testButtonStr=='CREATE NEW':
            testDef=TestDefinitionForm()
            testToChange='New Test'
            originalTestName='New Test'
            context={'originalTestName':originalTestName,'testToChange':testToChange,'testDef':testDef}
        elif testButtonStr=='Save':
            if originalTestName=='New Test':
                testDef=TestDefinitionForm(request.POST)
            else:
                try:
                    originalTestDef=TestDefinition.objects.get(testName=originalTestName)
                    testDef=TestDefinitionForm(request.POST,instance=originalTestDef)
                except:
                    testDef=TestDefinitionForm(request.POST)
            if testDef.is_valid():                
                testDefToSave=testDef.save(commit=False)
                retryTestSetup=False
                newTestName=testDefToSave.testName
                if testDefToSave.reagent1DispenseType=='drops' and (testDefToSave.reagent1DispenseCount-int(testDefToSave.reagent1DispenseCount)>0):
                    messages.error(request,'Reagent1 must be an integer number of drops')
                    retryTestSetup=True
                elif testDefToSave.reagent2DispenseType=='drops' and (testDefToSave.reagent2DispenseCount-int(testDefToSave.reagent2DispenseCount)>0):
                    messages.error(request,'Reagent1 must be an integer number of drops')
                    retryTestSetup=True
                elif testDefToSave.reagent3DispenseType=='drops' and (testDefToSave.reagent3DispenseCount-int(testDefToSave.reagent3DispenseCount)>0):
                    messages.error(request,'Reagent1 must be an integer number of drops')
                    retryTestSetup=True
                elif testDefToSave.titrationDispenseType=='drops' and (testDefToSave.titrationMaxDispenses-int(testDefToSave.titrationMaxDispenses)>0):
                    messages.error(request,'Titration Max must be an integer number of drops')
                    retryTestSetup=True
                else:
                #We saved the new or changed test def.  Now update any schedule objects
                    testDefToSave.save()
                    testDef.save_m2m()
                    sendCmdToTester('RELOAD/TestDefs')           
                    messages.success(request,'Test ' + testDefToSave.testName + ' saved')
                    if originalTestName=='New Test':
                        newTestSched=TestSchedule()
                        newTestSched.testToSchedule=newTestName
                        newTestSched.save()
                    else:
                        if originalTestName==newTestName:
                            pass  #New and old name the same, no need to do anything
                        else:
                            try:
                                oldTestSched=TestSchedule.objects.get(testToSchedule=originalTestName)
                            except:
                                oldTestSched=TestSchedule()
                            oldTestSched.testToSchedule=newTestName
                            oldTestSched.save()                    
                testDefList=TestDefinition.objects.all()
                if retryTestSetup:
                    context={'originalTestName':newTestName,'testToChange':newTestName,'testDef':testDef}
                else:    
                    context={'pageName':pageName,'testDefList':testDefList}
            else:
                testToChange=originalTestName
                context={'pageName':pageName,'originalTestName':originalTestName,'testToChange':testToChange,'testDef':testDef}
        elif testButtonStr=='Cancel':
            return redirect('/tester/testdef/')
    else:
        testDefList=TestDefinition.objects.all()
        context={'pageName':pageName,'testDefList':testDefList}
    return render(request,'tester/testdef.html',context)

@login_required
def reagent(request,formResult):
    pageName='Setup Reagents'
    if request.method=='GET':
        jumpLoc=navigate(request) 
        if not jumpLoc is None:
            return redirect(jumpLoc)    
    if request.method=='POST':
        ReagentFormSet=modelformset_factory(ReagentSetup, form=ReagentForm,extra=0)
        reagFormSet=ReagentFormSet(request.POST)
        try:
            whatToDoWithFormset=request.POST['actionButton']
        except:
            whatToDoWithFormset='CANCEL'
        if whatToDoWithFormset=='CANCEL':
            reagFormSet=ReagentFormSet()
            messages.success(request,'Changes Reset')
        if reagFormSet.is_valid():
            if whatToDoWithFormset=='UPDATE':
                reagFormSet.save()            
                sendCmdToTester('RELOAD/Reagents')           
                messages.success(request,'Reagents updated')
        else:
            messages.error(request,reagFormSet.errors)
    else:
        ReagentFormSet=modelformset_factory(ReagentSetup, form=ReagentForm,extra=0)
        reagFormSet=ReagentFormSet()
    context={'pageName':pageName,'reagFormSet':reagFormSet}
    return render(request,'tester/reagent.html',context)
    
@login_required
def logs(request,formResult):
    pageName='Display Logs'
    if request.method=='GET':
        jumpLoc=navigate(request) 
        if not jumpLoc is None:
            return redirect(jumpLoc)    
    logToDisplay="Info"
    logPath=getBasePath() + 'Logs'
    if request.method=='POST':
        try:
            logToDisplay=request.POST["radioLogDisplay"]
        except:
            pass
    print(logToDisplay)
    scrollLog=""
    if logToDisplay=='Info':
        try:
            f=open(logPath + '/' + 'tester.log.1','r')
            scrollLog=f.read()
            f.close()
            f=open(logPath + '/' + 'tester.log','r')
            scrollLog=scrollLog + f.read()
            f.close()
        except:
            traceback.print_exc()
    else:
        try:
            f=open(logPath + '/' + 'debug.log.1','r')
            scrollLog=f.read()
            f.close()
            f=open(logPath + '/' + 'debug.log','r')
            scrollLog=scrollLog + f.read()
            f.close()
        except:
            traceback.print_exc()
    context={'pageName':pageName,'logToDisplay':logToDisplay,'scrollLog':scrollLog}
    return render(request,'tester/logs.html',context)
    
@login_required
def admin(request,formResult):
    pageName='Administrative Setup'
    if request.method=='GET':
        jumpLoc=navigate(request) 
        if not jumpLoc is None:
            return redirect(jumpLoc)    
    if request.method=='POST':
        adminAction=request.POST["actionButton"]
        if adminAction=='CANCEL':
            messages.success(request,'Changes reverted')
            adminInfo=TesterExternal.objects.get(pk=1)
            testerAdminForm=TesterForm(instance=adminInfo)
        elif adminAction=="Test IFTTT": 
            try:
                adminInfo=TesterExternal.objects.get(pk=1)
                testerAdminForm=TesterForm(request.POST,instance=adminInfo)
                partialdata=testerAdminForm.save(commit=False)
                newKey=partialdata.iftttSecretKey
                sendCmdToTester('ALARMS/testIFTTT/' + newKey)
                messages.success(request,'Test Message Sent')
            except:
                traceback.print_exc()
        elif adminAction=='UPDATE':
            adminInfo=TesterExternal.objects.get(pk=1)
            testerAdminForm=TesterForm(request.POST,instance=adminInfo)
            try:
                testerAdminForm.save()
                messages.success(request,'Changes saved. Will take affect after program restarted')
            except:
                traceback.print_exc()
    else:           
        adminInfo=TesterExternal.objects.get(pk=1)
        testerAdminForm=TesterForm(instance=adminInfo)
    context={'pageName':pageName,'testerAdminForm':testerAdminForm}
    return render(request,'tester/admin.html',context)
    


