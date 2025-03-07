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

from rest_framework import serializers

from plugins.models import Plugin


class PluginSerializer(serializers.ModelSerializer):

    class Meta:
        model = Plugin
        fields = (
            'id',
            'name',
            'version',
            'description',
        )

    def create(self, validated_data):
        return Plugin.objects.create(**validated_data)


class PluginIDSerializer(serializers.Serializer):
    id = serializers.IntegerField()
