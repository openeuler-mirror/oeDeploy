# MonoDevelop 插件

这是一个用于在 openEuler 系统上安装和管理 MonoDevelop IDE 的 oeDeploy 插件。

## 功能特性

- 一键安装 MonoDevelop IDE
- 支持卸载 MonoDevelop
- 自动配置官方软件源

## 系统要求

- openEuler 20.03-LTS-SPx 版本
- 桌面环境(ukui或deepin)
- 规格大于4U8G

## 安装桌面(以UKUI为例，需要提前手动执行)

1. 更新软件包命令： `sudo dnf update` 
2. 运行桌面安装命令：`sudo dnf install ukui`
3. 启用图形化界面方式启动： `systemctl set-default graphical.target`
4. 重启机器

## 安装步骤

1. 配置主机信息在 `config.yaml` 中
2. 运行安装命令：`oedp run monodevelop install`

## 卸载步骤

运行卸载命令：`oedp run monodevelop uninstall`

## 配置说明

在 `config.yaml` 中配置目标主机信息：

```yaml
monodevelop_hosts:
  hosts:
    your_host_ip:
      ansible_host: your_host_ip
      ansible_port: 22
      ansible_user: root
      ansible_password: ""
      architecture: amd64               # [amd64, arm64]
      oeversion: 20.03-LTS-SP4
```

## 注意事项

- 需要 root 权限执行安装
- 确保网络连接正常以访问软件源
- 安装过程会自动添加官方 MonoDevelop 软件源

## 版本信息

- 当前版本：1.0.0
- 更新时间：2025-08-20