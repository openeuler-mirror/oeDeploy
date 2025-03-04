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
import re

from django.db import transaction
from rest_framework import serializers

from plugins.models import Plugin
from plugins.serializers import PluginIDSerializer
from taskmanager.models import Task, TaskPlugin, Node
from usermanager.models import User
from utils.cipher import OEDPCipher


class TaskSerializer(serializers.ModelSerializer):
    plugins = serializers.SerializerMethodField()

    def get_plugins(self, obj):
        plugin_ids = [entry.plugin_id for entry in TaskPlugin.objects.filter(task_id=obj.id)]
        plugin_info = []
        for plugin_id in plugin_ids:
            plugin = Plugin.objects.get(pk=plugin_id)
            plugin_info.append({'id': plugin.id, 'name': plugin.name})
        return plugin_info

    class Meta:
        model = Task
        fields = (
            'id',
            'name',
            'plugins',
        )


class TaskSerializerForCreate(serializers.ModelSerializer):
    disclaimer = serializers.BooleanField(default=False)
    plugins = PluginIDSerializer(many=True)

    class Meta:
        model = Task
        fields = (
            'name',
            'deploy_type',
            'disclaimer',
            'plugins',
        )

    def validate(self, data):
        task_name = data.get("name")
        user_id = self.context.get("request").user.id
        if Task.objects.filter(name=task_name).filter(is_deleted=False).filter(user_id=user_id).exists():
            raise serializers.ValidationError({"name": f"The task name '{task_name}' already exists."})
        return data

    def validate_disclaimer(self, value):
        if value is False:
            raise serializers.ValidationError('The disclaimer has not been reviewed.')
        return value

    def validate_plugins(self, value):
        for plugin in value:
            plugin_id = plugin.get("id")
            if not Plugin.objects.filter(id=plugin_id).exists():
                raise serializers.ValidationError(f'Plugin with ID {plugin_id} does not exist.')
        return value

    def create(self, validated_data):
        plugin_data = validated_data.pop('plugins')
        with transaction.atomic():
            task = Task.objects.create(
                name=validated_data.get('name'),
                deploy_type=validated_data.get('deploy_type'),
                status=Task.Status.NOT_BEGIN,
                user_id=self.context.get("request").user.id
            )
            task_plugin_entries = [TaskPlugin(task_id=task.id, plugin_id=plugin.get('id')) for plugin in plugin_data]
            TaskPlugin.objects.bulk_create(task_plugin_entries)
        return task


class NodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Node
        fields = (
            'id',
            'name',
            'ip',
            'port',
            'role',
            'arch',
            'os_type',
        )


class NodeSerializerForCreate(serializers.ModelSerializer):
    root_password = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = Node
        fields = (
            'name',
            'task_id',
            'ip',
            'port',
            'role',
            'username',
            'root_password',
            'password',
        )

    def validate(self, data):
        node_name = data.get("name")
        task_id = data.get('task_id')
        user = self.context.get('request').user
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise serializers.ValidationError({'task_id': f'The task with ID {task_id} does not exist.'})
        if user.role != User.Role.ADMIN and task.user_id != user.id:
            raise serializers.ValidationError(
                f'The current user does not have permission to operate the task with ID {task_id}.')
        if Node.objects.filter(name=node_name).filter(is_deleted=False).filter(task_id=task_id).exists():
            raise serializers.ValidationError({"name": f"The node name '{node_name}' already exists."})
        if data.get("root_password") and data.get("password"):
            password_dict = {
                "root_password": data.pop("root_password"),
                "password": data.pop("password")
            }
            oedp_cipher = OEDPCipher()
            data['ciphertext_data'] = oedp_cipher.encrypt_plaintext(password_dict)
        return data

    def validate_ip(self, value):
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if not bool(re.match(pattern, value)):
            raise serializers.ValidationError('Invalid IP.')
        return value

    def validate_port(self, value):
        if not 0 < value <= 65535:
            raise serializers.ValidationError(f'Invalid port, the valid range for port numbers is 1 to 65535.')
        return value

    def create(self, validated_data):
        node = Node.objects.create(**validated_data)
        return node
