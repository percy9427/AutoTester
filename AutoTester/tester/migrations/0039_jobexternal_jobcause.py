# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-08 19:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tester', '0038_auto_20170907_2009'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobexternal',
            name='JobCause',
            field=models.CharField(choices=[('SCHEDULED', 'SCHEDULED'), ('MANUAL', 'MANUAL')], default='MANUAL', max_length=10, null=True),
        ),
    ]
