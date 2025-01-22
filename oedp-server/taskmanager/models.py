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

from django.db import models


class Task(models.Model):

    class DeployTypeChoices(models.TextChoices):
        NEW_TASK = 'N', 'new_task'
        EXIST_TASK = 'E', 'exist_task'

    class StatusChoices(models.IntegerChoices):
        NOT_BEGIN = 0
        IN_PROGRESS = 1
        SUCCESS = 2
        FAIL = 3

    name = models.CharField('任务名称', max_length=32)
    deploy_type = models.CharField('部署类型', max_length=1, choices=DeployTypeChoices.choices)
    status = models.IntegerField('任务状态', choices=StatusChoices.choices)
    start_time = models.DateTimeField('任务开始时间', blank=True, null=True)
    end_time = models.DateTimeField('任务结束时间', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    modified_at = models.DateTimeField('修改时间', auto_now=True)


class Plugin(models.Model):
    name = models.CharField('插件名称', max_length=32)
    version = models.CharField('插件版本', max_length=32)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    modified_at = models.DateTimeField('修改时间', auto_now=True)


class TaskPlugin(models.Model):
    task_id = models.IntegerField('任务 ID')
    plugin_id = models.IntegerField('插件 ID')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    modified_at = models.DateTimeField('修改时间', auto_now=True)


class Step(models.Model):
    name = models.CharField('阶段名称', max_length=32)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    modified_at = models.DateTimeField('修改时间', auto_now=True)


class TaskProcess(models.Model):

    class StatusChoices(models.IntegerChoices):
        NOT_BEGIN = 0
        IN_PROGRESS = 1
        SUCCESS = 2
        FAIL = 3

    task_id = models.IntegerField('任务 ID')
    step_id = models.IntegerField('阶段 ID')
    step_status = models.IntegerField('阶段状态', choices=StatusChoices.choices)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    modified_at = models.DateTimeField('修改时间', auto_now=True)


class Node(models.Model):
    name = models.CharField('节点名称', max_length=32)
    ip = models.CharField('IP 地址', max_length=18)
    port = models.CharField('端口', max_length=18)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    modified_at = models.DateTimeField('修改时间', auto_now=True)
