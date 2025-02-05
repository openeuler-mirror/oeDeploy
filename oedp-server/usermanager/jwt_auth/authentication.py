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

import jwt
from django.utils.encoding import smart_text
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from constants.auth import JWT_AUTH_HEADER_PREFIX
from usermanager.jwt_auth.jwt_manager import JWTManager


class JSONWebTokenAuthentication(BaseAuthentication):

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
            raise exceptions.AuthenticationFailed('Invalid Authorization header.')
        return auth_header[1]

    def authenticate(self, request):
        token = self._get_token(request)
        # 解码 token
        try:
            payload = JWTManager().decode_token(token)
        # 签名过期
        except jwt.ExpiredSignatureError as error:
            raise exceptions.AuthenticationFailed('Signature has expired.') from error
        # 解码错误
        except jwt.DecodeError as error:
            raise exceptions.AuthenticationFailed('Decoding signature error.') from error
        # 无效token
        except jwt.InvalidTokenError as error:
            raise exceptions.AuthenticationFailed() from error
