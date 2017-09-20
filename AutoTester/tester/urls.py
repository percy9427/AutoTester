'''
AutoTester is the controlling software to automatically run water tests
Further info can be found at: https://robogardens.com/?p=928
This software is free for DIY, Nonprofit, and educational uses.
Copyright (C) 2017 - RoboGardens.com
    
Created on Aug 9, 2017

This module configures the autotester url web rules for django.

@author: Stephen Hayes
'''

from django.conf.urls import url

from . import views

app_name='tester'
urlpatterns = [
    #ex: /tester
    url(r'^(?P<formResult>)$', views.index, name='index'),
    #ex: /tester/home
    url(r'^home/?(?P<formResult>[\w-]*)$', views.home, name='home'),
    #ex: /tester/home
    url(r'^history/?(?P<formResult>[\w-]*)$', views.history, name='history'),
    #ex: /tester/control
    url(r'^control/?(?P<formResult>[\w-]*)$',views.control,name='control'),
    #ex: /tester/train
    url(r'^train/?(?P<formResult>[\w-]*)$',views.train,name='train'),
    #ex: /tester/train
    url(r'^reagent/?(?P<formResult>[\w-]*)$',views.reagent,name='reagent'),
    #ex: /tester/train
    url(r'^schedule/?(?P<formResult>[\w-]*)$',views.schedule,name='schedule'),
    #ex: /tester/train
    url(r'^testdef/?(?P<formResult>[\w-]*)$',views.testdef,name='testdef'),
    #ex: /tester/train
    url(r'^colorsheet/?(?P<formResult>[\w-]*)$',views.colorsheet,name='colorsheet'),
    #ex: /tester/train
    url(r'^logs/?(?P<formResult>[\w-]*)$',views.logs,name='logs'),
    #ex: /tester/train
    url(r'^admin/?(?P<formResult>[\w-]*)$',views.admin,name='admin'),
]