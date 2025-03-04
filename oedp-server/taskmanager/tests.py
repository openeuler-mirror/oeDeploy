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

from unittest.mock import patch

from rest_framework.test import APIClient

from plugins.models import Plugin
from taskmanager.models import Task, TaskPlugin, Node
from utils.test.testcases import CustomTestCase


class TaskTestCase(CustomTestCase):
    TASK_URL = "/v1.0/tasks/"
    NODE_URL = "/v1.0/nodes/"

    def _create_a_task(self, name, user_id, task_status=None):
        if task_status is None:
            task_status = Task.Status.NOT_BEGIN
        return Task.objects.create(name=name, status=task_status, user_id=user_id)

    def _create_a_plugin(self, name):
        return Plugin.objects.create(name=name)

    def _create_a_node(
        self,
        name,
        task_id,
        ip="192.168.122.1",
        port=22,
        role="master",
        username="root",
        ciphertext_data=None
    ):
        if ciphertext_data is None:
            ciphertext_data = "{'half_key': '', 'encrypted_work_key': '', 'work_key_iv': '', " \
                              "'ciphertext': '', 'plaintext_iv': ''}"
        return Node.objects.create(name=name, task_id=task_id, ip=ip, port=port, role=role, username=username,
                                   ciphertext_data=ciphertext_data)

    def _create_a_task_plugin_entry(self, task_id, plugin_id):
        return TaskPlugin.objects.create(task_id=task_id, plugin_id=plugin_id)

    def _create_tasks(self, task_num, task_name_prefix, user_id, task_status=None):
        if task_status is None:
            task_status = Task.Status.NOT_BEGIN
        for num in range(task_num):
            Task.objects.create(name=f'{task_name_prefix}-{num}', status=task_status, user_id=user_id)

    def setUp(self):
        # 创建管理源用户
        self.admin = self.create_user("admin")
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(self.admin)

    def test_task_creation_when_anonymous(self):
        """
        测试匿名状态下创建任务
        期望结果：
            - HTTP 状态码 401
        """
        response = self.anonymous_client.post(self.TASK_URL)
        self.assertEqual(response.status_code, 401)

    def test_task_creation_without_params(self):
        """
        测试登录状态但是未输入任何内容的情况下创建任务
        期望结果：
            - HTTP 状态码 400
            - except_data
        """
        except_data = {
            "is_success": False,
            "message": "Please check input.",
            "errors": {
                "name": [
                    "This field is required."
                ],
                "deploy_type": [
                    "This field is required."
                ],
                "disclaimer": [
                    "The disclaimer has not been reviewed."
                ],
                "plugins": [
                    "This field is required."
                ]
            }
        }

        response = self.admin_client.post(self.TASK_URL)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, except_data)

    def test_task_creation_with_duplicate_name(self):
        """
        测试使用重复的任务名称创建任务
        期望结果：
            - HTTP 状态码 400
            - except_data
        """
        task_name = "Task-01"
        user_id = self.admin.id
        plugin_name = "K8S"
        task = self._create_a_task(task_name, user_id)
        plugin = self._create_a_plugin(plugin_name)
        self._create_a_task_plugin_entry(task.id, plugin.id)
        request_data = {
            "name": task_name,
            "plugins": [
                {
                    "id": plugin.id
                }
            ],
            "disclaimer": True,
            "deploy_type": "N"
        }
        except_data = {
            "is_success": False,
            "message": "Please check input.",
            "errors": {
                "name": [
                    f"The task name '{task_name}' already exists."
                ]
            }
        }
        response = self.admin_client.post(self.TASK_URL, request_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, except_data)

    def test_task_creation_with_invalid_deploy_type(self):
        """
        测试使用无效的 deploy_type 参数创建任务。deploy_type 可选值为 'N' 和 'E'，用例中使用 'X'
        期望结果：
            - HTTP 状态码 400
            - except_data
        """
        plugin = self._create_a_plugin("kubeflow")
        request_data = {
            "name": "Task-02",
            "plugins": [
                {
                    "id": plugin.id
                }
            ],
            "disclaimer": True,
            "deploy_type": "X"
        }
        except_data = {
            "is_success": False,
            "message": "Please check input.",
            "errors": {
                "deploy_type": [
                    "\"X\" is not a valid choice."
                ]
            }
        }
        response = self.admin_client.post(self.TASK_URL, request_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, except_data)

    def test_task_creation_with_invalid_plugins(self):
        """
        测试使用无效的 plugins 参数创建任务。plugins 的值的类型为列表，用例中为字典
        期望结果：
            - HTTP 状态码 400
            - except_data:
        """
        request_data = {
            "name": "Task-03",
            "plugins": {
                "id": 3
            },
            "disclaimer": True,
            "deploy_type": "N"
        }
        except_data = {
            "is_success": False,
            "message": "Please check input.",
            "errors": {
                "plugins": {
                    "non_field_errors": [
                        "Expected a list of items but got type \"dict\"."
                    ]
                }
            }
        }
        response = self.admin_client.post(self.TASK_URL, request_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, except_data)

    def test_task_creation_with_not_exist_plugins(self):
        """
        测试使用不存在的插件 ID 创建任务
        期望结果：
            - HTTP 状态码 400
            - except_data:
        """
        request_data = {
            "name": "Task-04",
            "plugins": [
                {
                    "id": 100
                }
            ],
            "disclaimer": True,
            "deploy_type": "N"
        }
        except_data = {
            "is_success": False,
            "message": "Please check input.",
            "errors": {
                "plugins": [
                    "Plugin with ID 100 does not exist."
                ]
            }
        }
        response = self.admin_client.post(self.TASK_URL, request_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, except_data)

    def test_task_creation_without_plugin_id(self):
        """
        测试不传 plugins 的 id 时创建任务
        期望结果：
            - HTTP 状态码 400
            - except_data:
        """
        request_data = {
            "name": "Task-05",
            "plugins": [
                {
                    "idx": 1
                }
            ],
            "disclaimer": True,
            "deploy_type": "N"
        }
        except_data = {
            "is_success": False,
            "message": "Please check input.",
            "errors": {
                "plugins": [
                    {
                        "id": [
                            "This field is required."
                        ]
                    }
                ]
            }
        }
        response = self.admin_client.post(self.TASK_URL, request_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, except_data)

    def test_task_creation_with_wrong_type_plugin_id(self):
        """
        测试传不为整数类型的 plugins 的 id 时创建任务
        期望结果：
            - HTTP 状态码 400
            - except_data:
        """
        request_data = {
            "name": "Task-06",
            "plugins": [
                {
                    "id": "a"
                }
            ],
            "disclaimer": True,
            "deploy_type": "N"
        }
        except_data = {
            "is_success": False,
            "message": "Please check input.",
            "errors": {
                "plugins": [
                    {
                        "id": [
                            "A valid integer is required."
                        ]
                    }
                ]
            }
        }
        response = self.admin_client.post(self.TASK_URL, request_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, except_data)

    def test_task_creation_success(self):
        """
        测试成功创建任务
        期望结果：
            - HTTP 状态码 201
            - except_data:
        """
        deepseek = self._create_a_plugin("deepseek")
        pytorch = self._create_a_plugin("pytorch")
        request_data = {
            "name": "Task-06",
            "plugins": [
                {
                    "id": deepseek.id
                },
                {
                    "id": pytorch.id
                }
            ],
            "disclaimer": True,
            "deploy_type": "N"
        }
        except_data = {
            "is_success": True,
            "message": "Create task successfully.",
            "data": {
                "id": 1,
                "name": "Task-06",
                "plugins": [
                    {
                        "id": deepseek.id,
                        "name": "deepseek"
                    },
                    {
                        "id": pytorch.id,
                        "name": "pytorch"
                    }
                ]
            }
        }
        response = self.admin_client.post(self.TASK_URL, request_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, except_data)

    def test_task_list_when_anonymous(self):
        """
        测试匿名状态下获取任务列表
        期望结果：
            - HTTP 状态码 401
        """
        response = self.anonymous_client.get(self.TASK_URL)
        self.assertEqual(response.status_code, 401)

    def test_task_list_with_paginate(self):
        """
        测试使用不同的分页参数获取任务列表
        """
        # 创建 25 条 admin 用户的任务记录，再创建 10 条其他用户的任务记录
        self._create_tasks(25, "Task", self.admin.id)
        self._create_tasks(10, "Task_another_user", 2)

        # 测试不传递分页参数，默认获取第 1 页的 10 条记录，期望结果：获取到 10 条记录
        response = self.admin_client.get(self.TASK_URL, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('data').get('results')), 10)

        # 测试获取第 3 页的 10 条记录，期望结果：获取到 5 条记录
        response = self.admin_client.get(f"{self.TASK_URL}?cur_page=3&page_size=10", format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('data').get('results')), 5)

        # 测试获取第 1 页的 20 条记录，期望结果：获取到 20 条记录
        response = self.admin_client.get(f"{self.TASK_URL}?page_size=20", format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('data').get('results')), 20)

        # 测试获取第 1 页的 50 条记录，期望结果：获取到 25 条记录
        response = self.admin_client.get(f"{self.TASK_URL}?page_size=50", format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('data').get('results')), 25)

        # 测试获取第 2 页的 50 条记录，期望结果：返回 404
        response = self.admin_client.get(f"{self.TASK_URL}?cur_page=2&page_size=50", format='json')
        self.assertEqual(response.status_code, 404)

    def test_task_list_with_filter(self):
        """
        测试传不同的筛选参数时获取任务列表
        """
        # 创建不同任务名称和状态的任务记录
        self._create_tasks(6, "K8S_Task", self.admin.id)
        self._create_tasks(2, "K8S_x_Task", self.admin.id, task_status=Task.Status.IN_PROGRESS)
        self._create_tasks(8, 'DeepSeek_Task', self.admin.id, task_status=Task.Status.IN_PROGRESS)
        self._create_tasks(2, "DeepSeek_R1_Task", self.admin.id, task_status=Task.Status.SUCCESS)

        # 测试查找任务名称中包含 'K8S' 的任务记录，期望结果：获取到 8 条记录
        response = self.admin_client.get(f"{self.TASK_URL}?name=K8S")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('data').get('results')), 8)

        # 测试查找任务状态为'执行中'的任务记录，期望结果：获取到 10 条记录
        response = self.admin_client.get(f"{self.TASK_URL}?status={Task.Status.IN_PROGRESS}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('data').get('results')), 10)

        # 测试查找任务状态为'执行成功'且名字中包含 'Deep' 的任务记录，期望结果：获取到 2 条记录
        response = self.admin_client.get(f"{self.TASK_URL}?status={Task.Status.SUCCESS}&name=Deep")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('data').get('results')), 2)

        # 查找名字中包含 'task' (忽略大小写) 且单页显示 20 条记录，期望结果：获取到 18 条
        response = self.admin_client.get(f"{self.TASK_URL}?name=task&page_size=20")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('data').get('results')), 18)

        # 查找名字中包含 'task' (忽略大小写) 且单页默认显示 10 条记录，期望结果：获取到 10 条
        response = self.admin_client.get(f"{self.TASK_URL}?name=task")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('data').get('results')), 10)

    def test_task_deletion_when_anonymous(self):
        """
        测试匿名状态下删除任务
        期望结果：
            - HTTP 状态码 401
        """
        response = self.anonymous_client.delete(f'{self.TASK_URL}1/')
        self.assertEqual(response.status_code, 401)

    def test_task_deletion(self):
        """
        测试正常删除任务
        期望结果：
            - HTTP 状态码 200
            - 对应记录的 is_deleted 字段已经被置为 True
        """
        task = self._create_a_task('Task-01', self.admin.id)
        response = self.admin_client.delete(f'{self.TASK_URL}{task.id}/')
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.is_deleted, True)

    def test_node_creation_when_anonymous(self):
        """
        测试匿名状态下添加节点
        期望结果：
            - HTTP 状态码 401
        """
        response = self.anonymous_client.post(self.NODE_URL)
        self.assertEqual(response.status_code, 401)

    def test_node_creation_without_params(self):
        """
        测试登录状态但是未输入任何内容的情况下添加节点
        期望结果：
            - HTTP 状态码 400
            - except_data
        """
        except_data = {
            "is_success": False,
            "message": "Please check input.",
            "errors": {
                "name": [
                    "This field is required."
                ],
                "task_id": [
                    "This field is required."
                ],
                "ip": [
                    "This field is required."
                ],
                "port": [
                    "This field is required."
                ],
                "role": [
                    "This field is required."
                ],
                "username": [
                    "This field is required."
                ],
                "root_password": [
                    "This field is required."
                ],
                "password": [
                    "This field is required."
                ]
            }
        }

        response = self.admin_client.post(self.NODE_URL)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, except_data)

    def test_node_creation_with_duplicate_name(self):
        """
        测试添加节点使用重复的名称
        期望结果：
            - HTTP 状态码 400
            - except_data
        """
        task = self._create_a_task("Task-01", self.admin.id)
        self._create_a_node("Node-01", task.id)
        request_data = {
            "name": "Node-01",
            "task_id": task.id,
            "ip": "192.168.122.6",
            "port": 22,
            "role": "master",
            "username": "root",
            "root_password": "Test12#$",
            "password": "Test12#$"
        }
        except_data = {
            "is_success": False,
            "message": "Please check input.",
            "errors": {
                "name": [
                    "The node name 'Node-01' already exists."
                ]
            }
        }

        response = self.admin_client.post(self.NODE_URL, request_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, except_data)

    def test_node_creation_with_not_exists_task_id(self):
        """
        测试添加节点使用不存在的任务 ID
        期望结果：
            - HTTP 状态码 400
            - except_data
        """
        request_data = {
            "name": "Node-01",
            "task_id": 1,
            "ip": "192.168.122.6",
            "port": 22,
            "role": "master",
            "username": "root",
            "root_password": "Test12#$",
            "password": "Test12#$"
        }
        except_data = {
            "is_success": False,
            "message": "Please check input.",
            "errors": {
                "task_id": [
                    "The task with ID 1 does not exist."
                ]
            }
        }

        response = self.admin_client.post(self.NODE_URL, request_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, except_data)
