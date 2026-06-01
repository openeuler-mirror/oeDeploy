# Ascend Driver Manager

## Plugin Introduction

Ascend Driver Manager is an oeDeploy plugin used to manage the Ascend NPU driver and firmware. This plugin supports automatic installation, uninstallation, and status query of the driver and firmware of the 310P and 910B chips.

## Supported Hardware and Versions

### 310P Chip

- 25.0.rc1.1
- 25.2.0

### 910B Chip

- 25.0.rc1.1
- 25.2.0
- 25.3.rc1

## Functions

- **Automatic installation**: Automatically download and install the driver and firmware of a specified version.
- **Intelligent detection**: Automatically detect the system architecture (x86-64/AArch64) and virtualization environment.
- **Version verification**: Verify the validity of the hardware model and version number configured by the user.
- **Status query**: Provide detailed information about the driver, firmware, and NPU status.
- **Complete uninstallation**: Uninstall the driver and firmware completely and clean up the environment.

## How to Use

### 1. Configuring Parameters

Edit the `config.yaml` file and set the following parameters:

```yaml
all:
  hosts:
    target-host:
      ansible_host: 127.0.0.1      # IP address of the target host
      ansible_port: 22             # SSH port number
      ansible_user: root           # The root user must be used.
      ansible_password: ""         # password of the root user
  vars:
    chip_type: 310p                # hardware models: 310P or 910B
    version: 25.2.0                # version number
    file_server_url: https://repo.oepkgs.net/openEuler/rpm/openEuler-24.03-LTS/contrib/oedp/files/Ascend/
    download_path: /tmp/ascend      # download path
    download_checksum: false        # whether to enable SHA256 verification (requiring the support of the file server)
    download_timeout: 600           # download timeout interval (s)
    download_retry: 3               # number of download retry attempts
```

### 2. Installing the Driver and Firmware

```bash
oedp run install
```

The installation process is as follows:

1. Verify configuration parameters.
2. Install the dependency software package.
3. Create users and user groups.
4. Download and install the driver.
5. Check the physical machine environment and install the firmware. (Skip this step for VMs.)

### 3. Uninstalling the Driver and Firmware

```bash
oedp run uninstall
```

The uninstallation process is as follows:

1. Uninstall the firmware.
2. Uninstall the driver.
3. Delete users, groups, and temporary files.

### 4. Querying the Statuses

```bash
oedp run status
```

The status query includes:

- Driver and firmware installation status
- User and group existence status
- DKMS status
- NPU-SMI device information

## Configuration Description

### Mandatory

- `chip_type`: hardware model. The value can be `310p` or `910b`.
- `version`: version number. Different chips support different versions.
- `ansible_host`: IP address of the target host.
- `ansible_user`: The value must be `root`.
- `ansible_password`: root user password

### Optional Configurations

- `file_server_url`: address of the file server. The default value is the Huawei Cloud image source.
- `download_path`: path for storing downloaded files. The default value is `/tmp/ascend`.
- `download_checksum`: Whether to enable SHA256 verification. The default value is `false`. To enable this function, the file server must support it.
- `download_timeout`: download timeout interval. The default value is 600 seconds.
- `download_retry`: number of download retry times. The default value is 3.

### System Users and Groups

The plugin automatically creates and manages the following system users and groups:

- **User**: `HwHiAiUser`
- **Group**: `HwHiAiUser` 
- **Home directory**: `/home/HwHiAiUser`

These configurations are fixed in the code and do not need to be configured by users.

## Precautions

1. **User permission**: The root user must be used to install the system software package and kernel module.
2. **Network connection**: The file server must be accessible to download the `.run` package.
3. **VM environment**: Firmware installation is automatically skipped on a VM, which is normal.
4. **Repeated installation**: The plug-in automatically detects installed components to avoid repeated installation.

## Troubleshooting

### Download Failure

- Check the network connection.
- Check whether the file server address is correct.
- Increase the number of retry times or extend the timeout interval.

### Installation Failure

- Ensure that the root user is used.
- Check whether the required dependency packages are installed.
- Check the error information in the installation log.

### Status Query Exception

- Ensure that the driver has been correctly installed.
- Check whether the NPU device can be identified.
- Verify the DKMS module status.
