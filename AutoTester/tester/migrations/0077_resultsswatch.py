# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-05 23:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tester', '0076_auto_20170924_2028'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResultsSwatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('swatchDropCount', models.IntegerField(blank=True, default=0, null=True)),
                ('valueAtSwatch', models.FloatField(default=0)),
                ('channel1', models.FloatField(default=0)),
                ('channel2', models.FloatField(default=0)),
                ('channel3', models.FloatField(default=0)),
                ('lightingConditions', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tester.LightingConditionsExternal')),
                ('results', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='swatchForResults', to='tester.TestResultsExternal')),
            ],
            options={
                'ordering': ['results'],
            },
        ),
    ]
