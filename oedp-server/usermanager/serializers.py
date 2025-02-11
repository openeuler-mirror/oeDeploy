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

import re
from datetime import datetime, timedelta

from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from constants.auth import JWT_EXPIRY_DAYS
from constants.configs.account_config import ADMIN_ID, USERNAME_MIN_LEN, USERNAME_MAX_LEN
from usermanager.models import User
from utils.cipher import get_salt


def validate_password_valid(value):
    """
    校验器函数，检查密码的合法性，密码需要包括大小写字母、数字和特殊字符中的两种以上，且长度为 8-32 位
    """
    regex = r"^(?![A-Z]+$)(?![a-z]+$)(?![0-9]+$)" \
            r"(?![`~!@#$%^&*()\-_=+\\|[{}\];:'\",<.>/?]+$)" \
            r"[A-Za-z0-9`~!@#$%^&*()\-_=+\\|[{}\];:'\",<.>/?]{8,32}$"
    match = re.match(regex, value)
    if not match:
        del value, match
        raise serializers.ValidationError('The password is invalid.')
    del value, match


def confirm_password(data):
    """
    确认两次输入的密码是否匹配
    """
    password = data.get('password')
    confirmed_password = data.get('confirmed_password')
    if password != confirmed_password:
        del password, confirmed_password
        raise serializers.ValidationError({'confirmed_password': 'The passwords do not match.'})
    del password, confirmed_password


def check_username_as_password(data):
    """
    检查是否把用户名作为密码
    """
    username = data.get('username')
    password = data.get('password')
    if password == username or password == username[::-1]:
        del password
        raise serializers.ValidationError({'password': 'The username cannot be used as the password.'})
    del password


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'role',
        )


class UserSerializerForCreate(serializers.ModelSerializer):
    password = serializers.CharField(max_length=32, min_length=8, validators=[validate_password_valid])
    confirmed_password = serializers.CharField(max_length=32, min_length=8)

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'confirmed_password',
            'role',
        )

    @staticmethod
    def _check_username_valid(username):
        """
        检查用户名的合法性，用户名需以字母开头的，可以包含字母、数字或特殊字符（-_)，且长度为 6-32 位
        """
        regex = "^[a-zA-Z][a-zA-Z0-9_-]{5,31}$"
        match = re.match(regex, username)
        if match:
            return True
        return False

    def validate(self, data):
        # 校验两次输入的密码是否相等
        confirm_password(data)
        # 校验是否把用户名作为密码
        check_username_as_password(data)
        # TODO 校验密码是否为已配置的弱密码
        return data

    def validate_username(self, value):
        if not self._check_username_valid(value):
            raise serializers.ValidationError('The username is invalid.')
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(f'The username "${value}" already exists.')
        return value

    @staticmethod
    def validate_role(value):
        if value is None or value not in (User.RoleChoices.USER, User.RoleChoices.GUEST):
            raise serializers.ValidationError('The role is invalid.')
        return value

    def create(self, validated_data):
        username = validated_data.get('username', '')
        password = validated_data.get('password', '')
        return User.objects.create_user(username, password, **validated_data)


class UserSerializerForResetPW(serializers.ModelSerializer):
    password = serializers.CharField(max_length=32, min_length=8, validators=[validate_password_valid])
    confirmed_password = serializers.CharField(max_length=32, min_length=8)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'confirmed_password',
        )

    def validate(self, data):
        # 校验用户 id 是否和管理员 id 相同。
        if int(data.get('id')[0]) != ADMIN_ID:
            raise serializers.ValidationError({'id': 'This id is not the id of the administrator user.'})
        # 判断用户是否存在
        if not User.objects.filter(id=ADMIN_ID).exists():
            raise serializers.ValidationError({'id', 'The user whose id is 1 not exists.'})
        # 判断用户是否是管理员
        if User.objects.get(id=ADMIN_ID).role != User.RoleChoices.ADMIN:
            raise serializers.ValidationError('The role of user is not administrator.')
        # 判断是否重置过密码
        if User.objects.get(id=ADMIN_ID).has_reset:
            raise serializers.ValidationError('The Admin user has reset password.')
        # 校验两次输入的密码是否相等
        confirm_password(data)
        # 校验是否把用户名作为密码
        check_username_as_password(data)
        return data

    def update(self, instance, validated_data):
        instance.password = make_password(validated_data['password'], salt=get_salt())
        instance.has_reset = True
        instance.save()
        return instance


class UserSerializerForLogin(serializers.ModelSerializer):
    disclaimer = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'disclaimer'
        )

    def validate_disclaimer(self, value):
        if value is False:
            raise serializers.ValidationError('The disclaimer has not been reviewed.')
        return value

    def validate_username(self, value):
        if not USERNAME_MIN_LEN <= len(value) <= USERNAME_MAX_LEN:
            raise serializers.ValidationError(f'The username must be between {USERNAME_MIN_LEN} and {USERNAME_MAX_LEN} '
                                              'characters in length.')
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError(f'The user {value} not exists.')
        return value

    def validate(self, data):
        user = User.objects.get(username=data.get('username'))
        if user.has_reset is False and user.id == ADMIN_ID:
            raise serializers.ValidationError('Admin user needs to reset password before login.')
        return data

    def update(self, instance, validated_data):
        instance.csrf_token = validated_data.get('csrf_token')
        instance.expires_at = datetime.now() + timedelta(days=JWT_EXPIRY_DAYS)
        instance.last_login = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        instance.save()
        return instance
