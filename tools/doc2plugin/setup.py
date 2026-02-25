from setuptools import setup, find_packages

setup(
    name="doc2plugin",
    version="1.0.0",
    description="AI Agent工具，智能代码编写助手",
    author="doc2plugin",
    packages=find_packages(where='.', include=['doc2plugin*']),
    package_dir={'': '.'},
    package_data={
        'doc2plugin': ['../config/*.yaml'],
    },
    include_package_data=True,
    install_requires=[
        "langchain>=0.1.0",
        "langchain-openai>=0.1.0", 
        "langchain-community>=0.0.20",
        "pyyaml>=6.0",
        "click>=8.0.0",
        "colorama>=0.4.6"
    ],
    entry_points={
        'console_scripts': [
            'doc2plugin=doc2plugin.cli:main',
        ],
    },
    python_requires='>=3.8',
)

