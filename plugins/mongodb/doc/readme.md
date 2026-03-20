# MongoDB 插件使用指南

## 插件介绍

本插件用于在 openEuler 系统上自动部署和管理 MongoDB 数据库。支持以下功能：

- 自动安装 MongoDB
- 配置 MongoDB 服务
- 管理 MongoDB 服务（启动、停止、查看状态）
- 卸载 MongoDB

## 支持的操作

- `install`：安装并配置 MongoDB
- `uninstall`：卸载 MongoDB
- `start`：启动 MongoDB 服务
- `stop`：停止 MongoDB 服务
- `status`：查看 MongoDB 服务状态

## 配置说明

在 `config.yaml` 文件中可以配置以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `mongodb_version` | MongoDB 版本 | 7.0 |
| `mongodb_install_path` | MongoDB 安装路径 | /usr/local/mongodb |
| `mongodb_data_path` | MongoDB 数据目录 | /var/lib/mongodb |
| `mongodb_log_path` | MongoDB 日志目录 | /var/log/mongodb |
| `mongodb_port` | MongoDB 端口 | 27017 |
| `mongodb_bind_ip` | MongoDB 绑定地址 | 127.0.0.1 |
| `mongodb_user` | MongoDB 用户 | mongodb |
| `mongodb_password` | MongoDB 密码 | ****** |
| `mongodb_database` | MongoDB 数据库 | admin |
| `download_timeout` | 下载超时时间(秒) | 600 |
| `download_retry` | 下载重试次数 | 3 |
| `install_mode` | 安装模式 (repo/source) | repo |
| `enable_auth` | 是否开启认证 | false |

## 使用示例

### 安装 MongoDB

```bash
oedp run install
```

### 启动 MongoDB 服务

```bash
oedp run start
```

### 停止 MongoDB 服务

```bash
oedp run stop
```

### 查看 MongoDB 服务状态

```bash
oedp run status
```

### 卸载 MongoDB

```bash
oedp run uninstall
```

## 注意事项

1. 本插件需要 root 权限执行
2. 默认安装模式为从 MongoDB 官方仓库安装
3. 如需开启认证，请在 `config.yaml` 中设置 `enable_auth: true`
4. 安装完成后，MongoDB 服务会自动启动并设置为开机自启
5. 本插件适用于 openEuler 24.03-LTS 及以上版本

## 故障排查

- 如安装失败，请检查网络连接是否正常
- 如服务启动失败，请查看 `/var/log/mongodb/mongod.log` 日志
- 如端口被占用，请修改 `config.yaml` 中的 `mongodb_port` 参数

## 版本历史

- v1.0.0：初始版本，支持 MongoDB 7.0 安装和管理