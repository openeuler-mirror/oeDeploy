# -*- coding: utf-8 -*-
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# oeDeploy is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2024-12-23
# ======================================================================================================================

import argparse
import os
import re

from src.commands.check.check_cmd import CheckCmd
from src.commands.info.info_cmd import InfoCmd
from src.commands.init.init_cmd import InitCmd
from src.commands.list.list_cmd import ListCmd
from src.commands.run.run_cmd import RunCmd
from src.commands.repo.repo_cmd import RepoCmd
from src.constants.const import VERSION
from src.constants.paths import PLUGIN_DIR

from src.utils.command.command_executor import CommandExecutor


class OeDeployParser:
    """
    命令行参数解析器
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog='oedp',
            usage='%(prog)s <command> [<args>]',
            description='oeDeploy tool for openEuler.',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        self.parser.add_argument('-v', '--version', action='version', version=f'oedp {self._get_version()}')
        self.subparsers = self.parser.add_subparsers(
            dest='command',
            title='Available commands',
            required=True,
            metavar='<command>'
        )
        self._add_init_command()
        self._add_list_command()
        self._add_info_command()
        self._add_run_command()
        self._add_check_command()
        self._add_repo_command()

    def execute(self):
        """
        解析命令行参数，并执行对应子命令。

        不需要处理异常，参数错误由 argparse 处理。

        :return: 子命令执行结果
        """
        args = self.parser.parse_args()
        ret = args.func(args)
        return ret

    def _add_init_command(self):
        """
        oedp init <plugin> -p|--project <path> [-l|--local <path>] [-f|--force]

        在指定的目录下初始化一个项目。

        如果选中了--force选项，会删除路径下的原有内容，然后重新初始化。
        """
        init_command = self.subparsers.add_parser(
            'init',
            prog='oedp init',
            help='Initialize a plugin to a project.',
            usage='%(prog)s <plugin> -p|--project <path> [-f|--force]',
        )
        init_command.add_argument(
            'plugin',
            type=str,
            help='Specify the plugin name.'
        )
        init_command.add_argument(
            '-l', '--local',
            type=str,
            default=PLUGIN_DIR,
            help='Specify the local source path',
        )
        init_command.add_argument(
            '-p', '--project',
            type=str,
            help='Specify the project path.',
            required=True,
            metavar='<path>'
        )
        init_command.add_argument(
            '-f', '--force',
            action='store_true',
            help='Force the initialization of a project, overwrite existing project.',
        )
        init_command.set_defaults(func=self._run_init_command)

    def _add_list_command(self):
        """
        oedp list [-l|--local <path>]

        列举源中可用的插件。可以指定本地源。
        """
        drop_command = self.subparsers.add_parser(
            'list',
            prog='oedp list',
            help='List all available plugins',
            usage='%(prog)s [-l|--local <path>]',
        )
        drop_command.add_argument(
            '-l', '--local',
            type=str,
            default=PLUGIN_DIR,
            help='Specify the local source path',
        )
        drop_command.set_defaults(func=self._run_list_command)

    def _add_info_command(self):
        """
        oedp info [-p|--project <path>]

        查看一个项目的详细信息。

        如果没有指定路径，以当前路径作为项目路径，否则以指明的路径为项目路径。
        """
        info_command = self.subparsers.add_parser(
            'info',
            prog='oedp info',
            help='Show plugin information',
            usage='%(prog)s [-p|--project <path>]'
        )
        info_command.add_argument(
            '-p', '--project',
            type=str,
            default=os.getcwd(),
            help='Specify the project path.'
        )
        info_command.set_defaults(func=self._run_info_command)

    def _add_run_command(self):
        """
        oedp run <action> [-p|--project <path>]

        执行一个项目中的方法。

        如果没有指定路径，以当前路径作为项目路径，否则以指明的路径为项目路径。
        """
        deploy_command = self.subparsers.add_parser(
            'run',
            prog='oedp run',
            help='run an action on a project',
            usage='%(prog)s <action> [-p|--project <path>]'
        )
        deploy_command.add_argument(
            'action',
            type=str,
            help='Specify the action to run'
        )
        deploy_command.add_argument(
            '-p', '--project',
            type=str,
            default=os.getcwd(),
            help='Specify the project path'
        )
        deploy_command.add_argument(
            '-d', '--debug',
            action='store_true',
            help='Enable debug mode'
        )
        deploy_command.set_defaults(func=self._run_run_command)

    def _add_check_command(self):
        """
        oedp check <action> [-p|--project <path>]

        检查项目中指定方法的检查项。

        如果没有指定路径，以当前路径作为项目路径，否则以指明的路径为项目路径。
        """
        check_command = self.subparsers.add_parser(
            'check',
            prog='oedp check',
            help='check the connection'
        )
        check_command.add_argument(
            'action',
            type=str,
            help='Specify the action to check'
        )
        check_command.add_argument(
            '-p', '--project',
            type=str,
            default=os.getcwd(),
            help='Specify the project path.'
        )
        check_command.set_defaults(func=self._run_check_command)

    def _add_repo_command(self):
        """
        oedp repo <subcommand> [<args>]

        插件源管理
        """
        repo_command = self.subparsers.add_parser(
            'repo',
            prog='oedp repo',
            help='Manage plugin repositories',
            usage='%(prog)s <subcommand> [<args>]'
        )
        subparsers = repo_command.add_subparsers(
            dest='subcommand',
            title='Available subcommands',
            required=True,
            metavar='<subcommand>'
        )

        # repo list
        list_parser = subparsers.add_parser(
            'list',
            help='List all configured repositories'
        )
        list_parser.set_defaults(func=self._run_repo_command)

        # repo update
        update_parser = subparsers.add_parser(
            'update',
            help='Update repository index cache'
        )
        update_parser.set_defaults(func=self._run_repo_command)

        # repo set
        set_parser = subparsers.add_parser(
            'set',
            help='Modify repository URL'
        )
        set_parser.add_argument(
            'name',
            type=str,
            help='Repository name'
        )
        set_parser.add_argument(
            'url',
            type=str,
            help='New repository URL'
        )
        set_parser.set_defaults(func=self._run_repo_command)

        # repo del
        del_parser = subparsers.add_parser(
            'del',
            help='Delete a repository'
        )
        del_parser.add_argument(
            'name',
            type=str,
            help='Repository name to delete'
        )
        del_parser.set_defaults(func=self._run_repo_command)

        # repo enable
        enable_parser = subparsers.add_parser(
            'enable',
            help='Enable a repository'
        )
        enable_parser.add_argument(
            'name',
            type=str,
            help='Repository name to enable'
        )
        enable_parser.set_defaults(func=self._run_repo_command)

        # repo disable
        disable_parser = subparsers.add_parser(
            'disable',
            help='Disable a repository'
        )
        disable_parser.add_argument(
            'name',
            type=str,
            help='Repository name to disable'
        )
        disable_parser.set_defaults(func=self._run_repo_command)

    @staticmethod
    def _run_init_command(args):
        plugin = args.plugin
        source = args.local
        project = args.project
        force = args.force
        return InitCmd(plugin, source, project, force).run()

    @staticmethod
    def _run_list_command(args):
        source = args.local
        return ListCmd(source).run()

    @staticmethod
    def _run_info_command(args):
        project = args.project
        return InfoCmd(project).run()

    @staticmethod
    def _run_run_command(args):
        action = args.action
        project = args.project
        debug = args.debug
        return RunCmd(action, project, debug).run()

    @staticmethod
    def _run_check_command(args):
        project = args.project
        group = args.group
        return CheckCmd(project, group).run()

    @staticmethod
    def _run_repo_command(args):
        return RepoCmd(args).run()

    @staticmethod
    def _get_version():
        stdout, _, return_code = CommandExecutor.run_single_cmd(['rpm', '-q', 'oedp'])
        if not return_code:
            match = re.search(r'-([\d]+\.[\d]+\.[\d]+-\d+)', stdout.strip())
            if match:
                return match.group(1)
            else:
                return VERSION
        else:
            return VERSION
