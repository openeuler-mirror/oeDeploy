# Python 科学环境插件使用指南

## 插件介绍

本插件用于在 openEuler 系统上自动部署 Python 基础科学虚拟环境，包含以下核心库：

- numpy：科学计算库
- pandas：数据处理库
- scikit-learn：机器学习库
- matplotlib：数据可视化库

同时还会安装一些常用的辅助库，如 Jupyter、Seaborn、SciPy 等。

## 支持的操作

- `install`：安装 Python 科学环境
- `uninstall`：卸载 Python 科学环境
- `status`：检查 Python 科学环境状态

## 配置说明

在 `config.yaml` 文件中可以配置以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `python_version` | Python 版本 | 3.9 |
| `venv_name` | 虚拟环境名称 | python-science-env |
| `venv_path` | 虚拟环境路径 | /opt/python-science-env |
| `install_mode` | 安装模式 (system/venv) | venv |
| `numpy_version` | numpy 版本 | latest |
| `pandas_version` | pandas 版本 | latest |
| `scikit_learn_version` | scikit-learn 版本 | latest |
| `matplotlib_version` | matplotlib 版本 | latest |
| `extra_packages` | 额外安装的包 | jupyter, ipython, seaborn, scipy, plotly |
| `download_timeout` | 下载超时时间(秒) | 600 |
| `download_retry` | 下载重试次数 | 3 |
| `pip_mirror` | pip 镜像源 | https://pypi.tuna.tsinghua.edu.cn/simple |

## 使用示例

### 安装 Python 科学环境

```bash
oedp run install
```

### 检查 Python 科学环境状态

```bash
oedp run status
```

### 卸载 Python 科学环境

```bash
oedp run uninstall
```

## 注意事项

1. 本插件需要 root 权限执行
2. 默认使用虚拟环境安装，避免影响系统 Python
3. 安装过程中会自动安装系统依赖包
4. 支持自定义 Python 库版本
5. 使用国内镜像源加速下载
6. 本插件适用于 openEuler 24.03-LTS 及以上版本

## 故障排查

- 如安装失败，请检查网络连接是否正常
- 如依赖包安装失败，请检查 pip 镜像源配置
- 如虚拟环境创建失败，请检查目录权限
- 如库版本冲突，请指定具体版本号

## 版本历史

- v1.0.0：初始版本，支持 Python 科学环境的安装和管理