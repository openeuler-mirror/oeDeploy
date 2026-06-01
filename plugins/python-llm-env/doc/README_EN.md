# How to Use the Python LLM Application Environment Plug-in

## Plugin Description

This plug-in is used to automatically deploy the Python LLM virtual environment on openEuler. The following core libraries are included:

- LangChain: LLM development framework
- OpenAI: OpenAI API client
- LlamaIndex: data indexing and retrieval framework

In addition, some common auxiliary libraries, such as NumPy, pandas, transformers, sentence-transformers, chromadb, and faiss-cpu, as well as dependencies related to document processing, vector databases, and database connections, will also be installed.

## Supported Operations

- `install`: installs the Python LLM environment.
- `uninstall`: uninstalls the Python LLM environment.
- `status`: checks the status of the Python LLM environment.

## Configuration Description

Configure the following parameters in the `config.yaml` file.

| Parameter| Description| Default Value|
|------|------|--------|
| `python_version` | Python version| 3.9 |
| `venv_name` | Virtual environment name| python-llm-env |
| `venv_path` | Virtual environment path| /opt/python-llm-env |
| `install_mode` | Installation mode (system/venv)| venv |
| `langchain_version` | LangChain version| latest |
| `openai_version` | OpenAI version| latest |
| `llama_index_version` | LlamaIndex version| latest |
| `extra_packages` | Additional packages| numpy, pandas, scikit-learn, matplotlib, jupyter, ipython, seaborn, scipy, plotly, tqdm, Pillow, opencv-python, transformers, datasets, tokenizers, sentence-transformers, pyarrow, fasttext, textblob, wordcloud, pattern, requests, beautifulsoup4, lxml, pymupdf, pypdf, docx2txt, python-docx, unstructured, chromadb, faiss-cpu, pinecone-client, weaviate-client, redis, pymongo, psycopg2-binary, sqlalchemy, pydantic, pydantic-settings, rich, click, colorama, python-dotenv |
| `download_timeout` | Download timeout (s)| 600 |
| `download_retry` | Download retry attempts| 3 |
| `pip_mirror` | pip image source| <https://pypi.tuna.tsinghua.edu.cn/simple> |

## Examples

### Installing the Python LLM Environment

```bash
oedp run install
```

### Checking the Status of the Python LLM Environment

```bash
oedp run status
```

### Uninstalling the Python LLM Environment

```bash
oedp run uninstall
```

## Precautions

1. This plug-in requires the root permission.
2. By default, the virtual environment is used for installation to avoid affecting the system Python.
3. System dependencies are automatically installed during the installation.
4. Customized LLM library versions are supported.
5. The image source in China is used for high-speed download.
6. This plug-in applies to openEuler 24.03-LTS and later versions.

## Troubleshooting

- If the installation fails, check whether the network connection is normal.
- If the dependency package fails to be installed, check the pip image source configuration.
- If the virtual environment fails to be created, check the directory permission.
- If the memory is insufficient, increase the system memory.

## Version History

- v1.0.0: initial version, which supports the installation and management of the Python LLM environment.
