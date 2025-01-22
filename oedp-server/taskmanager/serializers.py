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

from rest_framework import serializers

from taskmanager.models import Task, Plugin, TaskPlugin


class TaskSerializer(serializers.ModelSerializer):
    plugins = serializers.SerializerMethodField()

    def get_plugins(self, obj):
        plugin_ids = [entry.plugin_id for entry in TaskPlugin.objects.filter(task_id=obj.id)]
        plugin_names = [Plugin.objects.get(pk=plugin_id).name for plugin_id in plugin_ids]
        return plugin_names

    class Meta:
        model = Task
        fields = (
            'name',
            'plugins',
        )


class TaskSerializerForDetail(TaskSerializer):

    class Meta:
        model = Task
        fields = (
            'name',
        )
