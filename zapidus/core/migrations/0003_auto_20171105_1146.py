# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-05 13:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20171104_1701'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('key', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('delivered', models.BooleanField(default=False)),
                ('delivered_time', models.DateTimeField(blank=True, default=None, null=True)),
                ('deliver_time', models.DateTimeField(blank=True, default=None, null=True)),
                ('forecast_day', models.DateField()),
                ('forecast_time', models.TimeField(blank=True, default=None, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('waypoint_position', models.DecimalField(blank=True, decimal_places=0, default=None, max_digits=2, null=True)),
                ('distance_from_last', models.DecimalField(blank=True, decimal_places=0, default=None, max_digits=5, null=True)),
                ('time_from_last', models.DecimalField(blank=True, decimal_places=0, default=None, max_digits=4, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='profile',
            name='address',
        ),
        migrations.AlterField(
            model_name='address',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='core.Profile'),
        ),
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Address'),
        ),
        migrations.AddField(
            model_name='order',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='core.Profile'),
        ),
        migrations.AddField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile_order', to='core.Profile'),
        ),
        migrations.AddField(
            model_name='order',
            name='driver',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dv', to='core.Profile'),
        ),
    ]