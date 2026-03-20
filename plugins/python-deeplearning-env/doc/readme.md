# Python 深度学习环境插件使用指南

## 插件介绍

本插件用于在 openEuler 系统上自动部署 Python 深度学习虚拟环境，包含以下核心库：

- torch：PyTorch 深度学习框架
- torchvision：PyTorch 计算机视觉库
- lightning：PyTorch Lightning 高级训练框架

同时还会安装一些常用的辅助库，如 numpy、pandas、scikit-learn、matplotlib、Jupyter、transformers 等。

## 支持的操作

- `install`：安装 Python 深度学习环境
- `uninstall`：卸载 Python 深度学习环境
- `status`：检查 Python 深度学习环境状态

## 配置说明

在 `config.yaml` 文件中可以配置以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `python_version` | Python 版本 | 3.9 |
| `venv_name` | 虚拟环境名称 | python-deeplearning-env |
| `venv_path` | 虚拟环境路径 | /opt/python-deeplearning-env |
| `install_mode` | 安装模式 (system/venv) | venv |
| `torch_version` | PyTorch 版本 | latest |
| `torchvision_version` | TorchVision 版本 | latest |
| `lightning_version` | Lightning 版本 | latest |
| `use_cuda` | 是否使用 CUDA | false |
| `cuda_version` | CUDA 版本 | 11.8 |
| `extra_packages` | 额外安装的包 | numpy, pandas, scikit-learn, matplotlib, jupyter, ipython, seaborn, scipy, plotly, tqdm, Pillow, opencv-python, transformers, datasets, wandb |
| `download_timeout` | 下载超时时间(秒) | 600 |
| `download_retry` | 下载重试次数 | 3 |
| `pip_mirror` | pip 镜像源 | https://pypi.tuna.tsinghua.edu.cn/simple |
| `torch_mirror` | PyTorch 镜像源 | https://download.pytorch.org/whl/cu118 |

## 使用示例

### 安装 Python 深度学习环境（CPU版本）

```bash
oedp run install
```

### 安装 Python 深度学习环境（CUDA版本）

修改 `config.yaml` 文件：
```yaml
use_cuda: true
cuda_version: "11.8"  # 根据系统CUDA版本调整
```

然后执行：
```bash
oedp run install
```

### 检查 Python 深度学习环境状态

```bash
oedp run status
```

### 卸载 Python 深度学习环境

```bash
oedp run uninstall
```

## 注意事项

1. 本插件需要 root 权限执行
2. 默认使用虚拟环境安装，避免影响系统 Python
3. 安装过程中会自动安装系统依赖包
4. 支持 CUDA 加速，需要系统已安装对应版本的 CUDA
5. 支持自定义 PyTorch 版本
6. 使用国内镜像源加速下载
7. 本插件适用于 openEuler 24.03-LTS 及以上版本

## 故障排查

- 如安装失败，请检查网络连接是否正常
- 如 CUDA 版本不匹配，请修改 `cuda_version` 参数
- 如依赖包安装失败，请检查 pip 镜像源配置
- 如虚拟环境创建失败，请检查目录权限
- 如内存不足，请增加系统内存或使用较小的模型

## 版本历史

- v1.0.0：初始版本，支持 Python 深度学习环境的安装和管理