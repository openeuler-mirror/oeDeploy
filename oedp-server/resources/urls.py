#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2025-01-14
# ======================================================================================================================

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from plugins.views import PluginViewSet
from taskmanager.views import TaskViewSet
from usermanager.views import UserViewSet

router = routers.DefaultRouter()
router.register(r'v1.0/tasks', TaskViewSet, basename='tasks')
router.register(r'v1.0/users', UserViewSet, basename='users')
router.register(r'v1.0/plugins', PluginViewSet, basename='plugins')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]
