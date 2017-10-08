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
from django.utils.timezone import get_current_timezone, activate

activate(get_current_timezone())

from .databaseAdmin import *

class ConfigureSite(AdminSite):
    site_header='Configure Site'
    
configure_admin=ConfigureSite(name='configure')
