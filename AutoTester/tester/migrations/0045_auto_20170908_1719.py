# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-08 22:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tester', '0044_auto_20170908_1718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testdefinition',
            name='hoursToRun',
            field=models.ManyToManyField(blank=True, to='tester.HourChoices'),
        ),
    ]
