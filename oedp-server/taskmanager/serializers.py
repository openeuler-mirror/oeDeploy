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
from taskmanager.models import Task, TaskPlugin, Node, TaskNode
from usermanager.models import User
from utils.cipher import OEDPCipher
from utils.ssh.ssh_connector import SSHConnector, SSHEstablishError, SSHCmdTimeoutError


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
        # 校验任务名称是否重复
        if Task.objects.filter(name=task_name).filter(is_deleted=False).filter(user_id=user_id).exists():
            raise serializers.ValidationError({"name": f"The task name '{task_name}' already exists."})
        return data

    def validate_disclaimer(self, value):
        # 校验免责声明是否同意
        if value is False:
            raise serializers.ValidationError('The disclaimer has not been reviewed.')
        return value

    def validate_plugins(self, value):
        # 校验选择的插件是否存在
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


class NodeSerializer(serializers.Serializer):
    ip = serializers.CharField()
    port = serializers.IntegerField()
    username = serializers.CharField()
    root_password = serializers.CharField()
    password = serializers.CharField()

    def validate_ip(self, value):
        # 校验 IP 是否符合规范
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if not bool(re.match(pattern, value)):
            raise serializers.ValidationError('Invalid IP.')
        return value

    def validate_port(self, value):
        # 校验端口是否符合规范
        if not 0 < value <= 65535:
            raise serializers.ValidationError(f'Invalid port, the valid range for port numbers is 1 to 65535.')
        return value


class TaskNodeSerializer(serializers.ModelSerializer):
    node = serializers.SerializerMethodField()

    class Meta:
        model = TaskNode
        fields = (
            'task_id',
            'node_id',
            'node_name',
            'node_role',
            'node'
        )

    @staticmethod
    def _get_arch_and_os_type(ssh_connector):
        arch = ""
        os_type = ""
        try:
            std, return_code = ssh_connector.execute_cmd("arch")
        except (SSHCmdTimeoutError, ValueError):
            std = ""
            return_code = 1
        if not return_code:
            arch = std.strip()
        try:
            std, return_code = ssh_connector.execute_cmd(
                "cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '\"'")
        except (SSHCmdTimeoutError, ValueError):
            std = ""
            return_code = 1
        if not return_code:
            os_type = std.strip()
        return arch, os_type

    @staticmethod
    def _validate_task(task_id, user):
        # 校验指定 task_id 的任务是否存在
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise serializers.ValidationError({'task_id': f'The task with ID {task_id} does not exist.'})
        # 校验用户是否有有权限操作该任务 (管理员用户和该任务的创建者可以操作)
        if user.role != User.Role.ADMIN and task.user_id != user.id:
            raise serializers.ValidationError(
                {'user': f'The current user does not have permission to operate the task with ID {task_id}.'})

    @staticmethod
    def _validate_node_name(task_id, node_name):
        # 校验指定任务下是否已存在相同的节点名称
        if TaskNode.objects.filter(node_name=node_name).filter(is_deleted=False).filter(task_id=task_id).exists():
            raise serializers.ValidationError({"node_name": f"The node name '{node_name}' already exists."})

    @staticmethod
    def _encrypt(data):
        node = data.get("node")
        # 对密码进行加密
        password_dict = {
            "root_password": node.pop("root_password"),
            "password": node.pop("password")
        }
        oedp_cipher = OEDPCipher()
        node['ciphertext_data'] = oedp_cipher.encrypt_plaintext(password_dict)
        del password_dict
        return data

    @staticmethod
    def _get_ssh_connection(node_dict):
        try:
            ssh_connector = SSHConnector(
                ip=node_dict.get("ip"),
                port=node_dict.get("port"),
                username=node_dict.get("username"),
                ciphertext_data=node_dict.get("ciphertext_data")
            )
        except SSHEstablishError as ex:
            raise serializers.ValidationError(
                {"ssh_connection": [f"Failed to establish SSH connection, Error: {ex}"]}
            )
        return ssh_connector

    def _validate_ssh_connection(self, data):
        node_dict = data.get("node")
        ssh_connector = self._get_ssh_connection(node_dict)
        arch, os_type = self._get_arch_and_os_type(ssh_connector)
        node_dict["arch"] = arch
        node_dict["os_type"] = os_type
        return data

    def get_node(self, obj):
        node = Node.objects.get(id=obj.node_id)
        return {
            "ip": node.ip,
            "port": node.port,
            "username": node.username,
            "arch": node.arch,
            "os_type": node.os_type
        }


class TaskNodeSerializerForCreate(TaskNodeSerializer):
    node = NodeSerializer()

    class Meta:
        model = TaskNode
        fields = (
            'task_id',
            'node_name',
            'node_role',
            'node',
        )

    def validate(self, data):
        task_id = data.get('task_id')
        user = self.context.get('request').user
        node_name = data.get("node_name")

        self._validate_task(task_id, user)
        self._validate_node_name(task_id, node_name)
        data = self._encrypt(data)
        return self._validate_ssh_connection(data)

    def create(self, validated_data):
        node_dict = validated_data.pop("node")
        ip = node_dict.get("ip")
        port = node_dict.get("port")
        username = node_dict.get("username")
        ciphertext_data = node_dict.get("ciphertext_data")
        arch = node_dict.get("arch")
        os_type = node_dict.get("os_type")
        task_id = validated_data.get("task_id")
        node_name = validated_data.get("node_name")
        node_role = validated_data.get("node_role")

        nodes = Node.objects.filter(ip=ip).filter(port=port).filter(username=username)
        if not nodes:
            # 如果节点不存在，则创建节点
            node = Node.objects.create(**node_dict)
        else:
            # 如果节点存在，则判断密码密文，架构和操作系统信息是否不同，如果不同则更新
            node = nodes[0]
            is_save = False
            if node.ciphertext_data != ciphertext_data:
                node.ciphertext_data = ciphertext_data
                is_save = True
            if node.arch != arch:
                node.arch = arch
                is_save = True
            if node.os_type != os_type:
                node.os_type = os_type
                is_save = True
            if is_save:
                node.save()
        task_node = TaskNode.objects.create(task_id=task_id, node_id=node.id, node_name=node_name, node_role=node_role)
        return task_node
