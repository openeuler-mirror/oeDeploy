# MonoDevelop Plug-in

This is an oeDeploy plug-in used to install and manage the MonoDevelop IDE on openEuler.

## Functions

- One-click installation of the MonoDevelop IDE
- MonoDevelop uninstallation
- Automatic configuration of official software sources

## System Requirements

- openEuler 20.03-LTS-SPx
- Desktop environment (UKUI or Deepin)
- Specifications greater than 4U8G

## Install the desktop (UKUI is used as an example and needs to be manually executed in advance)

1. Run the `sudo dnf update` command to update the software package.
2. Run the `sudo dnf install ukui` command to install the desktop.
3. Run the `systemctl set-default graphical.target` command to enable GUI startup.
4. Restart the system.

## Installation Procedure

1. Configure the host information in the `config.yaml` file.
2. Run the `oedp run monodevelop install` command to install the software.

## Uninstallation Procedure

Run the `oedp run monodevelop uninstall` command to uninstall the software.

## Configuration Description

Configure the target host information in the `config.yaml`.

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

## Precautions

- The root permission is required for installation.
- Ensure that the network connection is normal to access the software source.
- The official MonoDevelop software source will be automatically added during the installation.

## Version Information

- Current version: 1.0.0
- Updated on: 2025-08-20
