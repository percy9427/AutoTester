'''
AutoTester is the controlling software to automatically run water tests
Further info can be found at: https://robogardens.com/?p=928
This software is free for DIY, Nonprofit, and educational uses.
Copyright (C) 2017 - RoboGardens.com
    
Created on Aug 9, 2017

This module configures the autotester administrative interface for django.

@author: Stephen Hayes
'''

from django.contrib import admin
from django.contrib.admin import AdminSite
# Register your models here.
from .models import TesterExternal,TesterProcessingParameters,TestResultsExternal, \
    ColorSheetExternal,TestDefinition,TesterFeatureExternal, \
    LightingConditionsExternal,SwatchExternal,ReagentSetup, \
    JobExternal,HourChoices,TestSchedule

#admin.site.register(TesterExternal)
#admin.site.register(TesterProcessingParameters)
##admin.site.register(TestResultsExternal)
#admin.site.register(ColorSheetExternal)
#admin.site.register(TestDefinition)
#admin.site.register(TesterFeatureExternal)
#admin.site.register(LightingConditionsExternal)
#admin.site.register(SwatchExternal)
#admin.site.register(ReagentSetup)
#admin.site.register(JobExternal)
#admin.site.register(HourChoices)
#admin.site.register(TestSchedule)

class ConfigureSite(AdminSite):
    site_header='Configure Site'
    
configure_admin=ConfigureSite(name='configure')
