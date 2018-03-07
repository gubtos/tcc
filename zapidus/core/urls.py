from django.conf.urls import include, url
from rest_framework.authtoken import views as auth_views
# from routing views
from rest_framework.routers import DefaultRouter

from core import views
from fcm_django.api.rest_framework import FCMDeviceViewSet

router = DefaultRouter()
router.register(r'groups', views.GroupViewSet)
router.register(r'gps', views.CoordinateViewSet)
router.register(r'customers', views.CustomerViewSet)
router.register(r'drivers', views.DriverViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'addresses', views.AddressViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'devices', FCMDeviceViewSet)
router.register(r'deliveries', views.DeliveryViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^index/', views.index),
    url(r'^message/$', views.message),
    url(r'^token/$', views.token),
    url(r'^maps/$', views.Maps.as_view(), name='maps'),
    url(r'^getToken/', auth_views.obtain_auth_token),
    url(r'^user_type/', views.user_type),
    url(r'^auth/', include('rest_framework.urls',
        namespace='rest_framework'))
]
