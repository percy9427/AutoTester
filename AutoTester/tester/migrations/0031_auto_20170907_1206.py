# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-07 17:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tester', '0030_auto_20170907_1205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hourchoices',
            name='hour',
            field=models.CharField(max_length=10),
        ),
    ]
