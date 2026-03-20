# Python LLM 应用环境插件使用指南

## 插件介绍

本插件用于在 openEuler 系统上自动部署 Python LLM（大语言模型）应用虚拟环境，包含以下核心库：

- LangChain：LLM应用开发框架
- OpenAI：OpenAI API客户端
- LlamaIndex：数据索引和检索框架

同时还会安装一些常用的辅助库，如 numpy、pandas、transformers、sentence-transformers、chromadb、faiss-cpu 等，以及文档处理、向量数据库、数据库连接等相关依赖。

## 支持的操作

- `install`：安装 Python LLM 环境
- `uninstall`：卸载 Python LLM 环境
- `status`：检查 Python LLM 环境状态

## 配置说明

在 `config.yaml` 文件中可以配置以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `python_version` | Python 版本 | 3.9 |
| `venv_name` | 虚拟环境名称 | python-llm-env |
| `venv_path` | 虚拟环境路径 | /opt/python-llm-env |
| `install_mode` | 安装模式 (system/venv) | venv |
| `langchain_version` | LangChain 版本 | latest |
| `openai_version` | OpenAI 版本 | latest |
| `llama_index_version` | LlamaIndex 版本 | latest |
| `extra_packages` | 额外安装的包 | numpy, pandas, scikit-learn, matplotlib, jupyter, ipython, seaborn, scipy, plotly, tqdm, Pillow, opencv-python, transformers, datasets, tokenizers, sentence-transformers, pyarrow, fasttext, textblob, wordcloud, pattern, requests, beautifulsoup4, lxml, pymupdf, pypdf, docx2txt, python-docx, unstructured, chromadb, faiss-cpu, pinecone-client, weaviate-client, redis, pymongo, psycopg2-binary, sqlalchemy, pydantic, pydantic-settings, rich, click, colorama, python-dotenv |
| `download_timeout` | 下载超时时间(秒) | 600 |
| `download_retry` | 下载重试次数 | 3 |
| `pip_mirror` | pip 镜像源 | https://pypi.tuna.tsinghua.edu.cn/simple |

## 使用示例

### 安装 Python LLM 环境

```bash
oedp run install
```

### 检查 Python LLM 环境状态

```bash
oedp run status
```

### 卸载 Python LLM 环境

```bash
oedp run uninstall
```

## 注意事项

1. 本插件需要 root 权限执行
2. 默认使用虚拟环境安装，避免影响系统 Python
3. 安装过程中会自动安装系统依赖包
4. 支持自定义 LLM 库版本
5. 使用国内镜像源加速下载
6. 本插件适用于 openEuler 24.03-LTS 及以上版本

## 故障排查

- 如安装失败，请检查网络连接是否正常
- 如依赖包安装失败，请检查 pip 镜像源配置
- 如虚拟环境创建失败，请检查目录权限
- 如内存不足，请增加系统内存

## 版本历史

- v1.0.0：初始版本，支持 Python LLM 环境的安装和管理