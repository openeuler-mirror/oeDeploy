# CANN Toolkit 一键部署插件

## 插件简介

CANN Toolkit 一键部署插件是基于 oeDeploy 框架开发的自动化部署工具，用于在 openEuler 系统上快速部署昇腾 CANN（Compute Architecture for Neural Networks）工具链。

该插件支持以下组件的自动化安装和卸载：
- **Toolkit 开发套件包**：提供开发和编译环境
- **Kernels 算子包**：针对不同硬件型号的算子库
- **NNAL 神经网络加速库**：支持 ATB 和 SiP 两种加速库类型
- **NNAE 神经网络加速引擎**：提供神经网络加速能力
- **NNRT 神经网络运行时环境**：提供运行时支持

## 系统要求

- **操作系统**：openEuler 24.03-LTS-SPX
- **用户权限**：root 用户或具有 sudo 权限的用户
- **网络连接**：需要访问互联网下载软件包和依赖
- **硬件支持**：支持昇腾 AI 处理器（310b/310p/910/910b/Atlas-A3）

## 配置参数

### 主要配置项

在 `config.yaml` 中可以配置以下参数：

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|---------|------|
| `hardware_model` | string | "Atlas-A3" | 硬件型号，可选：310b, 310p, 910, 910b, Atlas-A3 |
| `nnal_type` | string | "ATB" | NNAL加速库类型，可选：ATB, SiP |
| `force_install` | boolean | false | 是否强制重新安装（即使已安装） |
| `skip_env_config` | boolean | false | 是否跳过环境变量配置 |
| `verbose_logging` | boolean | true | 是否启用详细日志输出 |

### 连接配置

```yaml
all:
  hosts:
    target-host:
      ansible_host: 127.0.0.1      # 目标主机IP地址
      ansible_port: 22             # SSH端口号
      ansible_user: root           # 用户名（建议使用root用户）
      ansible_password: ""         # 密码
```

## 支持的操作

### 一键操作

- **`install`**：一键安装所有 CANN 组件
- **`uninstall`**：一键卸载所有 CANN 组件
- **`run-samples`**：下载并执行用例代码

### 单独操作

#### 安装操作
- **`sub:env-prepare`**：环境准备（安装依赖包、配置软件源）
- **`sub:install-toolkit`**：安装 Toolkit 开发套件包
- **`sub:install-kernels`**：安装 Kernels 算子包
- **`sub:install-nnal`**：安装 NNAL 神经网络加速库
- **`sub:install-nnae`**：安装 NNAE 神经网络加速引擎
- **`sub:install-nnrt`**：安装 NNRT 神经网络运行时环境

#### 卸载操作
- **`sub:uninstall-toolkit`**：卸载 Toolkit 开发套件包
- **`sub:uninstall-kernels`**：卸载 Kernels 算子包
- **`sub:uninstall-nnal`**：卸载 NNAL 神经网络加速库
- **`sub:uninstall-nnae`**：卸载 NNAE 神经网络加速引擎
- **`sub:uninstall-nnrt`**：卸载 NNRT 神经网络运行时环境
- **`sub:env-cleanup`**：环境清理

## 使用方法

### 1. 获取插件

```bash
# 下载插件包
wget https://example.com/cann-toolkit.tar.gz
tar -xzf cann-toolkit.tar.gz
cd cann-toolkit
```

### 2. 配置参数

编辑 `config.yaml` 文件，设置目标主机信息和硬件型号：

```yaml
all:
  hosts:
    target-host:
      ansible_host: 192.168.1.100  # 修改为实际IP
      ansible_user: root
      ansible_password: "your_password"
  vars:
    hardware_model: "Atlas-A3"     # 根据实际硬件修改
    nnal_type: "ATB"              # 选择加速库类型
```

### 3. 执行部署

```bash
# 一键安装所有组件
oedp run install

# 或者分步安装
oedp run sub:env-prepare          # 环境准备
oedp run sub:install-toolkit      # 安装 Toolkit
oedp run sub:install-kernels      # 安装 Kernels
oedp run sub:install-nnal          # 安装 NNAL
oedp run sub:install-nnae          # 安装 NNAE
oedp run sub:install-nnrt          # 安装 NNRT

# 执行用例代码
oedp run run-samples

# 一键卸载
oedp run uninstall
```

### 4. 验证安装

安装完成后，需要重新加载环境变量：

```bash
source /root/.bashrc
```

然后可以验证安装：

```bash
# 检查环境变量
echo $ASCEND_TOOLKIT_HOME

# 运行用例代码
oedp run run-samples
```

## 硬件型号支持

| 硬件型号 | Kernels 包名 | 说明 |
|----------|-------------|------|
| 310b | Ascend-cann-kernels-310b | 昇腾310B处理器 |
| 310p | Ascend-cann-kernels-310p | 昇腾310P处理器 |
| 910 | Ascend-cann-kernels-910 | 昇腾910处理器 |
| 910b | Ascend-cann-kernels-910b | 昇腾910B处理器 |
| Atlas-A3 | Atlas-A3-cann-kernels | Atlas A3训练卡 |

## NNAL 加速库类型

- **ATB**：Ascend Tensor Boost，昇腾张量加速库
- **SiP**：System in Package，系统级封装加速库

**注意**：ATB 和 SiP 不能同时使用，插件会自动处理冲突。

## 用例代码

插件会自动下载并执行以下用例：

1. `AddKernelInvocationNeo` - 基础算子调用示例
2. `AddKernelInvocationTilingNeo` - Tiling算子调用示例
3. `addn_kernellaunch` - 多输入加法算子示例
4. `MatmulLeakyReluInvocation` - 矩阵乘法+LeakyRelu融合算子示例
5. `MatmulInvocationNeo` - 矩阵乘法算子示例

## 环境变量

插件会自动配置以下环境变量到 `/root/.bashrc`：

```bash
# C++编译环境
export CPLUS_INCLUDE_PATH=/usr/include/c++/12:/usr/include/c++/12/backward:/usr/include/c++/12/x86_64-openEuler-linux/:$CPLUS_INCLUDE_PATH

# CANN组件环境变量
source /usr/local/Ascend/ascend-toolkit/set_env.sh
source /usr/local/Ascend/nnae/set_env.sh
source /usr/local/Ascend/nnal/atb/set_env.sh  # 或 asdsip/set_env.sh
source /usr/local/Ascend/nnrt/set_env.sh
```

## 故障排除

### 常见问题

1. **权限不足**
   - 确保使用 root 用户或具有 sudo 权限的用户
   - 检查 SSH 连接配置

2. **网络连接问题**
   - 检查网络连接
   - 确认可以访问昇腾软件源

3. **硬件型号不匹配**
   - 确认 `hardware_model` 配置正确
   - 检查硬件是否支持

4. **环境变量未生效**
   - 执行 `source /root/.bashrc` 重新加载
   - 或重新登录 bash 会话

### 日志查看

启用详细日志输出：

```yaml
vars:
  verbose_logging: true
```

### 重新安装

如需重新安装：

```yaml
vars:
  force_install: true
```

## 技术支持

如遇到问题，请检查：

1. 系统版本是否支持
2. 网络连接是否正常
3. 硬件型号配置是否正确
4. 用户权限是否足够

更多信息请参考昇腾官方文档：https://www.hiascend.com/

## 版本信息

- **插件版本**：1.0.0
- **支持的CANN版本**：8.2.RC1
- **兼容的oeDeploy版本**：1.0+

## 许可证

本插件遵循开源许可证，具体请参考相关组件的许可证条款。
