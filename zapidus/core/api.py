# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import Order, Delivery
import json
import requests
import datetime


class QR:
    def __init__(self, code):
        self.code = code
        self.url = "https://zxing.org/w/chart?cht=qr&chs=350x350&chld=L&choe=UTF-8&chl=%s" % self.code
        self.address = Order.objects.get(key=code).address.__str__()


class CodeAddress:
    def __init__(self, code, address):
        self.code = code
        self.address = address


class Route:
    def __init__(self, delivery):
        orders = delivery.delivery_orders.all()
        #orders = []
        # for order in delivery_orders:
        #    orders.append(order)
        if orders.count() < 21:
            order_text = []
            for order in orders:
                if order.delivered != True:
                    order_text.append(order.address.special_print())
            url = self.getDirectionsSite(
                delivery.latitude, delivery.longitude, order_text)
            print(url)
            self.json_string = requests.get(
                url, stream=True).text.encode('utf-8', 'ignore')
            json_string = self.json_string
            json_data = json.loads(json_string)
            waypoint_order = json_data['routes'][0]['waypoint_order']
            seconds = 0
            position = 0
            for x in waypoint_order:
                order = orders[x]
                order.waypoint_position = position
                order.distance_from_last = int(
                    json_data['routes'][0]['legs'][position]['distance']['value'])
                order.time_from_last = int(
                    json_data['routes'][0]['legs'][position]['duration']['value'])
                seconds += int(json_data['routes'][0]
                               ['legs'][position]['duration']['value']) + 300
                order.forecast_time = (
                    delivery.delivery_day + datetime.timedelta(seconds=seconds)).time()
                order.forecast_day = datetime.date.today()
                order.save()
                position += 1
                if order.customer:
                    timedelta = datetime.timedelta(hours=-2)
                    tmp_datetime = datetime.datetime.combine(datetime.date(1, 1, 1), order.forecast_time)
                    time2 = (tmp_datetime + timedelta).time()
                    order.customer.last_message = create_message(title="Está chegando!",
                                                   message="Seu produto chegara por volta das %s"%(time2.strftime('%H:%M')),
                                                   icon="truck",
                                                   datetime=order.forecast_time.strftime('%H:%M'))
                    if order.customer.device:
                        order.customer.device.send_message(
                            title="Title", body="Message")
                    order.customer.save()

    def directions_json(self):
        return self.json_string

    def getDirectionsSite(self, origin_lat, origin_lon, orders_text):
        addresses = ''
        for i in orders_text:
            addresses = "%s%s|" % (addresses, i)
        addresses = addresses.replace(' ', '+')
        origin = "%s,%s" % (origin_lat, origin_lon)
        site_p1 = "https://maps.googleapis.com/maps/api/directions/json?origin="
        site_p2 = "&destination="
        site_p3 = "&waypoints=optimize:true|"
        site_p4 = "&key=AIzaSyB3tWlV-QbQN_SKbtjiqa1HVpjZ8b8J0-4"
        site = "%s%s%s%s%s%s%s" % (
            site_p1, origin, site_p2, origin, site_p3, addresses, site_p4)
        return site


def create_message(title, message, icon, datetime):
    message = '{"title": "%s", "message": "%s", "icon": "%s", "date": "%s"}' % (
        title, message, icon, datetime)
    return message
