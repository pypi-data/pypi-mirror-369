from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "CUDA Switch - A tool for managing multiple CUDA versions on macOS"

setup(
    name="cuda-switch",
    version="1.0.0",
    author="Jason Wang",
    author_email="your-email@example.com",  # 请替换为你的邮箱
    description="A tool for managing multiple CUDA versions on macOS",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cuda-switch",  # 请替换为你的GitHub仓库
    packages=find_packages(),
    py_modules=["cuda_switch", "cuda_downloader"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.6.0",
    ],
    entry_points={
        "console_scripts": [
            "cuda-switch=cuda_switch:main",
        ],
    },
    keywords="cuda nvidia gpu development macos",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/cuda-switch/issues",
        "Source": "https://github.com/yourusername/cuda-switch",
    },
)