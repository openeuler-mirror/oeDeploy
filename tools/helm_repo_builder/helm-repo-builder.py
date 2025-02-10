#!/usr/bin/python3
import argparse
import os
import re
import subprocess
from io import BytesIO

import requests
import yaml
from tqdm import tqdm


def get_parser():
    parser = argparse.ArgumentParser(
        description='一键制作Helm镜像仓库的工具',
        epilog="示例用法：\n./helm-repo-builder.py https://charts.example.com/helm --url https://mirror.example.com/helm --path ./charts",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # 必需参数
    parser.add_argument(
        'repo_url',
        help='源仓库的URL（与`helm repo add`使用的URL相同）'
    )

    # 可选参数
    parser.add_argument(
        '--url',
        metavar='URL',
        dest='mirror_url',
        default='',
        help='镜像仓库基础URL（默认：空，生成相对路径的index.yaml）'
    )

    parser.add_argument(
        '--path',
        default=os.getcwd(),
        help=f'本地存储路径（默认：当前目录 {os.getcwd()}）'
    )

    parser.add_argument(
        '--prefix',
        default=None,
        help='自定义公共前缀（默认：自动分析公共前缀）'
    )

    parser.add_argument(
        '--re-download',
        action='store_true',
        help='强制重新下载所有文件（默认：校验存在文件后跳过）'
    )

    # 互斥组
    index_group = parser.add_mutually_exclusive_group()
    index_group.add_argument(
        '--no-index',
        action='store_true',
        help='仅下载chart文件，不生成index.yaml'
    )
    index_group.add_argument(
        '--only-index',
        action='store_true',
        help='仅生成index.yaml，不下载chart文件'
    )

    parser.add_argument(
        '--new-index',
        action='store_true',
        help='强制覆盖已存在的index.yaml（默认：合并更新）'
    )

    parser.add_argument(
        '--retry',
        type=int,
        default=5,
        help='下载失败重试次数（默认：5）'
    )

    return parser


def check_sum(file_path, checksum):
    sha256 = subprocess.run(['sha256sum', file_path], stdout=subprocess.PIPE).stdout.decode('utf-8').split()[0]
    return sha256 == checksum or 'sha256:' + sha256 == checksum


def download_file(url, path, retry, checksum):
    for attempt in range(retry + 1):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024

            with open(path, 'wb') as f, tqdm(
                    total=total_size, unit='B', unit_scale=True, unit_divisor=1024,
                    desc=os.path.basename(path)) as pbar:
                for chunk in response.iter_content(block_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
            if check_sum(path, checksum):
                return
            elif attempt < retry:
                print(f'下载失败，第{attempt + 1}/{retry}次重试')
            else:
                raise Exception(f'下载失败（{url}），和校验不通过')
        except requests.exceptions.RequestException:
            if attempt < retry:
                print(f'下载失败，第{attempt + 1}/{retry}次重试')
            else:
                raise Exception(f'下载失败（{url}），请检查网络')


def get_index(repo_url, retry):
    index_url = f'{repo_url}/index.yaml'
    for attempt in range(retry + 1):
        try:
            response = requests.get(index_url, stream=True)
            response.raise_for_status()
            block_size = 1024

            file_buffer = BytesIO()
            for chunk in response.iter_content(block_size):
                if chunk:
                    file_buffer.write(chunk)
            file_buffer.seek(0)
            index_content = file_buffer.getvalue().decode('utf-8')
            index_yaml = yaml.safe_load(index_content)
            return index_yaml
        except requests.exceptions.RequestException:
            if attempt == retry:
                raise Exception(f'获取index.yaml失败（{index_url}），请检查网络')
        except yaml.YAMLError as e:
            if attempt == retry:
                raise Exception('解析index.yaml失败', e)


def get_prefix(index_yaml):
    urls = []
    for entry in index_yaml['entries'].values():
        urls.extend([i['urls'][0] for i in entry])
    if len(urls) == 0:
        return ''
    for i, url in enumerate(urls):
        if url.startswith('http'):
            urls[i] = re.sub(r'^https?://', '', url)
    split_urls = [i.split('/') for i in urls]
    prefix = ''
    for i in range(len(split_urls[0])):
        check = True
        for split_url in split_urls:
            if len(split_url[i]) <= i or split_url[i] != split_urls[0][i]:
                check = False
        if check:
            prefix += '/' + split_urls[0][i]
        else:
            break
    return prefix[1:]


def get_file_path(url, prefix, path):
    if url.startswith('http'):
        url = re.sub(r'^https?://', '', url)
    if not url.startswith(prefix):
        raise Exception(f'URL匹配前缀失败：{url}')
    file_path = os.path.join(path, url[len(prefix) + 1:])
    return file_path


def work(repo_url, mirror_url, path, prefix, re_download, no_index, only_index, new_index, retry):
    if not only_index:
        index_yaml = get_index(repo_url, retry)
        if prefix is None:
            prefix = get_prefix(index_yaml)
        for entry in index_yaml['entries'].values():
            for item in entry:
                file_path = get_file_path(item['urls'][0], prefix, path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                if re_download or not os.path.exists(file_path) or not check_sum(file_path, item['digest']):
                    download_file(item['urls'][0], file_path, retry, item['digest'])
    if not no_index:
        index_path = os.path.join(path, 'index.yaml')
        if new_index and os.path.exists(index_path):
            os.remove(index_path)
        cmd = ['helm', 'repo', 'index', path]
        if mirror_url:
            cmd.extend(['--url', mirror_url])
        subprocess.run(cmd)


def main():
    parser = get_parser()
    try:
        args = parser.parse_args()
        work(args.repo_url, args.mirror_url, args.path, args.prefix, args.re_download,
             args.no_index, args.only_index, args.new_index, args.retry)
    except KeyboardInterrupt:
        print('Interrupted by user')
        exit(1)
    except Exception as ex:
        print(ex)
        exit(1)


if __name__ == '__main__':
    main()
    exit(0)
