# Ascend Driver Manager

## 插件简介

Ascend Driver Manager 是一个用于管理昇腾NPU驱动和固件的oeDeploy插件。该插件支持310p和910b芯片的驱动和固件的自动化安装、卸载和状态查询。

## 支持的硬件和版本

### 310p芯片
- 25.0.rc1.1
- 25.2.0

### 910b芯片
- 25.0.rc1.1
- 25.2.0
- 25.3.rc1

## 功能特性

- **自动化安装**: 自动下载并安装指定版本的驱动和固件
- **智能检测**: 自动检测系统架构（x86-64/aarch64）和虚拟化环境
- **版本验证**: 验证用户配置的硬件型号和版本号的合法性
- **状态查询**: 提供详细的驱动、固件和NPU状态信息
- **完整卸载**: 支持驱动、固件的完整卸载和环境清理

## 使用方法

### 1. 配置参数

编辑 `config.yaml` 文件，配置以下参数：

```yaml
all:
  hosts:
    target-host:
      ansible_host: 127.0.0.1      # 目标主机IP
      ansible_port: 22             # SSH端口号
      ansible_user: root           # 必须使用root用户
      ansible_password: ""         # root用户密码
  vars:
    chip_type: 310p                # 硬件型号: 310p 或 910b
    version: 25.2.0                # 版本号
    file_server_url: https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/Ascend/
    download_path: /tmp/ascend      # 下载路径
    download_checksum: false        # 是否启用SHA256校验(需要文件服务器支持)
    download_timeout: 600           # 下载超时时间(秒)
    download_retry: 3               # 下载重试次数
```

### 2. 安装驱动和固件

```bash
oedp run install
```

安装过程包括：
1. 验证配置参数
2. 安装依赖软件包
3. 创建用户和组
4. 下载并安装驱动
5. 检测物理机环境并安装固件（虚拟机跳过）

### 3. 卸载驱动和固件

```bash
oedp run uninstall
```

卸载过程包括：
1. 卸载固件
2. 卸载驱动
3. 清理用户、组和临时文件

### 4. 查询状态

```bash
oedp run status
```

状态查询包括：
- 驱动和固件安装状态
- 用户和组存在状态
- DKMS状态信息
- NPU-SMI设备信息

## 配置说明

### 必需配置

- `chip_type`: 硬件型号，支持 `310p` 和 `910b`
- `version`: 版本号，不同芯片支持的版本不同
- `ansible_host`: 目标主机IP地址
- `ansible_user`: 必须为 `root`
- `ansible_password`: root用户密码

### 可选配置

- `file_server_url`: 文件服务器地址，默认为华为云镜像源
- `download_path`: 下载文件存储路径，默认为 `/tmp/ascend`
- `download_checksum`: 是否启用SHA256校验，默认为 `false`，开启需要文件服务器支持
- `download_timeout`: 下载超时时间，默认为 600 秒
- `download_retry`: 下载重试次数，默认为 3 次

### 系统用户和组

插件会自动创建和管理以下系统用户和组：
- **用户**: `HwHiAiUser`
- **组**: `HwHiAiUser`  
- **用户主目录**: `/home/HwHiAiUser`

这些配置已在代码中固定，无需用户配置。

## 注意事项

1. **用户权限**: 必须使用root用户执行，因为需要安装系统软件包和内核模块
2. **网络连接**: 需要能够访问文件服务器下载run包
3. **虚拟机环境**: 在虚拟机中会自动跳过固件安装，这是正常行为
4. **重复安装**: 插件会自动检测已安装的组件，避免重复安装

## 故障排除

### 下载失败
- 检查网络连接
- 验证文件服务器地址是否正确
- 增加重试次数或延长超时时间

### 安装失败
- 确保使用root用户
- 检查系统是否安装了必需的依赖包
- 查看安装日志中的错误信息

### 状态查询异常
- 确保驱动已正确安装
- 检查NPU设备是否正常识别
- 验证DKMS模块状态
