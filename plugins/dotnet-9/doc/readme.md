# dotnet-9 插件使用说明

## .NET 9 一键部署操作示例

1. 准备目标节点，OS 版本为 openEuler 25.09。

2. 获取并初始化`dotnet-9`插件。
    ```shell
    oedp repo update
    oedp init dotnet-9
    ```

3. 执行`info`命令以查看插件详细信息：
    ```shell
    oedp info -p dotnet-9
    ```

4. 修改项目配置文件，根据实际情况配置节点信息：
    ```shell
    vim dotnet-9/config.yaml
    ```

    ````yaml
    all:
      children:
        dotnet9_hosts:
          hosts:
            HOST_IP:
              ansible_host: 192.168.137.1
              ansible_port: 22
              ansible_user: root
              ansible_password: ""
              architecture: amd64
              oeversion: 25.09
      vars:
        ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
        
        # .NET 9 相关配置
        dotnet9_repo_url: "https://repo.oepkgs.net/openeuler/rpm/openEuler-25.09/contrib/dotnet/$basearch/"
        
        # 环境类型（production/development）
        environment_type: "development"
    ````

5. 执行以下命令以开始自动化安装：
    ```shell
    oedp run install -p dotnet-9
    ```

6. 执行以下命令以卸载.NET 9：
    ```shell
    oedp run uninstall -p dotnet-9
    ```

    > -p 参数表示 oeDeploy 项目所在目录

## 环境配置说明

### 生产环境
生产环境只安装运行时核心组件，包括：
- dotnet-host
- dotnet-hostfxr  
- dotnet-runtime
- aspnetcore-runtime

### 开发环境
开发环境包含完整的开发工具链，额外包括：
- dotnet-sdk
- dotnet-targeting-pack
- aspnetcore-targeting-pack
- dotnet-templates
- 调试包和开发工具

### 切换环境类型
在 `config.yaml` 中修改 `environment_type` 变量：
- `production`: 生产环境
- `development`: 开发环境

## 验证安装

安装完成后，可以通过以下命令验证.NET 9安装：
```bash
dotnet --version
dotnet --info
```

## 技术支持

如有问题，请参考：
- [.NET 9 官方文档](https://learn.microsoft.com/zh-cn/dotnet/core/)
- [OpenEuler .NET 支持](https://atomgit.com/src-openeuler/dotnet)

## 版本说明

本插件基于 OpenEuler 25.09 的 .NET 9 软件包构建，版本信息：
- .NET SDK: 9.0.109
- .NET Runtime: 9.0.8
- ASP.NET Core Runtime: 9.0.8