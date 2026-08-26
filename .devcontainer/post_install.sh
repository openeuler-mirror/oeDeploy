#!/usr/bin/env bash
# oeDeploy 环境初始化脚本（幂等，可重复执行）
# 原则：运行时目录/默认配置初始化 + CLI 冒烟测试 + 单元测试
set -euo pipefail

OEDP_HOME="/var/oedp"
OEDP_CONFIG_HOME="/etc/oedp"
SRC_CONFIG_DIR="/workspace/oedp/src/config"
LOCAL_PLUGIN_DIR="/opt/oedp/plugins"

echo "==> 检查工作区可写性（bind 挂载文件若为 root 属主，vscode 用户只读，需调整属主）"
if ! touch /workspace/.devcontainer-write-probe 2>/dev/null; then
    echo "    工作区不可写，执行 sudo chown -R vscode:vscode /workspace（会改变宿主机检出目录属主）"
    sudo chown -R vscode:vscode /workspace
fi
rm -f /workspace/.devcontainer-write-probe

echo "==> 初始化 oedp 运行时目录（对齐 RPM %files 目录结构）"
sudo mkdir -p "${OEDP_HOME}"/details "${OEDP_HOME}"/log "${OEDP_HOME}"/plugin
sudo mkdir -p "${OEDP_CONFIG_HOME}"/config/repo/cache
sudo mkdir -p "${OEDP_CONFIG_HOME}"/config/log
sudo mkdir -p "${LOCAL_PLUGIN_DIR}"
# RPM %files 中这些目录为 777，允许非 root 用户直接读写
sudo chmod 777 "${OEDP_HOME}"/details "${OEDP_HOME}"/log "${OEDP_HOME}"/plugin \
    "${OEDP_CONFIG_HOME}"/config "${OEDP_CONFIG_HOME}"/config/log \
    "${OEDP_CONFIG_HOME}"/config/repo \
    "${OEDP_CONFIG_HOME}"/config/repo/cache "${LOCAL_PLUGIN_DIR}"

echo "==> 复制默认配置（不覆盖用户已有配置）"
if [ ! -f "${OEDP_CONFIG_HOME}"/config/log/log.conf ]; then
  sudo cp "${SRC_CONFIG_DIR}"/log.conf "${OEDP_CONFIG_HOME}"/config/log/log.conf
  sudo chmod 666 "${OEDP_CONFIG_HOME}"/config/log/log.conf
fi
if [ ! -f "${OEDP_CONFIG_HOME}"/config/repo/repo.conf ]; then
  sudo cp "${SRC_CONFIG_DIR}"/repo/repo.conf "${OEDP_CONFIG_HOME}"/config/repo/repo.conf
  sudo chmod 666 "${OEDP_CONFIG_HOME}"/config/repo/repo.conf
fi
sudo touch "${OEDP_HOME}"/log/oedp.log
sudo chmod 666 "${OEDP_HOME}"/log/oedp.log

echo "==> 安装开发便利命令：oedp（指向源码树，源码树内可运行）"
sudo tee /usr/local/bin/oedp >/dev/null <<'EOF'
#!/usr/bin/env bash
PYTHONPATH=/workspace/oedp exec python3 /workspace/oedp/oedp.py "$@"
EOF
sudo chmod 755 /usr/local/bin/oedp

echo "==> 冒烟测试：oedp CLI 可加载"
oedp --version
oedp repo list || true

echo "==> 运行单元测试"
# 测试产物（.coverage / .pytest_cache / __pycache__）重定向到容器内，避免写入
# 宿主机挂载的工作区（尤其是工作区里已有 root 所有旧产物时，非 root 用户会无权限覆盖）
export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-p no:cacheprovider"
export COVERAGE_FILE=/tmp/oedp-coverage/.coverage
mkdir -p /tmp/oedp-coverage
cd /workspace/unittest
bash run_tests.sh

echo "==> devcontainer 环境初始化完成。"
