# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import random
import string

from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


from fcm_django.models import FCMDevice


# Create your models here.

class Profile(models.Model):
    '''
    Extende a classe User
    '''
    user = models.OneToOneField(
        User, primary_key=True, unique=True, related_name='user_profile')
    last_message = models.CharField(max_length=180)
    device = models.ForeignKey(
        FCMDevice, related_name='device_profile', null=True)

    def __str__(self):
        return "%s %s" % (self.user.first_name, self.user.last_name)


class Coordinate(models.Model):
    """
    Associa uma coordenada GPS a um usuário
    """
    driver = models.ForeignKey(
        Profile, related_name='profile_coordinates', on_delete=models.CASCADE)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    latitude = models.DecimalField(max_digits=11, decimal_places=8)
    datetime = models.DateTimeField()

    def __str__(self):
        return "%s %s %s" % (self.longitude, self.latitude, self.datetime)


class Address(models.Model):
    """
    Endereco de entrega
    """
    created_by = models.ForeignKey(
        Profile, related_name='profile_addresses', on_delete=models.CASCADE)
    name = models.CharField(max_length=30, default="")
    city = models.CharField(max_length=30, default="")
    street = models.CharField(max_length=50, default="")
    number = models.CharField(max_length=10, default="")
    details = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=2, default="")
    district = models.CharField(max_length=30, default="")
    cep = models.CharField(max_length=9, default="")

    def __str__(self):
        return "%s, %s, %s, %s, %s" % (self.city, self.district, self.street,
                                       self.number, self.cep)

    def special_print(self):
        """imprime sem espaços"""
        return self.city + "," + self.district + "," + self.street + "," + self.number + "," + self.cep



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Delivery(models.Model):
    delivery_day = models.DateTimeField(auto_now_add=True)
    driver = models.ForeignKey(
        Profile, default=None, null=True, on_delete=models.CASCADE, related_name='dv')
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)
    latitude = models.DecimalField(max_digits=11, decimal_places=8, null=True)

class Order(models.Model):
    key = models.CharField(max_length=8, primary_key=True)
    created_by = models.ForeignKey(
        Profile, related_name='profile_orders_created')
    customer = models.ForeignKey(
        Profile, default=None, null=True, related_name='profile_orders')
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, related_name='address_orders')
    delivery = models.ForeignKey(
        Delivery, default=None, null=True, related_name='delivery_orders')
    delivered = models.BooleanField(default=False)
    customer_setted = models.BooleanField(default=False)
    tries_number = models.IntegerField(default=0)
    deliver_time = models.DateTimeField(default=None, null=True, blank=True)
    forecast_day = models.DateField(null = True)
    forecast_time = models.TimeField(default=None, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    waypoint_position = models.DecimalField(
        default=None, null=True, blank=True, max_digits=2, decimal_places=0)
    distance_from_last = models.IntegerField(
        default=None, null=True, blank=True)  # in meters
    time_from_last = models.IntegerField(
        default=None, null=True, blank=True)  # in minutes

    def save(self):
        if not self.key:
            # Generate ID once, then check the db. If exists, keep trying.
            self.key = id_generator()
            while Order.objects.filter(key=self.key).exists():
                self.key = id_generator()
        if not self.forecast_day:
            self.forecast_day = timezone.now().date() + datetime.timedelta(days=14)
        super(Order, self).save()


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return "%s%s" % ("ZP", ''.join(random.choice(chars) for _ in range(size)))

class Warehouse(models.Model):
    driver = models.ForeignKey(Profile, related_name='profile_warehouse')
    
    def __str__(self):
        return self.driver.user.username