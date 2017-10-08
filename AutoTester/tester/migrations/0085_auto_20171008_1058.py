# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-08 10:58
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tester', '0084_auto_20171007_2358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testdefinition',
            name='titrationAgitateSecs',
            field=models.IntegerField(default=10, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)]),
        ),
    ]
