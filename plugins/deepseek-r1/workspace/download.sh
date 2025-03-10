#!/bin/bash

download_url=$1
store_path=$2
check=$3
timeout=$4
retry=$5

download_file=$(basename "$download_url")

download_file_with_retry() {
  local url=$1
  local dest=$2
  local retries=$3
  local timeout=$4
  local attempt=0

  while [ $attempt -lt $retries ]; do
    echo "Attempt $(($attempt + 1)) to download $url..."
    curl -C - --max-time "$timeout" -o "$dest" "$url"
    if [ $? -eq 0 ]; then
      return 0
    fi
    attempt=$(($attempt + 1))
  done

  return 1
}

# 关闭sha256校验
if [ "$check" -eq 0 ]; then
  download_file_with_retry "$download_url" "$store_path/$download_file" "$retry" "$timeout"
  if [ $? -eq 0 ]; then
    echo "Download succeeded."
    exit 0
  else
    echo "Download failed."
    exit 1
  fi
fi

# 打开sha256校验
if [ "$check" -eq 1 ]; then
  sha256sum_url="${download_url}.sha256sum"
  sha256sum_file="$store_path/${download_file}.sha256sum"
  curl -s --max-time 60 -o "$sha256sum_file" "$sha256sum_url"
  if [ $? -ne 0 ]; then
    echo "Failed to download SHA256 checksum file."
    exit 1
  fi

  remote_sum=$(cat "$sha256sum_file" | awk '{print $1}')

  local_file="$store_path/$download_file"
  if [ -f "$local_file" ]; then
    local_sum=$(sha256sum "$local_file" | awk '{print $1}')
    if [ "$local_sum" == "$remote_sum" ]; then
      echo "Local file checksum matches remote checksum."
      exit 0
    fi
  fi

  attempt=0
  while [ $attempt -lt $retry ]; do
    echo "Attempt $(($attempt + 1)) to download $download_url and verify checksum..."
    download_file_with_retry "$download_url" "$local_file" 1 "$timeout"
    if [ $? -ne 0 ]; then
      echo "Download failed."
      attempt=$(($attempt + 1))
      continue
    fi

    local_sum=$(sha256sum "$local_file" | awk '{print $1}')
    if [ "$local_sum" == "$remote_sum" ]; then
      echo "Checksum matches. Download succeeded."
      exit 0
    fi

    attempt=$(($attempt + 1))
  done

  echo "Checksum verification failed after $retry attempts."
  exit 1
fi

echo "Invalid check parameter. Must be 0 or 1."
exit 1