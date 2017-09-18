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
            self.fields['fluidRemainingInML'].widget.attrs['readonly'] = True
            self.fields['slotName'].help_text=None
            self.fields['reagentName'].help_text=None
            self.fields['used'].help_text=None
            self.fields['hasAgitator'].help_text=None
            self.fields['fluidRemainingInML'].help_text=None
            self.fields['reagentType'].help_text=None
            self.fields['color'].help_text=None
            self.fields['reagentInserted'].help_text=None
            
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
        exclude=('testerVersion','lensType','fisheyeExpansionFactor','cameraWidthLowRes','cameraHeightLowRes', \
                 'tooDarkThreshold','measurementUnits','pumpPurgeTimeSeconds')
#        widgets = {
#            'testToSchedule': Textarea(attrs={'cols': 80, 'rows': 20}),
#        }
#    def __init__(self, *args, **kwargs):
#        super(TesterForm, self).__init__(*args, **kwargs)




