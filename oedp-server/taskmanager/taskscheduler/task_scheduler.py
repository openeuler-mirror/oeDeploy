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

import functools
import multiprocessing
import os
import queue
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

from django.db import connections
from utils.record_time.record_time import RecordTime

from constants.configs.task_config import task_config
from taskmanager.taskscheduler import service
from taskmanager.taskscheduler.task import TaskStatus
from utils.logger import init_log

task_logger = init_log("taskmanager.log")

__all__ = ["TASK_SCHEDULER"]


def reopen_logger_file():
    """
    多进程+多线程的架构在fork子进程时其他线程如果正在打印日志会持有日志的文件锁
    fork之后的父子进程文件锁都是持有的，父进程可以正常释放，单子进程无法释放导致日志打印卡死
    多进程fork后重新打开日志文件，替换掉原来的日志文件对象，防止日志文件锁导致卡住
    """
    for handler in task_logger.handlers:
        if hasattr(handler, "stream") and hasattr(handler, "_open"):
            handler.stream = handler._open()


def keep_while_true(func):
    """
    装饰器，保持while True
    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            func(*args, **kwargs)

    return wrapper


def task_thread_handler(task_manager):
    """
    开启任务进程
    :param task_manager:
    :return:
    """
    reopen_logger_file()
    connections.close_all()
    task_manager.thread_id = threading.get_ident()
    ip_address = "127.0.0.1"
    port = '22'
    if task_manager.task.node.get("node_alias_name", ""):
        ip_address = task_manager.task.node.get("ip_address", "127.0.0.1")
        port = task_manager.task.node.get("port", '22')
    elif task_manager.task.node.get("dst_node_alias_name", ""):
        ip_address = task_manager.task.node.get("dst_ip_address", "127.0.0.1")
        port = task_manager.task.node.get("dst_port", '22')
    actor_name = task_manager.task.__class__.__name__
    task_logger.info("Task start successfully,thread[%s]|ip[%s]|port[%s]|actor_name[%s].", task_manager.thread_id,
                ip_address, port, actor_name)
    task = task_manager.task
    message_queue = task_manager.message_queue
    task.start(message_queue)


def capture_thread_exception(future_obj):
    """
    捕获线程池运行异常
    :param future_obj:
    :return:
    """
    task_exception = future_obj.exception()
    if task_exception:
        ex = traceback.format_exc()
        task_logger.error("======ex: %s", ex)
        task_logger.error("task run error, error is %s", task_exception)


class TaskManager:
    """
    任务调度模块使用的任务类，封装各模块具体的任务实例
    """

    def __init__(self, task, message_queue):
        self.task = task
        self.message_queue = message_queue
        self.thread = None
        self.thread_id = 0
        self.thread_timeout = 0
        self.thread_start_time = None  # timezone实例


class ThreadManager:
    """
    线程管理类，封装需要的各种信息
    """

    def __init__(self, task_thread_pool, message_queue, pending_queue, pending_queue_condition,
                 running_task_queue, running_task_condition):
        self.task_thread_pool = task_thread_pool
        self.message_queue = message_queue
        self.pending_queue = pending_queue
        self.pending_queue_condition = pending_queue_condition
        self.running_task_queue = running_task_queue
        self.running_task_condition = running_task_condition


class ProcessManager:
    """
    进程管理类，封装需要的各种信息
    """

    def __init__(self, thread_pool_number, pending_queue, pending_queue_condition):
        self.process = None
        self.thread_pool_number = thread_pool_number
        self.pending_queue = pending_queue
        self.pending_queue_condition = pending_queue_condition


@keep_while_true
def update_task(thread_obj):
    """
    任务状态刷新
    :param thread_obj: 线程管理类对象
    :return: None
    """
    reopen_logger_file()
    try:
        message = thread_obj.message_queue.get(True)
        connections.close_all()
        # 更新数据库
        is_completed = message.pop("is_completed")
        service.schedule_model_service(message)
        # 更新时间节点
        RecordTime.update_end_time(message)
        # 判断任务是否结束，结束则从运行队列剔除该任务
        check_task_complete(thread_obj, message, is_completed)
    except Exception as ex:
        task_logger.error(ex)


@keep_while_true
def schedule_task(thread_obj):
    """
    任务调度
    :param thread_obj: 线程管理类对象
    :return: None
    """
    reopen_logger_file()
    task_logger.info("schedule task start")
    try:
        with thread_obj.pending_queue_condition:
            if thread_obj.pending_queue.empty():
                thread_obj.pending_queue_condition.wait()
        task_logger.info("schedule task pid is %s", os.getpid())
        task = thread_obj.pending_queue.get()
        with thread_obj.running_task_condition:
            task_manager = TaskManager(task, thread_obj.message_queue)
            task_thread = thread_obj.task_thread_pool.submit(task_thread_handler, task_manager)
            task_thread.add_done_callback(capture_thread_exception)
            task_manager.thread = task_thread
            thread_obj.running_task_queue.put(task_manager)
            thread_obj.running_task_condition.notify()
        task_logger.info("schedule task finish")
    except Exception as ex:
        task_logger.error(ex)


@keep_while_true
def monitor_task(thread_obj):
    """
    任务进程监控（进程保活已完成，心跳待完成）
    :param thread_obj: 线程管理类对象
    :return: None
    """
    reopen_logger_file()
    try:
        check_task_timeout(thread_obj)
    except Exception as ex:
        task_logger.error(ex)
    time.sleep(TaskScheduler.THREAD_MONITORING_DURATION_INTERVAL)


def check_task_timeout(thread_obj):
    """
    检查任务是否超时，如果超时，将任务置为任务异常
    :param thread_obj: 线程管理类对象
    :return: None
    """
    with thread_obj.running_task_condition:
        if thread_obj.running_task_queue.empty():
            thread_obj.running_task_condition.wait()

        for _ in range(thread_obj.running_task_queue.qsize()):
            task_manager = thread_obj.running_task_queue.get()
            if not task_manager.thread.done():
                thread_obj.running_task_queue.put(task_manager)
                continue
            if task_manager.thread_timeout >= task_config.thread_timeout:
                # 进程异常退出，将数据库任务状态置成任务异常
                connections.close_all()
                message = service.generate_process_timeout_message(task_manager.task.node)
                service.schedule_model_service(message)
                task_logger.error("Task[%s] thread[%s] timeout.", task_manager.task.node.get('id'), task_manager.thread_id)
            else:
                task_manager.thread_timeout += TaskScheduler.THREAD_MONITORING_DURATION_INTERVAL
                thread_obj.running_task_queue.put(task_manager)


def check_task_complete(thread_obj, message, complete_status):
    """
    检查任务是否完成，如果完成，将任务从运行队列中移除
    :param thread_obj: 线程管理类对象
    :param message: 任务间通信的消息队列
    :param complete_status: 任务是否完成的标志
    :return: None
    """
    with thread_obj.running_task_condition:
        if not TaskStatus.task_is_completed(complete_status):
            return
        task_logger.info("Node[%s] current step[%s] result is: %s.", message.get('id'), message.get('current_step'),
                    message.get('current_step_status'))
        service.update_task_completed(message)
        for _ in range(thread_obj.running_task_queue.qsize()):
            task_manager = thread_obj.running_task_queue.get()
            if task_manager.task.id == message.get("id"):
                break
            else:
                thread_obj.running_task_queue.put(task_manager)


def manage_process(process_id):
    """
    管理进程运行，生成线程运行必要环境，创建任务运行线程池
    :param process_id: 进程编号
    :return: None
    """
    reopen_logger_file()
    task_logger.info("Process start, pid is %s", os.getpid())
    process_manager = None
    while not process_manager:
        process_manager = TaskScheduler.process_dict.get(process_id)
    running_task_queue = queue.Queue()
    # 创建通信用的消息队列
    message_queue = queue.Queue()
    # 控制运行队列存放和取出的条件变量
    running_task_condition = threading.Condition()
    # 创建用来运行任务的线程池
    task_thread_pool = ThreadPoolExecutor(process_manager.thread_pool_number)
    # 初始时，子进程中的任务数为0
    thread_obj = ThreadManager(task_thread_pool, message_queue,
                               process_manager.pending_queue,
                               process_manager.pending_queue_condition,
                               running_task_queue,
                               running_task_condition)
    update_task_thread = threading.Thread(target=update_task, args=(thread_obj,), daemon=True)
    update_task_thread.start()
    monitor_task_thread = threading.Thread(target=monitor_task, args=(thread_obj,), daemon=True)
    monitor_task_thread.start()
    schedule_task_thread = threading.Thread(target=schedule_task, args=(thread_obj,), daemon=True)
    schedule_task_thread.start()
    update_task_thread.join()
    monitor_task_thread.join()
    schedule_task_thread.join()
    task_logger.info("Process end, pid is %s", os.getpid())


class TaskScheduler:
    """
    单例实现任务调度模块
    """
    # 线程监控间隔
    THREAD_MONITORING_DURATION_INTERVAL = 2
    # 任务监控间隔
    RUNNING_TASK_DURATION_INTERVAL = 2
    # 最大任务数
    MAX_RUNNING_TASK = task_config.max_task_number
    # 单例
    _instance = None
    # 机器核数
    cpu_number = multiprocessing.cpu_count()
    # 存储子进程的字典
    process_dict = dict()
    # 主进程存放任务的队列
    task_save_queue = queue.Queue()
    # 控制主线程任务队列的条件变量
    task_save_queue_condition = threading.Condition()
    process_num = 0

    def __new__(cls, *args, **kw):
        """ 实例化单例 """
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
            cls._instance.start()
        return cls._instance

    def start(self):
        """
        随单例实例化启动任务调度功能
        :return: None
        """
        # 防止获取cpu数量异常导致除数不正确的情况
        if self.cpu_number <= 0:
            self.cpu_number = 1
        # 当cpu数量为1时，线程池数为任务数
        if self.cpu_number == 1:
            thread_pool_number = self.MAX_RUNNING_TASK
        # 当cpu数量大于任务数量时，要创建的进程数变为任务数，每个进程中线程池的数量为1
        elif self.cpu_number > self.MAX_RUNNING_TASK:
            self.cpu_number = self.MAX_RUNNING_TASK
            thread_pool_number = 1
        # 每个进程的线程池数量为任务数/进程数，如果有余数，那么每个进程中线程池数量多一个
        else:
            additional_quantity = 0
            if self.MAX_RUNNING_TASK % self.cpu_number != 0:
                additional_quantity = 1
            thread_pool_number = int(self.MAX_RUNNING_TASK / self.cpu_number) + additional_quantity
        task_logger.info("process number is %s", self.cpu_number)
        task_logger.info("thread number is %s", thread_pool_number)
        distribute_task_thread = threading.Thread(target=self.distribute_task, args=())
        distribute_task_thread.daemon = True
        distribute_task_thread.start()
        self.start_subprocess(thread_pool_number)
        task_logger.info("start finish")

    def start_subprocess(self, thread_pool_number):
        """
        子进程管理，生成子进程
        :param thread_pool_number: 子进程中需要开启的线程数量
        :return: None
        """
        try:
            for i in range(self.cpu_number):
                # 生成和子进程通信的等待队列，用来存放需要执行的任务，当主进程有任务添加时，通过此队列将任务分发给子进程
                pending_queue = multiprocessing.Queue()
                pending_queue_condition = multiprocessing.Condition()
                process_manager = ProcessManager(thread_pool_number, pending_queue, pending_queue_condition)
                self.process_dict[i] = process_manager
                process_obj = multiprocessing.Process(target=manage_process, args=(i,), daemon=True)
                process_manager.process = process_obj
                process_obj.start()
        except Exception as ex:
            task_logger.error(ex)
        task_logger.info("create subprocess finish")

    @keep_while_true
    def distribute_task(self):
        """
        任务分发，将添加到等待队列中的任务分发给子进程
        :return: None
        """
        task_logger.info("distribute task start")
        try:
            with self.task_save_queue_condition:
                if self.task_save_queue.empty():
                    self.task_save_queue_condition.wait()
            task = self.task_save_queue.get()
            # 选择需要分发任务的子进程
            process_manager = self.process_dict.get(self.process_num)
            self.process_num = self.process_num + 1
            if self.process_num == self.cpu_number:
                self.process_num = 0
            # 将任务分发个选定的子进程
            with process_manager.pending_queue_condition:
                process_manager.pending_queue.put(task)
                process_manager.pending_queue_condition.notify()
            task_logger.info("distribute task finish")
        except Exception as ex:
            task_logger.error(ex)

    def add_task(self, task):
        """
        添加任务，唤醒任务分发线程
        :param task: 任务actor
        :return: None
        """
        task_logger.info("add task start")
        with self.task_save_queue_condition:
            self.task_save_queue.put(task)
            self.task_save_queue_condition.notify()
        task_logger.info("add task finish")


TASK_SCHEDULER = TaskScheduler()
