# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-06 19:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20171105_2330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='last_message',
            field=models.CharField(default='{"date":"","message":"","icon":"","title":""}', max_length=180),
        ),
    ]
