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
# Create: 2025-01-23
# ======================================================================================================================

import uuid
from datetime import datetime, timedelta

import jwt
import pytz
from django.contrib.auth import get_user_model
from jwt.utils import base64url_encode

from constants.auth import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRY_DAYS
from utils.cipher import generate_random_bytes
from utils.time import get_time_zone


class JWTManager:

    @staticmethod
    def _get_username(user):
        """
        获取用户名
        """
        try:
            username = user.get_username()
        except AttributeError:
            username = user.username
        return username

    def _generate_payload(self, user):
        """
        生成 payload
        """
        username_field = get_user_model().USERNAME_FIELD
        username = self._get_username(user)
        expiration_time = datetime.now(tz=pytz.timezone(get_time_zone())) + timedelta(days=JWT_EXPIRY_DAYS)
        return {'user_id': user.pk, username_field: username, 'exp': expiration_time}

    def decode_token(self, token):
        options = {'verify_exp': False}
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options=options,
            audience=None,
            leeway=0,
            issuer=None,
        )
        return payload

    def generate_token(self, user):
        """
        生成 token
        """
        payload = self._generate_payload(user)
        token = "JWT {}".format(jwt.encode(payload, JWT_SECRET_KEY, JWT_ALGORITHM))
        return token

    @staticmethod
    def generate_csrf_token():
        """
        生成 csrf-token
        """
        csrf_token = base64url_encode(generate_random_bytes(32))
        return csrf_token