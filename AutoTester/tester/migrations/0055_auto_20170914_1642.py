# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-14 21:42
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tester', '0054_auto_20170913_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testdefinition',
            name='testName',
            field=models.CharField(default='New Test', max_length=40, unique=True, validators=[django.core.validators.RegexValidator(inverse_match=True, message='Pick a better name than New Test', regex='^rNew Test$')]),
        ),
    ]
