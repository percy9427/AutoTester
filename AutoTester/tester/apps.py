'''
AutoTester is the controlling software to automatically run water tests
Further info can be found at: https://robogardens.com/?p=928
This software is free for DIY, Nonprofit, and educational uses.
Copyright (C) 2017 - RoboGardens.com
    
Created on Aug 9, 2017

This module configures the autotester app interface for django.

@author: Stephen Hayes
'''

from django.apps import AppConfig


class TesterConfig(AppConfig):
    name = 'tester'
