#!/bin/bash

# 获取脚本绝对路径
SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
PROJECT_ROOT="$SCRIPT_DIR/../oedp"

# 设置Python环境变量
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 执行测试用例
coverage run -m pytest

# 检查执行结果
if [ $? -eq 0 ]; then
    echo "所有测试用例执行成功"
    coverage report
else
    echo "部分测试用例执行失败"
    exit 1
fi