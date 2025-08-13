#!/usr/bin/env python
"""
桌面卡通贴纸效果程序的安装配置
"""

import os
from setuptools import setup, find_packages

# 读取README文件
def read_readme():
    """读取README文件内容"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# 读取版本信息
def get_version():
    """从__init__.py获取版本信息"""
    init_path = os.path.join(os.path.dirname(__file__), 'desktop_stickers', '__init__.py')
    with open(init_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return "1.0.0"

# 包信息配置
setup(
    name="dster",
    version=get_version(),
    author="ylicen",
    author_email="sokllmiller@gmail.com",
    description="一个在Windows桌面上显示动态卡通贴纸的Python程序",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ylicen/desktop-stickers",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Desktop Environment",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pygame>=2.0.0",
    ],
    extras_require={
        "dev": [
            "build",
            "twine",
            "wheel",
        ],
    },
    entry_points={
        "console_scripts": [
            "dster=desktop_stickers.cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="desktop, stickers, pygame, windows, animation, cartoon",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/desktop-stickers/issues",
        "Source": "https://github.com/yourusername/desktop-stickers",
    },
)