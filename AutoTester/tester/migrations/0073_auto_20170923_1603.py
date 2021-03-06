# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-23 16:03
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tester', '0072_auto_20170922_2307'),
    ]

    operations = [
        migrations.AddField(
            model_name='testerexternal',
            name='stopperTighteningInMM',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)]),
        ),
        migrations.AlterField(
            model_name='testerexternal',
            name='fillTimePerML',
            field=models.FloatField(default=1, validators=[django.core.validators.MinValueValidator(0.1), django.core.validators.MaxValueValidator(10)]),
        ),
        migrations.AlterField(
            model_name='testerexternal',
            name='mixerCleanCycles',
            field=models.IntegerField(default=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)]),
        ),
        migrations.AlterField(
            model_name='testerexternal',
            name='mixerCleanTimeSeconds',
            field=models.IntegerField(default=4, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(60)]),
        ),
        migrations.AlterField(
            model_name='testerexternal',
            name='pauseInSecsBeforeEmptyingMixingChamber',
            field=models.IntegerField(default=10, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3600)]),
        ),
        migrations.AlterField(
            model_name='testerexternal',
            name='pumpPurgeTimeSeconds',
            field=models.IntegerField(default=4, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(60)]),
        ),
        migrations.AlterField(
            model_name='testerexternal',
            name='reagentRemainingMLAlarmThreshold',
            field=models.FloatField(default=1.0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)]),
        ),
    ]
