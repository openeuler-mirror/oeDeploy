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
# Create: 2025-01-24
# ======================================================================================================================
from datetime import datetime

import jwt
import pytz
from django.contrib.auth import get_user_model
from django.utils.encoding import smart_text
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from constants.auth import JWT_AUTH_HEADER_PREFIX
from usermanager.jwt_auth.jwt_manager import JWTManager
from utils.time import get_time_zone


class TokenAuthentication(BaseAuthentication):

    def __init__(self):
        self.user = None
        super().__init__()

    def _get_user(self, user_id):
        user_model = get_user_model()
        try:
            self.user = user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            raise AuthenticationFailed('User not exists.')

    def _get_token(self, request):
        # 从 cookie 中获取 token
        token = request.COOKIES.get('token', '')
        if isinstance(token, str):
            # Work around django test client oddness
            token = token.encode('iso-8859-1')
        auth_header = token.split()
        if not token or smart_text(auth_header[0].lower()) != JWT_AUTH_HEADER_PREFIX.lower():
            return None
        if len(auth_header) != 2:
            raise AuthenticationFailed('Invalid Authorization header.')
        return auth_header[1]

    def _check_token(self, token):
        try:
            payload = JWTManager().decode_token(token)
        # 签名过期
        except jwt.ExpiredSignatureError as error:
            raise AuthenticationFailed('Token has expired.') from error
        # 解码错误
        except jwt.DecodeError as error:
            raise AuthenticationFailed('Decoding token error.') from error
        # 无效token
        except jwt.InvalidTokenError as error:
            raise AuthenticationFailed('Invalid token.') from error
        user_id = payload.get('user_id', None)
        username = payload.get("username", "")
        if not (username and user_id):
            raise AuthenticationFailed('Invalid payload.')
        self._get_user(user_id)

    def _check_csrf_token(self, csrf_token):
        if not self.user.csrf_token:
            raise AuthenticationFailed('User not logged in.')
        if self.user.csrf_token != csrf_token:
            raise AuthenticationFailed('Invalid CSRF token.')
        current_datetime = datetime.now(tz=pytz.timezone(get_time_zone()))
        if current_datetime > self.user.expires_at:
            raise AuthenticationFailed('CSRF token has expired.')

    def authenticate(self, request):
        token = self._get_token(request)
        csrf_token = request.COOKIES.get('csrf_token', '')
        if token is None or csrf_token is None:
            return None
        self._check_token(token)
        self._check_csrf_token(csrf_token)
        return self.user, None

    def authenticate_header(self, request):
        """
        认证 jwt 头部
        """
        return f'{JWT_AUTH_HEADER_PREFIX} realm="api"'
