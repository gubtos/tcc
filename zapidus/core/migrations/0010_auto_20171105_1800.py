# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-05 20:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20171105_1535'),
    ]

    operations = [
        migrations.AddField(
            model_name='delivery',
            name='latitude',
            field=models.DecimalField(decimal_places=8, max_digits=11, null=True),
        ),
        migrations.AddField(
            model_name='delivery',
            name='longitude',
            field=models.DecimalField(decimal_places=8, max_digits=11, null=True),
        ),
    ]
