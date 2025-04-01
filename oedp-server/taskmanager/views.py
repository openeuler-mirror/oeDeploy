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

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from taskmanager.models import Task
from taskmanager.serializers import (
    TaskSerializer,
    TaskSerializerForCreate,
    TaskNodeSerializerForCreate,
    TaskNodeSerializer
)
from utils.logger import init_log
from utils.ssh.ssh_connector import SSHConnector, SSHEstablishError, SSHCmdTimeoutError

run_logger = init_log("run.log")


class TaskViewSet(viewsets.GenericViewSet):
    queryset = Task.objects.all()

    @staticmethod
    def _filter_tasks(request, task_queryset):
        name = request.query_params.get("name")
        task_status = request.query_params.get("status")
        if name:
            task_queryset = task_queryset.filter(name__icontains=name)
        if task_status:
            task_queryset = task_queryset.filter(status=task_status)
        return task_queryset

    def list(self, request):
        task_queryset = Task.objects.filter(is_deleted=False).filter(user_id=request.user.id)
        tasks = self.paginate_queryset(self._filter_tasks(request, task_queryset))
        serializer = TaskSerializer(
            tasks,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)

    def create(self, request):
        serializer = TaskSerializerForCreate(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response({
                'is_success': False,
                'message': 'Please check input.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        task = serializer.save()
        return Response({
            'is_success': True,
            'message': 'Create task successfully.',
            'data': TaskSerializer(task).data
        }, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk):
        task = Task.objects.get(id=pk)
        task.is_deleted = True
        task.save()
        return Response({
            'is_success': True,
            'message': 'Delete task successfully.',
            'data': TaskSerializer(task).data
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def add_node(self, request):
        serializer = TaskNodeSerializerForCreate(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({
                'is_success': False,
                'message': 'Please check input.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        task_node_entry = serializer.save()
        data = TaskNodeSerializer(task_node_entry).data
        return Response({
            'is_success': True,
            'message': 'Add a node successfully.',
            'data': data
        }, status=status.HTTP_201_CREATED)
