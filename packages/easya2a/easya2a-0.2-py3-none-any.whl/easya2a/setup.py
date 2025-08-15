"""
EasyA2A 安装脚本

用于安装easya2a包的setup.py文件。
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# 读取版本
version_file = Path(__file__).parent / "__init__.py"
version = "0.2.2"  # 默认版本

if version_file.exists():
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip('"').strip("'")
                break

setup(
    name="easya2a",
    version=version,
    author="EasyA2A Team",
    author_email="team@easya2a.com",
    description="快速将LangChain Agent包装为A2A协议服务",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/easya2a",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        # 核心依赖
        "uvicorn>=0.20.0",
        "starlette>=0.25.0",
        
        # A2A协议支持（假设已安装）
        # "a2a>=0.3.0",  # 取消注释如果a2a包可通过pip安装
    ],
    extras_require={
        "langchain": [
            "langchain>=0.1.0",
            "langchain-core>=0.1.0",
            "langchain-openai>=0.1.0",
        ],
        "openai": [
            "openai>=1.0.0",
        ],
        "anthropic": [
            "anthropic>=0.20.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
            "mkdocstrings[python]>=0.20.0",
        ],
        "all": [
            "langchain>=0.1.0",
            "langchain-core>=0.1.0", 
            "langchain-openai>=0.1.0",
            "openai>=1.0.0",
            "anthropic>=0.20.0",
            "pydantic>=2.0.0",
            "pyyaml>=6.0.0",
            "python-dotenv>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "easya2a-test=easya2a.utils.validation:main",
        ],
    },
    include_package_data=True,
    package_data={
        "easya2a": [
            "examples/*.py",
            "*.md",
        ],
    },
    keywords=[
        "a2a",
        "agent",
        "langchain",
        "ai",
        "chatbot",
        "wrapper",
        "protocol",
        "rpc",
        "microservice",
        "easya2a"
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-org/easya2a/issues",
        "Source": "https://github.com/your-org/easya2a",
        "Documentation": "https://easya2a.readthedocs.io/",
    },
)
