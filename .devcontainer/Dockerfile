# oeDeploy devcontainer - openEuler 24.03-LTS
# 资源要求：常规开发环境即可（内存 >= 2GB，磁盘 >= 5GB）
#
# 设计说明：
#   1. 基础镜像与仓库发布形态对齐：README/构建产物均为 openEuler-24.03-LTS RPM
#   2. 系统包使用 dnf 包名，运行时依赖对齐 oedp.spec 的 Requires
#      （python3 / ansible / tar / rsync / python3-prettytable / python3-netaddr / python3-packaging）
#   3. 测试依赖（pytest / coverage / pyyaml）用 dnf 安装，不依赖 pip 网络
#   4. 内网 dnf 镜像源不写死，通过 ARG 传入（默认官方源）；凭据一律走 remoteEnv/envFile
ARG OPENEULER_IMAGE=openeuler/openeuler:24.03-lts
FROM ${OPENEULER_IMAGE}

ARG TZ=Asia/Shanghai
ENV TZ="${TZ}"

# dnf 镜像源覆盖：默认官方源；内网/慢网络可用 --build-arg OPENEULER_REPO=https://mirrors.xxx/openeuler
ARG OPENEULER_REPO="https://repo.openeuler.org"

# 基础工具链 + Python + oedp 运行时/测试依赖（dnf 包名；update 与 install 在同一 RUN 层分步执行，结尾 clean all）
# 替换 baseurl/gpgkey 前缀并移除 metalink（避免 metalink 504 导致构建失败；gpgkey 也走 https 镜像源）
# 去掉 OPENEULER_REPO 可能携带的尾斜杠，避免拼接出 // 双斜杠
RUN sed -i -e "s|https\?://repo.openeuler.org|${OPENEULER_REPO%/}|g" -e "/metalink=/d" /etc/yum.repos.d/openEuler.repo \
    && dnf update -y --setopt=retries=5 --setopt=timeout=60 \
    && dnf install -y --setopt=retries=5 --setopt=timeout=60 \
    git \
    curl \
    wget \
    tar \
    unzip \
    xz \
    bzip2 \
    jq \
    vim \
    tmux \
    zsh \
    bash-completion \
    sudo \
    python3 \
    python3-devel \
    python3-pip \
    python3-setuptools \
    ansible \
    rsync \
    python3-prettytable \
    python3-netaddr \
    python3-packaging \
    python3-pyyaml \
    python3-tabulate \
    python3-pytest \
    python3-pytest-mock \
    python3-coverage \
    && dnf clean all

# 创建开发用户（devcontainer remoteUser）
RUN useradd -m -s /bin/bash vscode && \
    echo 'vscode ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/vscode && \
    chmod 440 /etc/sudoers.d/vscode && \
    mkdir -p /workspace /commandhistory /home/vscode/.cache/pip && \
    chown -R vscode:vscode /workspace /commandhistory /home/vscode/.cache

WORKDIR /workspace
USER vscode
ENV PATH="/home/vscode/.local/bin:/usr/local/bin:$PATH"
ENV SHELL=/bin/bash
ENV EDITOR=vim
