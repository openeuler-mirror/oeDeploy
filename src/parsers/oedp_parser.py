# Copyright (c) 2024 Huawei Technologies Co., Ltd. All Rights Reserved.
# 本文件是oeDeploy软件（“本软件”）的一部分，受您与华为签订的保密协议约束。
# 除非另有协议约定或经华为书面授权，您不得将本软件披露、公开或分发给任何第三方，包括您的关联公司。
# 本软件按“原样”提供，不附带任何明示或默示的担保。华为不对您因使用本软件而引发的任何直接或间接损失承担责任。
# ======================================================================================================================

import argparse
import os

from src.commands.check.check_cmd import CheckCmd
from src.commands.info.info_cmd import InfoCmd
from src.commands.init.init_cmd import InitCmd
from src.commands.list.list_cmd import ListCmd
from src.commands.run.run_cmd import RunCmd
from src.constants.paths import PLUGIN_DIR


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
        return RunCmd(action, project).run()

    @staticmethod
    def _run_check_command(args):
        project = args.project
        group = args.group
        return CheckCmd(project, group).run()
