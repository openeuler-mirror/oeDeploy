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

from rest_framework import viewsets
from rest_framework.response import Response

from taskmanager.models import Task
from taskmanager.serializers import TaskSerializer, TaskSerializerForDetail


class TaskViewSet(viewsets.GenericViewSet):
    queryset = Task.objects.all()

    def list(self, request):
        tasks = self.paginate_queryset(self.get_queryset())
        serializer = TaskSerializer(
            tasks,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        return Response(TaskSerializerForDetail(
            self.get_object(),
            context={'request': request},
        ).data)
