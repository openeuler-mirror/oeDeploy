# How to Use the Python Science Environment Plug-in

## Plugin Description

This plug-in is used to automatically deploy the Python basic science virtual environment on openEuler. The following core libraries are included:

- numpy: scientific computing library
- pandas: data processing library
- scikit-learn: machine learning library
- matplotlib: data visualization library

In addition, some common auxiliary libraries, such as Jupyter, Seaborn, and SciPy, will be installed.

## Supported Operations

- `install`: installs the Python science environment.
- `uninstall`: uninstalls the Python science environment.
- `status`: checks the status of the Python science environment.

## Configuration Description

Configure the following parameters in the `config.yaml` file.

| Parameter| Description| Default Value|
|------|------|--------|
| `python_version` | Python version| 3.9 |
| `venv_name` | Virtual environment name| python-science-env |
| `venv_path` | Virtual environment path| /opt/python-science-env |
| `install_mode` | Installation mode (system/venv)| venv |
| `numpy_version` | NumPy version| latest |
| `pandas_version` | Pandas version| latest |
| `scikit_learn_version` | Scikit-learn version| latest |
| `matplotlib_version` | Matplotlib version| latest |
| `extra_packages` | Additional packages| jupyter, ipython, seaborn, scipy, plotly |
| `download_timeout` | Download timeout (s)| 600 |
| `download_retry` | Download retry attempts| 3 |
| `pip_mirror` | pip image source| <https://pypi.tuna.tsinghua.edu.cn/simple> |

## Example

### Installing the Python Science Environment

```bash
oedp run install
```

### Checking the Status of the Python Science Environment

```bash
oedp run status
```

### Uninstalling the Python Science Environment

```bash
oedp run uninstall
```

## Precautions

1. This plug-in requires the root permission.
2. By default, the virtual environment is used for installation to avoid affecting the system Python.
3. System dependencies are automatically installed during the installation.
4. Customized Python library versions are supported.
5. The image source in China is used for high-speed download.
6. This plug-in applies to openEuler 24.03-LTS and later versions.

## Troubleshooting

- If the installation fails, check whether the network connection is normal.
- If the dependency package fails to be installed, check the pip image source configuration.
- If the virtual environment fails to be created, check the directory permission.
- If a library version conflict occurs, specify the version number.

## Version History

- v1.0.0: initial version, which supports the installation and management of the Python science environment.
