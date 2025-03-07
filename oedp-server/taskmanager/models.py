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

    class DeployType(models.TextChoices):
        NEW_TASK = 'N', 'new_task'
        EXIST_TASK = 'E', 'exist_task'

    class Status(models.IntegerChoices):
        NOT_BEGIN = 0
        IN_PROGRESS = 1
        SUCCESS = 2
        FAIL = 3

    name = models.CharField('任务名称', max_length=64)
    deploy_type = models.CharField('部署类型', max_length=1, choices=DeployType.choices)
    status = models.IntegerField('任务状态', choices=Status.choices)
    start_time = models.DateTimeField('任务开始时间', blank=True, null=True)
    end_time = models.DateTimeField('任务结束时间', blank=True, null=True)
    user_id = models.IntegerField('用户 id')
    is_deleted = models.BooleanField('任务是否被删除', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.name


class TaskPlugin(models.Model):
    task_id = models.IntegerField('任务 ID')
    plugin_id = models.IntegerField('插件 ID')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)


class Step(models.Model):
    name = models.CharField('阶段名称', max_length=32)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)


class TaskProcess(models.Model):

    class Status(models.IntegerChoices):
        NOT_BEGIN = 0
        IN_PROGRESS = 1
        SUCCESS = 2
        FAIL = 3

    task_id = models.IntegerField('任务 ID')
    step_id = models.IntegerField('阶段 ID')
    step_status = models.IntegerField('阶段状态', choices=Status.choices)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)


class Node(models.Model):
    name = models.CharField('节点名称', max_length=32)
    ip = models.CharField('IP 地址', max_length=18)
    port = models.IntegerField('端口')
    username = models.CharField('用户名', max_length=128)
    ciphertext_data = models.CharField('密码密文数据', max_length=512)
    role = models.CharField('节点角色', max_length=32)
    arch = models.CharField('节点架构', max_length=32)
    os_type = models.CharField('操作系统', max_length=64)
    task_id = models.IntegerField('任务 id')
    is_deleted = models.BooleanField('节点是否被删除', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return f"{self.ip}:{self.port}"
