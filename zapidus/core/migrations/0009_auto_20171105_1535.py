# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-05 17:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_order_customer_setted'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='delivery_orders', to='core.Delivery'),
        ),
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile_orders', to='core.Profile'),
        ),
    ]
