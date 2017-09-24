'''
AutoTester is the controlling software to automatically run water tests
Further info can be found at: https://robogardens.com/?p=928
This software is free for DIY, Nonprofit, and educational uses.
Copyright (C) 2017 - RoboGardens.com
    
Created on Aug 9, 2017

This module configures the autotester database models for django.

@author: Stephen Hayes
'''

from django.db import models
from datetime import datetime
from django.forms import ModelForm
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

# Create your models here.
class TesterExternal(models.Model):
    testerName = models.CharField(max_length=200, default='AutoTester')
    testerVersion = models.CharField(max_length=40, default='v1.0')
    dbModelVersion = models.CharField(max_length=40, default='v1.0')
    virtualEnvironmentName = models.CharField(max_length=40, default='cv')
    lensType = models.CharField(max_length=40, default='piCam-FE')
    fisheyeExpansionFactor = models.FloatField(default=1.2)
    cameraWidthLowRes = models.IntegerField(default=480)
    cameraHeightLowRes = models.IntegerField(default=640)
    tooDarkThreshold = models.IntegerField(default=30)
    webPort = models.IntegerField(default=8000,validators=[MinValueValidator(1001),MaxValueValidator(65535),])
    videoStreamingPort = models.IntegerField(default=8080,validators=[MinValueValidator(1001),MaxValueValidator(65535),])
    measurementUnits = models.CharField(max_length=40, default='US Imperial')
    pumpPurgeTimeSeconds = models.IntegerField(default=4,validators=[MinValueValidator(1),MaxValueValidator(60),])
    mixerCleanTimeSeconds = models.IntegerField(default=4,validators=[MinValueValidator(1),MaxValueValidator(60),])
    mixerCleanCycles = models.IntegerField(default=2,validators=[MinValueValidator(1),MaxValueValidator(4),])
    fillTimePerML = models.FloatField(default=1,validators=[MinValueValidator(.1),MaxValueValidator(10),])
    mlDisplacedByMagnet = models.FloatField(default=.34,validators=[MinValueValidator(.1),MaxValueValidator(1),])
    reagentRemainingMLAlarmThreshold = models.FloatField(default=1.0,validators=[MinValueValidator(0),MaxValueValidator(10)])
    reagentAlmostEmptyAlarmEnable = models.BooleanField(default=True)
    pauseInSecsBeforeEmptyingMixingChamber = models.IntegerField(default=10,validators=[MinValueValidator(0),MaxValueValidator(3600)])
    iftttSecretKey = models.CharField(max_length=50, default=None, help_text="How to set up webhooks and get secret key: https://www.hackster.io/ali-ozkil/ifttt-maker-channel-triggers-21365b")
    sendMeasurementReports = models.BooleanField(default=False)
    currentTimeZone = models.CharField(max_length=50,default='US/Central',help_text="Enter your timezone from the list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")
    stopperTighteningInMM = models.FloatField(default=0,validators=[MinValueValidator(0),MaxValueValidator(3)])
    enableConsoleOutput = models.BooleanField(default=False)
    manageDatabases = models.BooleanField(default=False)
   
    def __str__(self):
        return self.testerName
            
class TesterProcessingParameters(models.Model):
    cameraChannel = models.CharField(max_length=100, default='0')
    cameraIllumSource = models.CharField(max_length=100, default='LED')
    framesPerSecond = models.IntegerField(default=10)
    defaultReferenceCenterRow = models.FloatField(default=256.5)
    defaultReferenceCenterCol = models.FloatField(default=245)
    defaultAvgDotDistance = models.FloatField(default=95)
    skipOrientation = models.BooleanField(default=False)
    maxImageScalingWithoutAdjustment=models.FloatField(default=1.05)
    minImageScalingWithoutAdjustment=models.FloatField(default=.95)
    maxImageRotationWithoutAdjustment=models.FloatField(default=2)
    minImageRotationWithoutAdjustment=models.FloatField(default=-2)
    defaultFisheyeExpansionFactor=models.FloatField(default=1.2)
    gapTolerance=models.FloatField(default=5.0)

class TestResultsExternal(models.Model):
    testPerformed = models.CharField(max_length=200, default=None, help_text="This was the test that was run")
    results = models.FloatField(default=None, null=True, blank=True, help_text="Numeric results from running the test")
    status = models.CharField(max_length=200,default='Completed', help_text="Completion status of the test")
    datetimePerformed = models.DateTimeField(auto_now_add=True, help_text="When the test was run")

    def __str__(self):
        return self.testPerformed

    class Meta:
        ordering = ['datetimePerformed']


class ReagentSetup(models.Model):
    slotName = models.CharField(max_length=1, default='A',unique=True, help_text="The carousel slot letter")
    reagentName = models.CharField(max_length=40, default=None, null=True, help_text="A descriptive name of the reagent")
    used = models.BooleanField(default=False, help_text="Is there anything in the slot (an empty syringe is No)")
    hasAgitator = models.BooleanField(default=False, help_text="Is there an agitator magnet in the syringe")
    fluidRemainingInML = models.FloatField(default=0, help_text="The amount of usable reagent remaining (computed by the machine)")
    REAGENT_TYPE_CHOICES = (('Liquid', 'Liquid'), ('Powder', 'Powder'))
    reagentType = models.CharField(max_length=6, choices=REAGENT_TYPE_CHOICES, default='Liquid', help_text="The type of reagent")
    color = models.CharField(max_length=40, default=None, null=True, blank=True, help_text="An optional description of the color of the reagent")
    reagentInserted = models.DateTimeField(default=datetime.now, null=True, blank=True, help_text="When was the reagent last replaced")
    
    def __str__(self):
        return self.slotName
    
    class Meta:
        ordering = ['slotName']

class ColorSheetExternal(models.Model):
    colorSheetName = models.CharField(max_length=40, default=None,unique=True, help_text="Name of the colorsheet.  A recommended format is whatIsBeingTested-manufacturer")
    itemBeingMeasured = models.CharField(max_length=200, default=None, null=True, help_text="What the test measures")
    minPermissableValue = models.FloatField(default=0, help_text="Minimum possible reading from the test")
    maxPermissableValue = models.FloatField(default=1000, help_text="Maximum possible reading from the test")

    def __str__(self):
        return self.colorSheetName
    
    class Meta:
        ordering = ['colorSheetName']


class HourChoices(models.Model):
    hour = models.TimeField(unique=True, help_text="Tests are on hour boundaries")
    
    def __str__(self):
        return str(self.hour)

    class Meta:
        ordering = ['hour']

    
class TestDefinition(models.Model):
    testName = models.CharField(max_length=40, default='New Test',unique=True, blank=False, validators=[RegexValidator(regex='^New Test$',message='Pick a better name than New Test',inverse_match=True)])
    enableTest = models.BooleanField(default=True)
    waterVolInML = models.FloatField(default=5.0, validators=[MinValueValidator(1),MaxValueValidator(12),])
    reagent1Slot = models.ForeignKey(ReagentSetup, related_name="reagent1", on_delete=models.CASCADE, null=True)
    MEASUREMENT_CHOICES = (('drops', 'drops'), ('ml', 'ml'))
    reagent1DispenseType=models.CharField(max_length=6, choices=MEASUREMENT_CHOICES, default='drops', help_text="How to measure dispensing")
    reagent1DispenseCount = models.FloatField(default=0, null=True, validators=[MinValueValidator(.05),MaxValueValidator(50)])
    reagent1AgitateSecs = models.IntegerField(default=0, null=True, validators=[MinValueValidator(0),MaxValueValidator(1000)])
    reagent2Slot = models.ForeignKey(ReagentSetup, related_name="reagent2", on_delete=models.CASCADE, null=True, blank=True)
    reagent2DispenseType=models.CharField(max_length=6, choices=MEASUREMENT_CHOICES, default='Drops', help_text="How to measure dispensing")
    reagent2DispenseCount = models.IntegerField(default=0, null=True, validators=[MinValueValidator(0),MaxValueValidator(50)])
    reagent2AgitateSecs = models.IntegerField(default=0, null=True, validators=[MinValueValidator(0),MaxValueValidator(1000)])
    reagent3Slot = models.ForeignKey(ReagentSetup, related_name="reagent3", on_delete=models.CASCADE, null=True, blank=True)
    reagent3DispenseType=models.CharField(max_length=6, choices=MEASUREMENT_CHOICES, default='Drops', help_text="How to measure dispensing")
    reagent3DispenseCount = models.IntegerField(default=0, null=True, validators=[MinValueValidator(0),MaxValueValidator(50)])
    reagent3AgitateSecs = models.IntegerField(default=0, null=True, validators=[MinValueValidator(0),MaxValueValidator(1000)])
    agitateMixtureSecs = models.IntegerField(default=0, validators=[MinValueValidator(0),MaxValueValidator(1000)])
    delayBeforeReadingSecs = models.IntegerField(default=0, validators=[MinValueValidator(0),MaxValueValidator(1000)])
    colorChartToUse = models.ForeignKey(ColorSheetExternal, on_delete=models.CASCADE)
    tooLowAlarmThreshold = models.FloatField(default=None, null=True, blank=True)
    tooLowWarningThreshold = models.FloatField(default=None, null=True, blank=True)
    tooHighWarningThreshold = models.FloatField(default=None, null=True, blank=True)
    tooHighAlarmThreshold = models.FloatField(default=None, null=True, blank=True)

    def __str__(self):
        return self.testName
    
    class Meta:
        ordering = ['testName']
        
class TestSchedule(models.Model):
    testToSchedule=models.CharField(max_length=40,null=True,blank=False,default='Dummy')
    enableSchedule = models.BooleanField(default=True)  
    DAYS_TO_RUN = (('Everyday','Everyday'),('2day','Every 2 days'),('3day','Every 3 days'),('4day','Every 4 days'),('5day','Every 5 days'),('10day','Every 10 days'),
                   ('Sunday', 'Every Sunday'), ('Monday', "Every Monday"), ('Tuesday', "Every Tuesday"), ('Wednesday', 'Every Wednesday'),
                   ('Thursday', "Every Thursday"), ('Friday', 'Every Friday'), ('Saturday', 'Every Saturday'),
                   ('14day','Every 2 weeks'),('21day','Every 3 weeks'),('28day','Every 4 weeks'),('Never','Never'))
    daysToRun = models.CharField(max_length=10, choices=DAYS_TO_RUN, default='Never',null=True)
    hoursToRun = models.ManyToManyField(HourChoices, blank=True)

    def __str__(self):
        return self.testToSchedule

    class Meta:
        ordering = ['testToSchedule']


    
class TesterFeatureExternal(models.Model):
    featureName = models.CharField(max_length=40, default='dummy Feature',unique=True)
    featureDescription = models.CharField(max_length=200, default='description of Feature')
    ulClipRowOffset = models.FloatField(default=-50)
    ulClipColOffset = models.FloatField(default=-50)
    lrClipRowOffset = models.FloatField(default=50)
    lrClipColOffset = models.FloatField(default=50)
    learnedWithReferenceDistance = models.FloatField(default=95)
    usesRaw = models.BooleanField(default=False)
    userTrainable = models.BooleanField(default=False)
    centerImage = models.BooleanField(default=False)
    useDlib = models.BooleanField(default=False)
    modelRequired = models.BooleanField(default=True)
    trainingURL = models.CharField(max_length=1000, default='http://robogardens.com')
    roiSideLength = models.IntegerField(default=65)
    cParmValue = models.IntegerField(default=8)
    upSampling = models.IntegerField(default=0)
    dlibPositionRowOffset = models.IntegerField(default=0)
    dlibPositionColOffset = models.IntegerField(default=0)
    dlibUseRowPosition = models.BooleanField(default=True)
    positionCoefficientA = models.FloatField(default=1)
    positionCoefficientB = models.FloatField(default=0)
    confidenceThreshold = models.FloatField(default=1)
    showConfidenceValues = models.BooleanField(default=False)
    
    def __str__(self):
        return self.featureName
    
    class Meta:
        ordering = ['featureName']
        
class TesterStartupInfo(models.Model):
    seatedGap = models.FloatField(default=2)
    unseatedGap = models.FloatField(default=0)

    def __str__(self):
        return str(self.unseatedGap) + '/' + str(self.seatedGap)
    
class LightingConditionsExternal(models.Model):
    lightingConditionName = models.CharField(max_length=40, default='LED',unique=True) 
    channel1 = models.FloatField(default=0) 
    channel2 = models.FloatField(default=0) 
    channel3 = models.FloatField(default=0) 
    
    def __str__(self):
        return self.lightingConditionName

    class Meta:
        ordering = ['lightingConditionName']

class SwatchExternal(models.Model):
    colorSheetName = models.ForeignKey(ColorSheetExternal, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    swatchRow = models.IntegerField(default=1)
    valueAtSwatch = models.FloatField(default=0)
    lightingConditions = models.ForeignKey(LightingConditionsExternal, on_delete=models.CASCADE)
    channel1 = models.FloatField(default=0)
    channel2 = models.FloatField(default=0)
    channel3 = models.FloatField(default=0)
    swatchULRow = models.IntegerField(default=-20)
    swatchULCol = models.IntegerField(default=-20)
    swatchLRRow = models.IntegerField(default=20)
    swatchLRCol = models.IntegerField(default=20)
    
    def __str__(self):
        return str(self.colorSheetName) + '/' + str(self.swatchRow) + '/' + str(self.lightingConditions)

    class Meta:
        ordering = ['colorSheetName__colorSheetName', 'lightingConditions', 'swatchRow']

class JobExternal(models.Model):
    jobToRun = models.ForeignKey(TestDefinition, on_delete=models.CASCADE)
    jobStatus= models.CharField(max_length=20, default='Queued')
    timeStamp = models.DateTimeField(default=datetime.now)
    JOB_INVOCATION=(('SCHEDULED','SCHEDULED'),('MANUAL','MANUAL'))
    jobCause = models.CharField(max_length=10, choices=JOB_INVOCATION, default='MANUAL',null=True)

    def __str__(self):
        return self.jobToRun.testName + '/' + str(self.timeStamp)

    class Meta:
        ordering = ['timeStamp']
        
class JobEntry(models.Model):  #This field is used for display and no instances exist in the db
    jobName = models.CharField(max_length=40)
    jobText = models.CharField(max_length=40)
    jobAction = models.CharField(max_length=40)
    timeStamp = models.DateTimeField(default=datetime.now)
    jobIndex = models.IntegerField(default=0)

    def __str__(self):
        return self.jobName + '/' + str(self.timeStamp)

    class Meta:
        ordering = ['timeStamp']
        
        
        
    