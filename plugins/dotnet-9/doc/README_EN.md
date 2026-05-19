# How to Use the dotnet-9 Plug-in

## Example of Quick Deployment of .NET 9

1. Prepare the target node. The OS version is openEuler 25.09.

2. Obtain and initialize the `dotnet-9` plug-in.

    ```shell
    oedp repo update
    oedp init dotnet-9
    ```

3. Run the `info` command to view the plug-in details.

    ```shell
    oedp info -p dotnet-9
    ```

4. Modify the project configuration file and configure the node information based on site requirements.

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
        
        # .NET 9 Configuration
        dotnet9_repo_url: "https://repo.oepkgs.net/openeuler/rpm/openEuler-25.09/contrib/dotnet/$basearch/"
        
        # Environment type (production/development)
        environment_type: "development"
    ````

5. Run the following commands to start automatic installation.

    ```shell
    oedp run install -p dotnet-9
    ```

6. Run the following command to uninstall .NET 9.

    ```shell
    oedp run uninstall -p dotnet-9
    ```

    > -The `p` parameter indicates the directory where the oeDeploy project is located.

## Configuring the Environment

### Production

In the production environment, only the core components are installed, including:

- dotnet-host
- dotnet-hostfxr
- dotnet-runtime
- aspnetcore-runtime

### Development

The development environment contains a complete development tool chain and the following additional components:

- dotnet-sdk
- dotnet-targeting-pack
- aspnetcore-targeting-pack
- dotnet-templates
- Debugging packages and development tools

### Switching the Environment

Modify the `environment_type` variable in the `config.yaml` file:

- `production`: production environment
- `development`: development environment

## Verify the Installation

After the installation is complete, run the following command to verify the .NET 9 installation.

```bash
dotnet --version
dotnet --info
```

## Technical Support

If you have any questions, refer to the following documents:

- [.NET 9 official documentation](https://learn.microsoft.com/en-us/dotnet/fundamentals/)
- [openEuler .NET support](https://atomgit.com/src-openeuler/dotnet)

## Release Notes

This plug-in is built based on the `.NET 9` software package of openEuler 25.09. The version information is as follows:

- .NET SDK: 9.0.109
- .NET Runtime: 9.0.8
- ASP.NET Core Runtime: 9.0.8
