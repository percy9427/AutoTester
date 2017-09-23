'''
AutoTester is the controlling software to automatically run water tests
Further info can be found at: https://robogardens.com/?p=928
This software is free for DIY, Nonprofit, and educational uses.
Copyright (C) 2017 - RoboGardens.com
    
Created on Aug 9, 2017

This module configures the autotester web forms for django.

@author: Stephen Hayes
'''

from django import forms
#from django.forms import modelformset_factory, Textarea

from .models import TestSchedule,TestDefinition,ReagentSetup,TesterExternal

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = TestSchedule
        exclude=()
#        widgets = {
#            'testToSchedule': Textarea(attrs={'cols': 80, 'rows': 20}),
#        }
    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['testToSchedule'].widget.attrs['readonly'] = True
            self.fields['hoursToRun'].help_text="Control Select for more than on hour"

class ReagentForm(forms.ModelForm):
    class Meta:
        model = ReagentSetup
        exclude=()
#        widgets = {
#            'testToSchedule': Textarea(attrs={'cols': 80, 'rows': 20}),
#        }
    def __init__(self, *args, **kwargs):
        super(ReagentForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['slotName'].widget.attrs['readonly'] = True
            self.fields['slotName'].label="Carousel Letter"
            self.fields['slotName'].help_text=None
            self.fields['slotName'].widget.attrs['title'] = "This is the carousel slot containing the reagent"
            self.fields['fluidRemainingInML'].widget.attrs['readonly'] = True
            self.fields['reagentName'].help_text=None
            self.fields['reagentName'].widget.attrs['title'] = "Human description of what the reagent is"
            self.fields['used'].help_text=None
            self.fields['used'].widget.attrs['title'] = "Is this reagent being used?"
            self.fields['hasAgitator'].help_text=None
            self.fields['hasAgitator'].widget.attrs['title'] = "If the syringe has an agitator magnet or not"
            self.fields['fluidRemainingInML'].help_text=None
            self.fields['fluidRemainingInML'].widget.attrs['title'] = "Amount of usable reagent left (set by machine)"
            self.fields['reagentType'].help_text=None
            self.fields['reagentType'].widget.attrs['title'] = "If solid or liquid reagent (currently only liquid supported)"
            self.fields['color'].help_text=None
            self.fields['color'].widget.attrs['title'] = "Human description of the color"
            self.fields['reagentInserted'].help_text=None
            self.fields['reagentInserted'].widget.attrs['title'] = "When the reagent was last replaced"
            
class TestDefinitionForm(forms.ModelForm):
    class Meta:
        model = TestDefinition
        exclude=()
#        widgets = {
#            'testToSchedule': Textarea(attrs={'cols': 80, 'rows': 20}),
#        }

class TesterForm(forms.ModelForm):
    class Meta:
        model = TesterExternal
        exclude=('testerVersion','dbModelVersion','lensType','fisheyeExpansionFactor','cameraWidthLowRes','cameraHeightLowRes', \
                 'tooDarkThreshold','measurementUnits','pumpPurgeTimeSeconds','pauseInSecsBeforeEmptyingMixingChamber')

    def __init__(self, *args, **kwargs):
        super(TesterForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['testerName'].label="Name of the Tester"
            self.fields['testerName'].widget.attrs['title'] = "This is the name of the AutoTester.  It will be sent in notifications"
            self.fields['virtualEnvironmentName'].label="Virtual Environment Name"
            self.fields['virtualEnvironmentName'].widget.attrs['title'] = "The name of the virtual environment that the program runs under"
            self.fields['webPort'].label="WebServer Port"
            self.fields['webPort'].widget.attrs['title'] = "Port that the WebServer Listens On, Must be >1000"
            self.fields['videoStreamingPort'].label="Video Streaming Port"
            self.fields['videoStreamingPort'].widget.attrs['title'] = "Port that the Video from the AutoTester is streamed to.  Must be >1000"
            self.fields['mixerCleanTimeSeconds'].label="Seconds to Clean the Mixer"
            self.fields['mixerCleanTimeSeconds'].widget.attrs['title'] = "How many seconds to clean the mixer for each flush cycle"
            self.fields['mixerCleanCycles'].label="Mixer Cleaning Cycles"
            self.fields['mixerCleanCycles'].widget.attrs['title'] = "How many times to clean the mixer at the beginning of each test"
            self.fields['fillTimePerML'].label="Fill time per ML"
            self.fields['fillTimePerML'].widget.attrs['title'] = "Approx how long in seconds to pump 1ML of water into the mixing chamber.  Does not need to exact"
            self.fields['reagentRemainingMLAlarmThreshold'].label="Reagent Low Threshold"
            self.fields['reagentRemainingMLAlarmThreshold'].widget.attrs['title'] = "A reagent is considered low when this many usable ML remain"
            self.fields['reagentAlmostEmptyAlarmEnable'].label="Send Reagent Low Alarms"
            self.fields['reagentAlmostEmptyAlarmEnable'].widget.attrs['title'] = "Check if you want AutoTester to notify you when a reagent is low"
            self.fields['iftttSecretKey'].label="IFTTT Secret Key"
            self.fields['iftttSecretKey'].widget.attrs['title'] = "Set the secret key for sending alarms or reports"
            self.fields['sendMeasurementReports'].label="Enable Measurement Reports"
            self.fields['sendMeasurementReports'].widget.attrs['title'] = "Check if you want a notification each time a test is run"
            self.fields['currentTimeZone'].label="Set Current TimeZone"
            self.fields['currentTimeZone'].widget.attrs['title'] = "Set the timezone of the program"
            self.fields['stopperTighteningInMM'].label="Stopper Tightening Amount"
            self.fields['stopperTighteningInMM'].widget.attrs['title'] = "AutoTester detects when the stoppers begin to lift the carousel.  This is how many mm past that point to go to tighten the stoppers"
            self.fields['enableConsoleOutput'].label="Enable Console Output"
            self.fields['enableConsoleOutput'].widget.attrs['title'] = "Checking this will cause a verbose stream to be displayed on the SSH program console"
            self.fields['manageDatabases'].label="Manage Databases"
            self.fields['manageDatabases'].widget.attrs['title'] = "Checking this and restarting will give access to the internal databases.  Caution in making changes"



