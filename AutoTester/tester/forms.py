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
 #   def __init__(self, *args, **kwargs):
#        super(ScheduleForm, self).__init__(*args, **kwargs)
#        if self.instance.id:
#            self.fields['testToSchedule'].widget.attrs['readonly'] = True

class TesterForm(forms.ModelForm):
    class Meta:
        model = TesterExternal
        exclude=('testerVersion','dbModelVersion','lensType','fisheyeExpansionFactor','cameraWidthLowRes','cameraHeightLowRes', \
                 'tooDarkThreshold','measurementUnits','pumpPurgeTimeSeconds')
#        widgets = {
#            'testToSchedule': Textarea(attrs={'cols': 80, 'rows': 20}),
#        }
#    def __init__(self, *args, **kwargs):
#        super(TesterForm, self).__init__(*args, **kwargs)




