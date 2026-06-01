# How to Use the Python Deep Learning Environment Plug-in

## Plugin Description

This plug-in is used to automatically deploy the Python deep learning virtual environment on openEuler. The following core libraries are included:

- torch: PyTorch deep learning framework
- torchvision: PyTorch computer vision library
- lightning: PyTorch Lightning advanced training framework

In addition, some common auxiliary libraries, such as NumPy, pandas, scikit-learn, matplotlib, Jupyter, and transformers, will be installed.

## Supported Operations

- `install`: installs the Python deep learning environment.
- `uninstall`: uninstalls the Python deep learning environment.
- `status`: checks the status of the Python deep learning environment.

## Configuration Description

Configure the following parameters in the `config.yaml` file.

| Parameter| Description| Default Value|
|------|------|--------|
| `python_version` | Python version| 3.9 |
| `venv_name` | Virtual environment name| python-deeplearning-env |
| `venv_path` | Virtual environment path| /opt/python-deeplearning-env |
| `install_mode` | Installation mode (system/venv)| venv |
| `torch_version` | PyTorch version| latest |
| `torchvision_version` | TorchVision version| latest |
| `lightning_version` | Lightning version| latest |
| `use_cuda` | Whether to use CUDA| false |
| `cuda_version` | CUDA version| 11.8 |
| `extra_packages` | Additional packages| numpy, pandas, scikit-learn, matplotlib, jupyter, ipython, seaborn, scipy, plotly, tqdm, Pillow, opencv-python, transformers, datasets, wandb |
| `download_timeout` | Download timeout (s)| 600 |
| `download_retry` | Download retry attempts| 3 |
| `pip_mirror` | pip image source| <https://pypi.tuna.tsinghua.edu.cn/simple> |
| `torch_mirror` | PyTorch image source| <https://download.pytorch.org/whl/cu118> |

## Examples

### Installing the Python Deep Learning Environment (CPU Version)

```bash
oedp run install
```

### Installing the Python Deep Learning Environment (CUDA Version)

Modify the parameters in the `config.yaml` file.

```yaml
use_cuda: true
cuda_version: "11.8"  # Adjust the value based on the CUDA version of the system.
```

Run the following command.

```bash
oedp run install
```

### Checking the Status of the Python Deep Learning Environment

```bash
oedp run status
```

### Uninstalling the Python Deep Learning Environment

```bash
oedp run uninstall
```

## Precautions

1. This plug-in requires the root permission.
2. By default, the virtual environment is used for installation to avoid affecting the system Python.
3. System dependencies are automatically installed during the installation.
4. CUDA acceleration is supported. Ensure that the CUDA of the corresponding version has been installed in the system.
5. Customized PyTorch versions are supported.
6. The image source in China is used for high-speed download.
7. This plug-in applies to openEuler 24.03-LTS and later versions.

## Troubleshooting

- If the installation fails, check whether the network connection is normal.
- If the CUDA version does not match, modify the `cuda_version` parameter.
- If the dependency package fails to be installed, check the pip image source configuration.
- If the virtual environment fails to be created, check the directory permission.
- If the memory is insufficient, increase the system memory or use a smaller model.

## Version History

- v1.0.0: initial version, which supports the installation and management of the Python deep learning environment.
