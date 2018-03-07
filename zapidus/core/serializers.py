# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from json import loads

from django.contrib.auth.models import Group, User
from django.utils.dateparse import parse_datetime
from rest_framework import serializers
from fcm_django.models import FCMDevice
from django.core.exceptions import ObjectDoesNotExist

from core.models import Coordinate, Profile, Address, Order, Delivery, Warehouse
from api import Route

class GroupSerializer(serializers.ModelSerializer):
    '''
        Generic Group Serializer
    '''
    class Meta:
        model = Group
        fields = ['name', ]
        ordering = ['-id']
        extra_kwargs = {
            'url': {'lookup_field': 'name'},
        }

class CoordinateSerializer(serializers.ModelSerializer):
    '''
        Generic GPS Serializer
    '''
    class Meta:
        model = Coordinate
        fields = ['latitude', 'longitude', 'datetime', 'driver']
    driver = serializers.ReadOnlyField(source='driver.user.username')
    datetime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S+%z")


class CoordinateJSONSerializer(serializers.Serializer):
    '''
        JSON input on view
    '''
    json_data = serializers.CharField(max_length=65536)

    def create(self, validated_data):
        json_response = loads(validated_data['json_data'])
        for obj in json_response:
            coordinate = Coordinate(latitude=obj['lat'],
                                    longitude=obj['lon'],
                                    datetime=parse_datetime(obj['dat']),
                                    driver=validated_data['driver'])
            coordinate.save()
        return validated_data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'url',
                  'first_name', 'last_name', 'groups', 'coordinates']
        ordering = ['-id']
        lookup_field = 'username'
        extra_kwargs = {
            'url': {'lookup_field': 'username'},
            'password': {'write_only': True},
            'username': {'write_only': True},
        }
    coordinates = CoordinateSerializer(many=True, read_only=True)
    groups = GroupSerializer(many=True, read_only=True)

    def create(self, validated_data):
        user = self.Meta.model(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'last_message', 'device']
        lookup_field = 'user__username'
        read_only_fields = ['device','last_message']
    user = UserSerializer()

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User(**user_data)
        user.set_password(user_data['password'])
        user.save()
        if not Group.objects.filter(name='driver').exists():
            group = Group(name='driver')
            group.save()
        else:
            group = Group.objects.get(name='driver')
        user.groups.add(group)
        user.save()
        profile = Profile(
            user=user,
            last_message='{"date":"null","message":"Bem Vindo","icon":"welcome","title":"Zapidus"}'
        )
        profile.save()
        return profile


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'last_message', 'device']
        lookup_field = 'user__username'
        read_only_fields = ['device','last_message']
    user = UserSerializer()

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User(**user_data)
        user.set_password(user_data['password'])
        user.save()
        if not Group.objects.filter(name='customer').exists():
            group = Group(name='customer')
            group.save()
        else:
            group = Group.objects.get(name='customer')
        user.groups.add(group)
        user.save()
        profile = Profile(
            user=user,
            last_message='{"date":"null","message":"Bem Vindo","icon":"welcome","title":"Zapidus"}'
        )
        profile.save()
        return profile



class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=500)

    def create(self, profile):
        token = self.validated_data['token']
        if profile.device == None:
            device = FCMDevice(registration_id=token, type='android')
            device.save()
            profile.device = device
        else:
            if profile.device.registration_id != token:
                profile.device.registration_id = token
                profile.device.save()
        profile.save()
        return self.validated_data


class AddressSerializer(serializers.ModelSerializer):
    '''
    Generic Address Serializer
    '''
    class Meta:
        model = Address
        fields = '__all__'
        ordering = ['-id']
    created_by = serializers.ReadOnlyField(source='created_by.user.username')

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['address','created_by','key','url','forecast_day',]
        #depth = 1
        ordering = ['-id']
        read_only_fields = ('key','forecast_day',)
    created_by = serializers.ReadOnlyField(source='created_by.user.username')

    def create(self, validated_data):
        order = Order(
            address=validated_data['address'], 
            created_by=validated_data['created_by']
            )
        order.save()
        return order

class OrderRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['address','created_by','last_coordinates','key','distance_from_last','time_from_last','delivery','customer_setted','url','tries_number','forecast_day','customer','forecast_time','delivered','deliver_time','waypoint_position']
        #depth = 1
        ordering = ['-id']
        read_only_fields = ('key','forecast_day','delivery','last_coordinates')
    created_by = serializers.ReadOnlyField(source='created_by.user.username')
    customer = serializers.ReadOnlyField(source='customer.user.username')
    address = AddressSerializer(many=False)
    last_coordinates = serializers.SerializerMethodField(source='get_last_coordinates')

    def get_last_coordinates(self, obj):
        if obj.delivery:
            driver = obj.delivery.driver
            if driver.profile_coordinates.last():
                gps = driver.profile_coordinates.last()
                mapped_object = {
                    'driver': driver.user.username,
                    'latitude': gps.latitude,
                    'longitude': gps.longitude,
                    'datetime': gps.datetime
                }
        else:
            mapped_object = {
                    'driver': None,
                    'latitude': None,
                    'longitude': None,
                    'datetime': None
                }
        return mapped_object

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['deliver_time','delivered',]
        #depth = 1
        ordering = ['-id']
        read_only_fields = ('key','address')

class OrderCustomerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['customer_setted']
        ordering = ['-id']      

class OrdersJSON(object):
    def __init__(self, json_data, driver):
        json_response = json.loads(json_data)
        if json_response.__len__() < 21:
            addresses = []
            for code in json_response:
                order = Order.objects.get(code)
                addresses.append(code,order.address.__str__())
        return addresses
            
class OrderJSONSerializer(serializers.Serializer):
    def create(self, validated_data):
        return OrdersJSON(**validated_data)
    json_data = serializers.CharField(max_length=8192)

class DeliverySerializer(serializers.ModelSerializer):
    '''
    Generic Address Serializer
    '''
    class Meta:
        model = Delivery
        fields = '__all__'
        ordering = ['-id']
        read_only_fields = ['delivery_day','latitude','longitude']
    driver = serializers.ReadOnlyField(source='driver.user.username')
    delivery_orders = OrderRetrieveSerializer(many=True, read_only=True)
    orders = serializers.CharField(max_length=500, write_only=True)

    def create(self, profile):
        json_data = self.validated_data['orders']
        json_response = loads(json_data)
        lat = json_response['lat']
        lon = json_response['lon']
        orders = json_response['orders']
        delivery = Delivery(driver=profile, latitude=lat, longitude=lon)
        delivery.save()
        for code in orders:
            try:
                order = Order.objects.get(key=code)
                order.delivery = delivery
                order.save()
            except ObjectDoesNotExist:
                error = True
        route = Route(delivery)
        return delivery


class DriversSerializer(serializers.ModelSerializer):

    class Meta:
        model = Warehouse
        fields = ('driver',)
        lookup_field = 'driver'