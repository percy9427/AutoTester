# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-07 11:39
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tester', '0081_auto_20171007_1126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testdefinition',
            name='titrationMaxDispenses',
            field=models.FloatField(default=10, null=True, validators=[django.core.validators.MinValueValidator(0.05), django.core.validators.MaxValueValidator(50)]),
        ),
    ]
