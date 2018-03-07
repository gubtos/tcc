# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from json import loads

from django.contrib.auth.models import Group, User
from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics, permissions, serializers, status, viewsets
from rest_framework.decorators import (api_view, detail_route, list_route,
                                       permission_classes, renderer_classes)
from rest_framework.exceptions import APIException, NotFound
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.renderers import (HTMLFormRenderer, JSONRenderer,
                                      TemplateHTMLRenderer, StaticHTMLRenderer)
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from api import QR
from models import Address, Coordinate, Delivery, Order, Profile, Warehouse
from permissions import IsDriver
from serializers import (AddressSerializer, CoordinateJSONSerializer,
                         CoordinateSerializer, CustomerSerializer,
                          DeliverySerializer,
                         DriverSerializer, DriversSerializer, GroupSerializer,
                         OrderCreateSerializer, OrderCustomerUpdateSerializer,
                         OrderJSONSerializer, OrderRetrieveSerializer,
                         OrderUpdateSerializer, TokenSerializer,
                         UserSerializer)

# Create your views here.


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def message(request, format=None):
    """
    A view that returns the count of active users in JSON.
    """
    message = request.user.user_profile.last_message
    json_message = loads(message)
    #content = {'json_message': json_message}
    return Response(json_message, status=status.HTTP_200_OK)

@api_view(['GET'])
@renderer_classes((TemplateHTMLRenderer,))
@permission_classes((AllowAny,))
def index(request):
    """
    A view that returns the count of active users in JSON.
    """
    return Response(template_name='index.html')

@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def user_type(request, format=None):
    """
    A view that returns the count of active users in JSON.
    """
    user_type = '{"user_type":"none"}'
    if request.user.groups.filter(name='customer').exists():
        user_type = '{"user_type":"customer"}'
    elif request.user.groups.filter(name='driver').exists():
        user_type = '{"user_type":"driver"}'
    return Response(loads(user_type), status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def token(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        return Response(TokenSerializer(None).data)

    elif request.method == 'POST':
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(profile=request.user.user_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeliveryViewSet(viewsets.ModelViewSet):
    '''
    Profile Views
    '''
    queryset = Delivery.objects.all()
    permission_classes = (IsDriver,)
    serializer_class =  DeliverySerializer

    # def perform_create(self, serializer):
    #     print("a",serializer.create(profile=self.request.user.user_profile))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.create(profile=self.request.user.user_profile)
        json_data = {'id':data.id}
        return Response(json_data, status=status.HTTP_201_CREATED)    

class CustomerViewSet(viewsets.ModelViewSet):
    '''
    Profile Views
    '''
    queryset = Profile.objects.all().filter(user__groups__name='customer')
    permission_classes = (IsAdminUser,)
    serializer_class = CustomerSerializer
    lookup_field = 'username'

class DriverViewSet(viewsets.ModelViewSet):
    '''
    Profile Views
    '''
    queryset = Profile.objects.all().filter(user__groups__name='driver')
    permission_classes = (IsAdminUser,)
    serializer_class = DriverSerializer
    lookup_field = 'username'

class UserViewSet(viewsets.ModelViewSet):
    '''
    Profile Views
    '''
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = UserSerializer
    lookup_field = 'username'


class GroupViewSet(viewsets.ModelViewSet):
    '''
    Group View
    '''
    queryset = Group.objects.all()
    #permission_classes = (IsDriverOrError,IsOwnerOrReadOnly,)
    serializer_class = GroupSerializer
    lookup_field = 'name'
    ordering = ('-id')


class AddressViewSet(viewsets.ModelViewSet):
    '''
    Group View
    '''
    queryset = Address.objects.all()
    #permission_classes = (IsDriverOrError,IsOwnerOrReadOnly,)
    serializer_class = AddressSerializer
    ordering = ('-id')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.user_profile)

    @list_route(methods=['get'], permission_classes=[IsAuthenticated], renderer_classes=[TemplateHTMLRenderer])
    def register(self, request):
        serializer = AddressSerializer()
        return Response({'serializer': serializer}, template_name='address.html')


class OrderViewSet(viewsets.ModelViewSet):
    '''
    Group View
    '''
    queryset = Order.objects.all()
    #permission_classes = (IsDriverOrError,IsOwnerOrReadOnly,)
    ordering = ('-id')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.user_profile)

    def perform_update(self, serializer):
        if self.request.user.groups.filter(name='customer').exists():
            serializer.save(customer=self.request.user.user_profile)
        else:
            tries_number = self.get_object().tries_number + 1            
            serializer.save(tries_number=tries_number)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action =='update':
            if self.request.user.groups.filter(name='customer').exists():
                return OrderCustomerUpdateSerializer
            return OrderUpdateSerializer
        else:
            return OrderRetrieveSerializer

    @list_route(methods=['get'], permission_classes=[IsAuthenticated], renderer_classes=[TemplateHTMLRenderer])
    def qrlist(self, request):
        queryset = Order.objects.all().order_by('forecast_day')[:12]
        if not queryset:
            raise NotFound(detail="ERRO 404, usuario inexistente", code=404)
        orders = []
        for order in queryset:
            orders.append(QR(order.key))
        return Response({'qrlist':orders}, template_name='qrList.html')

    @list_route(methods=['get', 'post'], permission_classes=[IsAuthenticated], renderer_classes=[TemplateHTMLRenderer])
    def route(self, request):
        serializer = OrderJSONSerializer()
        return Response({'serializer': serializer}, template_name='routeform.html')


class CoordinateViewSet(viewsets.ModelViewSet):
    '''
    Coordinate View
    '''
    queryset = Coordinate.objects.all()
    permission_classes = (IsDriver,)
    ordering = ('-id')

    def perform_create(self, serializer):
        serializer.save(driver=self.request.user.user_profile)

    def get_serializer_class(self):
        if self.action == 'create':
            return CoordinateJSONSerializer
        else:
            return CoordinateSerializer


class Maps(generics.ListCreateAPIView):
    serializer_class = CoordinateSerializer
    renderer_classes=[TemplateHTMLRenderer,]

    def get_queryset(self):
        driver = self.request.query_params.get('driver', None)
        day = self.request.query_params.get('day', None)            
        if driver is not None:
            #queryset = Coordinate.objects.filter(driver__username=driver)
            profile = Profile.objects.get(user__id=driver)
            print(profile)
            queryset = profile.profile_coordinates
            if not queryset:
                profile = Profile.objects.get(user__username=driver)
                #queryset = Coordinate.objects.filter(driver__id=driver)  
                queryset = profile.profile_coordinates           
                if not queryset:
                    return Coordinate.objects.none()
        else:
            return Coordinate.objects.none()
        if day is not None:
            x = day.replace('-', ' ').split()
            y = []
            for value in x:
                y.append(int(value))
            start = datetime.datetime(y[2],y[1],y[0], 0, 0, 0)
            end = datetime.datetime(y[2],y[1],y[0], 23, 59, 59)
        else:
            end = timezone.now()    
            start = end - datetime.timedelta(seconds=12*3600)
        queryset = queryset.filter(datetime__range=(start,end)).order_by('datetime')
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = DriversSerializer()
        if not queryset:
            return Response({'serializer': serializer, 'text':'Usuário inválido ou data sem registros'}, 
                template_name='mapsform.html')
        driver = queryset.last().driver
        directions = "["
        for direction in queryset:
            directions = "%s{lat: %s, lng: %s},"%(directions, direction.latitude, direction.longitude)
        directions = directions[:-1]
        directions = "%s]"%directions
        init = "{lat: %s, lng: %s}"%(queryset.last().latitude, queryset.last().longitude)
        init_content = "Ultima posição registrada Horário: %s"%(queryset.last().datetime)
        #except User.DoesNotExist:
        #    raise NotFound(detail="ERRO 404, usuario inexistente", code=404)
        key = "AIzaSyCu2NrIL8zmW8bw9QwVzJhpeOrI0kXOmSs"
        driver_name = "%s %s"%(driver.user.first_name, driver.user.last_name)
        serializer = DriversSerializer()
        return Response({'data':directions, 'init':init, 
                "init_content":init_content,"YOUR_API_KEY":key,
                "driver":driver_name,'base_path': driver_name, 'serializer':serializer},
                template_name='map.html') 
