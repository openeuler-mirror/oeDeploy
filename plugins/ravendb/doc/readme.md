# RavenDB 插件使用指南

## 插件介绍

本插件用于在 openEuler 系统上自动部署和管理 RavenDB 数据库。支持以下功能：

- 自动安装 RavenDB
- 配置 RavenDB 服务
- 管理 RavenDB 服务（启动、停止、查看状态）
- 卸载 RavenDB

## 支持的操作

- `install`：安装并配置 RavenDB
- `uninstall`：卸载 RavenDB
- `start`：启动 RavenDB 服务
- `stop`：停止 RavenDB 服务
- `status`：查看 RavenDB 服务状态

## 配置说明

在 `config.yaml` 文件中可以配置以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `ravendb_version` | RavenDB 版本 | 6.0 |
| `ravendb_install_path` | RavenDB 安装路径 | /usr/local/ravendb |
| `ravendb_data_path` | RavenDB 数据目录 | /var/lib/ravendb |
| `ravendb_log_path` | RavenDB 日志目录 | /var/log/ravendb |
| `ravendb_port` | RavenDB HTTP 端口 | 8080 |
| `ravendb_management_port` | RavenDB 管理端口 | 38888 |
| `ravendb_bind_ip` | RavenDB 绑定地址 | 127.0.0.1 |
| `ravendb_user` | RavenDB 用户 | ravendb |
| `ravendb_password` | RavenDB 密码 | ****** |
| `ravendb_cluster_name` | RavenDB 集群名称 | RavenDB-Cluster |
| `download_timeout` | 下载超时时间(秒) | 600 |
| `download_retry` | 下载重试次数 | 3 |
| `install_mode` | 安装模式 (direct) | direct |
| `enable_auth` | 是否开启认证 | false |

## 使用示例

### 安装 RavenDB

```bash
oedp run install
```

### 启动 RavenDB 服务

```bash
oedp run start
```

### 停止 RavenDB 服务

```bash
oedp run stop
```

### 查看 RavenDB 服务状态

```bash
oedp run status
```

### 卸载 RavenDB

```bash
oedp run uninstall
```

## 注意事项

1. 本插件需要 root 权限执行
2. RavenDB 需要 Java 11 环境，插件会自动安装
3. 默认从 RavenDB 官方网站下载安装包
4. 安装完成后，RavenDB 服务会自动启动并设置为开机自启
5. 访问地址：http://localhost:8080
6. 本插件适用于 openEuler 24.03-LTS 及以上版本

## 故障排查

- 如安装失败，请检查网络连接是否正常
- 如服务启动失败，请查看 `/var/log/ravendb` 目录下的日志
- 如端口被占用，请修改 `config.yaml` 中的端口参数
- 如 Java 环境问题，请确保 Java 11 已正确安装

## 版本历史

- v1.0.0：初始版本，支持 RavenDB 6.0 安装和管理