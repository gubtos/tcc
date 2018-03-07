# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import permissions
from django.contrib.auth.models import Group

class IsDriver(permissions.BasePermission):
    """
    Permissao de visualizacao e edicao apenas para drivers
    """
    def has_permission(self, request, view):
        #return True
        return request.user.groups.filter(name='driver').exists() or request.user.is_superuser