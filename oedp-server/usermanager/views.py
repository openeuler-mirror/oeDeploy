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

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.contrib.auth import authenticate, login, logout

from constants.configs.account_config import ADMIN_ID
from usermanager.jwt_auth.jwt_manager import JWTManager
from usermanager.models import User
from usermanager.serializers import (
    UserSerializer,
    CreateUserSerializer,
    UserSerializerForResetPW,
    UserSerializerForLogin,
)


class UserViewSet(ViewSet):

    def create(self, request):
        """
        创建用户接口
        """
        serializer = CreateUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "is_success": False,
                "message": "Please check input.",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        return Response({
            "is_success": True,
            "message": "Create user successfully.",
            "data": UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)

    @action(methods=['PUT'], detail=False)
    def reset_password(self, request):
        """
        在管理员用户首次登陆前修改密码
        """
        admin = User.objects.get(id=ADMIN_ID)
        serializer = UserSerializerForResetPW(admin, data=request.data, partial=True, context={'request': request.data})
        if not serializer.is_valid():
            return Response({
                "is_success": False,
                "message": "Please check input.",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        return Response({
            "is_success": True,
            "message": "Reset password successfully.",
            "data": UserSerializer(user).data,
            "user": user
        }, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False)
    def login(self, request):
        user = User.objects.get(username=request.data.get('username'))
        serializer = UserSerializerForLogin(user, data=request.data)
        if not serializer.is_valid():
            return Response({
                "is_success": False,
                "message": "Please check input.",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        del password
        if not user or user.is_anonymous:
            return Response({
                "is_success": False,
                "message": "Username and password does not match.",
                "errors": {}
            }, status=400)
        login(request, user)
        response = Response({
            "is_success": True,
            "message": "Login successfully.",
            "data": UserSerializer(user).data,
        }, status=status.HTTP_200_OK)
        jwt_manager = JWTManager()
        token = jwt_manager.generate_token(user)
        csrf_token = jwt_manager.generate_csrf_token()
        response.headers.setdefault('csrf_token', csrf_token)
        response.set_cookie("token", token)
        return response

    @action(methods=['GET'], detail=False)
    def logout(self, request):
        logout(request)
        return Response({
            "is_success": True,
            "message": "Logout successfully.",
            "data": []
        }, status=status.HTTP_200_OK)
