# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-06 01:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20171105_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='customer_setted',
            field=models.CharField(default='false', max_length=5),
        ),
    ]