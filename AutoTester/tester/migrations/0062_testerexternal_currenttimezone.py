# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-17 18:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tester', '0061_auto_20170917_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='testerexternal',
            name='currentTimeZone',
            field=models.CharField(default='US/Central', help_text='Enter your timezone from the list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones', max_length=50),
        ),
    ]
