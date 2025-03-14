#!/bin/bash
current_path=$(
    cd $(dirname $0/)
    pwd
)
ENV_FILE=/root/.bashrc
source $current_path/config.cfg
source $ENV_FILE
# 仅主节点运行

if [ $NODE_NUM -eq 2 ]; then
	NPU_NUM=16.0
    PARALLEL=16
elif [ $NODE_NUM -eq 4 ]; then
	NPU_NUM=32.0
    PARALLEL=32
fi

ray_status=0
for i in {1..10}; do
    ray status | grep "$NPU_NUM NPU"
    if [ $? -eq 0 ]; then
        echo "ray集群已全部拉起"
        ray_status=1
        break
    fi
    sleep 3
done

if [ $ray_status -eq 0 ]; then
    echo "ray集群超时"
    exit 1
fi

#拉起服务
rm -rf ds.log
nohup python3 -m vllm_mindspore.entrypoints vllm.entrypoints.openai.api_server --model "$MODEL_PATH" --port=$LLM_PORT --trust_remote_code --tensor_parallel_size=$PARALLEL --max-num-seqs=192 --max_model_len=32768 --max-num-batched-tokens=16384 --block-size=32 --gpu-memory-utilization=0.93 --num-scheduler-steps=8 --distributed-executor-backend=ray &> ds.log &
#检测推理服务是否拉起
llm_status=0
for i in {1..7200}; do
    netstat -ntlp | grep $LLM_PORT
    if [ $? -eq 0 ]; then
        echo "推理服务已拉起，端口$LLM_PORT已打开"
        llm_status=1
        break
    fi
    sleep 1
done

if [ $llm_status -eq 0 ]; then
    echo "推理服务拉起超时，请手动确认"
    exit 1
fi