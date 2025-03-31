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
    NodeSerializerForCreate,
    NodeSerializer
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

    @staticmethod
    def _get_ssh_connector(validated_data):
        try:
            ssh_connector = SSHConnector(
                ip=validated_data.get("ip"),
                port=validated_data.get("port"),
                username=validated_data.get("username"),
                ciphertext_data=validated_data.get("ciphertext_data")
            )
        except SSHEstablishError:
            return None
        return ssh_connector

    @staticmethod
    def _get_arch_and_os_type(ssh_connector):
        arch = ""
        os_type = ""
        try:
            std, return_code = ssh_connector.execute_cmd("arch")
        except (SSHCmdTimeoutError, ValueError):
            run_logger.warning("Failed to get node arch")
            std = ""
            return_code = 1
        if not return_code:
            arch = std.strip()
        try:
            std, return_code = ssh_connector.execute_cmd(
                "cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '\"'")
        except (SSHCmdTimeoutError, ValueError):
            run_logger.warning("Failed to get node OS type")
            std = ""
            return_code = 1
        if not return_code:
            os_type = std.strip()
        return arch, os_type

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
        serializer = NodeSerializerForCreate(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({
                'is_success': False,
                'message': 'Please check input.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        ssh_connector = self._get_ssh_connector(serializer.validated_data)
        if ssh_connector:
            arch, os_type = self._get_arch_and_os_type(ssh_connector)
            node = serializer.save(arch=arch, os_type=os_type)
        else:
            node = serializer.save()
        data = NodeSerializer(node).data
        data['name'] = serializer.validated_data.get('name')
        data['role'] = serializer.validated_data.get('role')
        if not ssh_connector:
            return Response({
                'is_success': False,
                'message': 'Please check input.',
                'data': data,
                'errors': {"non_field_errors": ["Failed to establish SSH connection."]}
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'is_success': True,
            'message': 'Add node successfully.',
            'data': data
        }, status=status.HTTP_201_CREATED)
