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
# Create: 2025-01-21
# ======================================================================================================================

from django.apps import apps
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db import models

from utils.cipher import get_salt


class CustomUserManager(BaseUserManager):

    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.password = make_password(password, salt=get_salt())
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault("has_reset", False)
        return self._create_user(username, password, **extra_fields)


class User(AbstractBaseUser):

    class RoleChoices(models.IntegerChoices):
        ADMIN = 0
        USER = 1
        GUEST = 2

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['role']

    username = models.CharField('用户名', max_length=32, unique=True)
    password = models.CharField('用户密码', max_length=32, blank=True, null=True)
    role = models.IntegerField('用户角色', choices=RoleChoices.choices)
    has_reset = models.BooleanField('用户是否重设密码', default=False, blank=True, null=True)
    last_login = models.DateTimeField('上次登陆时间', blank=True, null=True)

    csrf_token = models.CharField('CSRF token', max_length=255, blank=True, null=True)
    expires_at = models.DateTimeField('CSRF token 失效时间', blank=True, null=True)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def set_password(self, new_password):
        """
        设置密码，使用自定义方法生成的盐值
        """
        # 长度为18的字节数组base64后会转成长度为24的字符串
        self.password = make_password(new_password, salt=get_salt())
        self._password = new_password
