# -*- coding: utf-8 -*-
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.

import unittest
from unittest.mock import patch, MagicMock
from src.commands.check.check_cmd import CheckCmd


class TestCheckCmd(unittest.TestCase):
    def setUp(self):
        self.project_path = "/fake/project"
        self.action = "install"
    
    def test_init(self):
        """测试CheckCmd初始化"""
        check_cmd = CheckCmd(self.project_path, self.action)
        self.assertEqual(check_cmd.project, self.project_path)
        self.assertEqual(check_cmd.action, self.action)
        self.assertIsNotNone(check_cmd.log)
    
    def test_run(self):
        """测试run方法（当前为空实现）"""
        check_cmd = CheckCmd(self.project_path, self.action)
        result = check_cmd.run()
        # 当前实现为pass，返回None
        self.assertIsNone(result)

