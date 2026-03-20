# Python NLP 环境插件使用指南

## 插件介绍

本插件用于在 openEuler 系统上自动部署 Python NLP（自然语言处理）虚拟环境，包含以下核心库：

- spaCy：工业级NLP库
- NLTK：自然语言处理工具包
- Gensim：主题建模和文档相似度库
- Transformers：Hugging Face的预训练模型库

同时还会安装一些常用的辅助库，如 numpy、pandas、scikit-learn、matplotlib、Jupyter、sentence-transformers 等。

## 支持的操作

- `install`：安装 Python NLP 环境
- `uninstall`：卸载 Python NLP 环境
- `status`：检查 Python NLP 环境状态

## 配置说明

在 `config.yaml` 文件中可以配置以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `python_version` | Python 版本 | 3.9 |
| `venv_name` | 虚拟环境名称 | python-nlp-env |
| `venv_path` | 虚拟环境路径 | /opt/python-nlp-env |
| `install_mode` | 安装模式 (system/venv) | venv |
| `spacy_version` | spaCy 版本 | latest |
| `nltk_version` | NLTK 版本 | latest |
| `gensim_version` | Gensim 版本 | latest |
| `transformers_version` | Transformers 版本 | latest |
| `download_resources` | 是否下载NLP资源 | true |
| `extra_packages` | 额外安装的包 | numpy, pandas, scikit-learn, matplotlib, jupyter, ipython, seaborn, scipy, plotly, tqdm, Pillow, opencv-python, datasets, tokenizers, sentence-transformers, pyarrow, fasttext, textblob, wordcloud, pattern |
| `download_timeout` | 下载超时时间(秒) | 600 |
| `download_retry` | 下载重试次数 | 3 |
| `pip_mirror` | pip 镜像源 | https://pypi.tuna.tsinghua.edu.cn/simple |

## 使用示例

### 安装 Python NLP 环境

```bash
oedp run install
```

### 检查 Python NLP 环境状态

```bash
oedp run status
```

### 卸载 Python NLP 环境

```bash
oedp run uninstall
```

## 注意事项

1. 本插件需要 root 权限执行
2. 默认使用虚拟环境安装，避免影响系统 Python
3. 安装过程中会自动安装系统依赖包
4. 默认会下载 NLP 资源（如 spaCy 模型和 NLTK 数据包）
5. 支持自定义 NLP 库版本
6. 使用国内镜像源加速下载
7. 本插件适用于 openEuler 24.03-LTS 及以上版本

## 故障排查

- 如安装失败，请检查网络连接是否正常
- 如资源下载失败，请检查网络连接或设置 `download_resources: false`
- 如依赖包安装失败，请检查 pip 镜像源配置
- 如虚拟环境创建失败，请检查目录权限
- 如内存不足，请增加系统内存

## 版本历史

- v1.0.0：初始版本，支持 Python NLP 环境的安装和管理