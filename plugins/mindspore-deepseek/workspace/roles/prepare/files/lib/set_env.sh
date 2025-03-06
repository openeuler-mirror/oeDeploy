#!/bin/bash

# 各个节点的容器内均执行
current_path=$(
    cd $(dirname $0/)
    pwd
)
source $current_path/config.cfg

ENV_ARG='
# openeuler_deepseek_env_config
export ASCEND_CUSTOM_PATH=$ASCEND_HOME_PATH/../
export MS_ENABLE_LCCL=off
export HCCL_OP_EXPANSION_MODE=AIV
export vLLM_MODEL_BACKEND=MindFormers
export vLLM_MODEL_MEMORY_USE_GB=50
export MS_DEV_RUNTIME_CONF="parallel_dispatch_kernel:True"
export MS_ALLOC_CONF="enable_vmm:False"
export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export ASCEND_TOTAL_MEMORY_GB=64
'

RAY_ENV="
export GLOO_SOCKET_IFNAME=$RAY_DEVICE
export TP_SOCKET_IFNAME=$RAY_DEVICE
"

W8A8_ENV='export MINDFORMERS_MODEL_CONFIG=/root/miniconda3/lib/python3.11/site-packages/research/deepseek3/deepseek3_671b/predict_deepseek3_671b_w8a8.yaml'

if grep -q "openeuler_deepseek_env_config" /root/.bashrc; then
    echo "存在已配置的环境变量，详见容器内/root/.bashrc"
    exit 0
fi

echo "$ENV_ARG" >> /root/.bashrc
echo "$RAY_ENV" >> /root/.bashrc
echo "$W8A8_ENV" >> /root/.bashrc
source /root/.bashrc

