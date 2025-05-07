#!/bin/bash

# 检查参数个数
if [ $# -lt 2 ]; then
    echo "Usage: $0 <url> <output_path>"
    exit 1
fi

URL="$1"
OUTPUT_PATH="$2"

if [ ! -d $OUTPUT_PATH ]; then
  mkdir -p "$OUTPUT_PATH"
fi

rpm -q wget >/dev/null 2>&1
if [ $? -ne 0 ];then
  echo "install wget failed"
  exit 1
fi

MAX_RETRIES=5
RETRY_COUNT=1
SLEEP_TIME=2
TIMEOUT=1200

echo "开始下载文件: $URL"
echo "保存路径: $OUTPUT_PATH"

while [ $RETRY_COUNT -le $MAX_RETRIES ]; do
    echo "尝试第 $RETRY_COUNT 次下载..."

    wget --timeout=$TIMEOUT \
         -P "$OUTPUT_PATH" \
         -c \
         "$URL"

    if [ $? -eq 0 ]; then
        echo "下载成功！"
        exit 0
    else
        echo "下载失败，准备重试..."
        sleep $SLEEP_TIME
        RETRY_COUNT=$((RETRY_COUNT + 1))
    fi
done

echo "错误：超过最大重试次数 ($MAX_RETRIES 次)，下载失败。"
exit 1