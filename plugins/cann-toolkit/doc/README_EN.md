# CANN Toolkit One-Click Deployment Plugin

## Plugin Introduction

It is an automatic deployment tool developed based on the oeDeploy framework. It is used to quickly deploy the Ascend Compute Architecture for Neural Networks (CANN) toolchain on openEuler.

This plugin supports automatic installation and uninstallation of the following components:

- **Toolkit**: provides development and compilation environment.
- **Kernels operator package**: operator libraries for different hardware models
- **NNAL**: supports two types of acceleration libraries: ATB and SiP.
- **NNAE**: provides neural network acceleration capabilities.
- **NNRT**: provides runtime support.

## System Requirements

- **OS**: openEuler 24.03-LTS-SPX
- **User permission**: root user or user with the sudo permission
- **Network connection**: Internet access for downloading software packages and dependencies
- **Hardware support**: Ascend AI Processors (310b/310p/910/910b/Atlas-A3)

## Configuration Parameters

### Main Configuration Items

Configure the following parameters in the `config.yaml` file.

| Parameter| Type| Default Value| Description|
|--------|------|---------|------|
| `hardware_model` | string | "Atlas-A3" | Hardware model. The options are 310b, 310p, 910, 910b, and Atlas-A3.|
| `nnal_type` | string | "ATB" | NNAL acceleration library type. The options are ATB and SiP.|
| `force_install` | boolean | false | Whether to forcibly reinstall the software (even if the software has been installed)|
| `skip_env_config` | boolean | false | Whether to skip environment variable configuration|
| `verbose_logging` | boolean | true | Whether to enable detailed log output|

### Connection Configuration

```yaml
all:
  hosts:
    target-host:
      ansible_host: 127.0.0.1      # IP address of the target host
      ansible_port: 22             # SSH port number
      ansible_user: root           # username (root is recommended)
      ansible_password: ""         # password
```

## Supported Operations

### One-Click Operations

- **`install`**: Install all CANN components in one-click mode.
- **`uninstall`**: Uninstall all CANN components in one-click mode.
- **`run-samples`**: Download and execute the test case code.

### Independent Operations

## Installation

- **`sub:env-prepare`**: Prepare the environment (install the dependency package and configure the software source).
- **`sub:install-toolkit`**: Install the Toolkit development kit.
- **`sub:install-kernels`**: Install the kernels operator package.
- **`sub:install-nnal`**: Install the NNAL.
- **`sub:install-nnae`**: Install the NNAE.
- **`sub:install-nnrt`**: Install the NNRT.

## Uninstallation

- **`sub:uninstall-toolkit`**: Uninstall the Toolkit.
- **`sub:uninstall-kernels`**: Uninstall the kernels operator package.
- **`sub:uninstall-nnal`**: Uninstall the NNAL.
- **`sub:uninstall-nnae`**: Uninstall the NNAE.
- **`sub:uninstall-nnrt`**: Uninstall the NNRT.
- **`sub:env-cleanup`**: Clear the environment.

## How to Use

### 1. Obtaining the Plugin

```bash
# Download the plugin package.
wget https://example.com/cann-toolkit.tar.gz
tar -xzf cann-toolkit.tar.gz
cd cann-toolkit
```

### 2. Configuring Parameters

Edit the `config.yaml` file to set the target host information and hardware model.

```yaml
all:
  hosts:
    target-host:
      ansible_host: 192.168.1.100 # Change it to the actual IP address.
      ansible_user: root
      ansible_password: "your_password"
  vars:
    hardware_model: "Atlas-A3"     # Change it based on the actual hardware.
    nnal_type: "ATB"              # Select the acceleration library type.
```

### 3. Performing the Deployment

```bash
# Install all components in one-click mode.
oedp run install

# Perform step-by-step installation.
oedp run sub:env-prepare          # Prepare the environment.
oedp run sub:install-toolkit      # Install the Toolkit.
oedp run sub:install-kernels      # Install the kernels.
oedp run sub:install-nnal          # Install the NNAL.
oedp run sub:install-nnae          # Install the NNAE.
oedp run sub:install-nnrt          # Install the NNRT.

# Execute the sample code.
oedp run run-samples

# Perform one-click uninstallation.
oedp run uninstall
```

### 4. Verifying the Installation

After the installation is complete, reload the environment variables.

```bash
source /root/.bashrc
```

Then, verify the installation.

```bash
# Check environment variables.
echo $ASCEND_TOOLKIT_HOME

# Execute the sample code.
oedp run run-samples
```

## Supported Hardware Models

| Hardware Model| Kernel Package Name| Description|
|----------|-------------|------|
| 310b | Ascend-cann-kernels-310b | Ascend 310B Processor|
| 310p | Ascend-cann-kernels-310p | Ascend 310P Processor|
| 910 | Ascend-cann-kernels-910 | Ascend 910 Processor|
| 910b | Ascend-cann-kernels-910b | Ascend 910B Processor|
| Atlas-A3 | Atlas-A3-cann-kernels | Atlas A3 training card|

## NNAL Acceleration Library Type

- **ATB**: Ascend Tensor Boost, the Ascend tensor acceleration library
- **SiP**: System in Package, the system-in-package acceleration library

**Note**: ATB and SiP cannot be used at the same time. The plugin automatically handles the conflict.

## Case Code

The plugin automatically downloads and executes the following cases:

1. `AddKernelInvocationNeo` - Basic operator calling example
2. `AddKernelInvocationTilingNeo` - Tiling operator calling example
3. `addn_kernellaunch` - multi-input addition operator example
4. `MatmulLeakyReluInvocation` - matrix multiplication + LeakyRelu fusion operator example
5. `MatmulInvocationNeo` - matrix multiplication operator example

## Environment Variables

The plugin automatically configures the following environment variables to `/root/.bashrc`:

```bash
# C++ compilation environment
export CPLUS_INCLUDE_PATH=/usr/include/c++/12:/usr/include/c++/12/backward:/usr/include/c++/12/x86_64-openEuler-linux/:$CPLUS_INCLUDE_PATH

# CANN component environment variables
source /usr/local/Ascend/ascend-toolkit/set_env.sh
source /usr/local/Ascend/nnae/set_env.sh
source /usr/local/Ascend/nnal/atb/set_env.sh # or asdsip/set_env.sh
source /usr/local/Ascend/nnrt/set_env.sh
```

## Troubleshooting

### FAQ

1. **Insufficient permissions**
   - Ensure that the root user or a user with the sudo permission is used.
   - Check the SSH connection configuration.

2. **Network connection issues**
   - Check the network connection.
   - Ensure that the Ascend software source can be accessed.

3. **Hardware model mismatch**
   - Ensure that the `hardware_model` configuration is correct.
   - Check whether the hardware is supported.

4. **Ineffective environment variables**
   - Run the `source /root/.bashrc` command for reloading.
   - Re-log in to the bash session.

### Viewing Logs

Enable detailed log output:

```yaml
vars:
  verbose_logging: true
```

### Reinstallation

If reinstallation is required:

```yaml
vars:
  force_install: true
```

## Technical Support

If any issues occur, check the following:

1. System version
2. Network connection
3. Hardware model configuration
4. User permission

For more information, see the Ascend official documents at https://www.hiascend.com/.

## Versions

- **Plugin version**: 1.0.0
- **Supported CANN version**: 8.2.RC1
- **Compatible oeDeploy version**: 1.0+

## License

This plugin complies with the open source license. For details, see the license terms of related components.
