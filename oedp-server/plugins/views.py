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
# Create: 2025-02-07
# ======================================================================================================================

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from plugins.models import Plugin
from plugins.serializers import PluginSerializer


class PluginViewSet(viewsets.GenericViewSet):
    queryset = Plugin.objects.all()

    def list(self, request):
        plugins = self.paginate_queryset(self.get_queryset())
        serializer = PluginSerializer(plugins, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request):
        serializer = PluginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'is_success': False,
                'message': "Failed to add a plugin.",
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({
            'is_success': True,
            'message': 'Add a plugin successfully.',
            'data': serializer.data
        })
