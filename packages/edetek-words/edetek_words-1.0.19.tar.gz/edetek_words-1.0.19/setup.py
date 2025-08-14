# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/30/2025 3:04 PM
@Description: Description
@File: setup.py
"""

import setuptools
from setuptools import find_packages

from src.edetek_words import __version__

version = __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="edetek_words",
    version=version,
    author="xiaodong.li",
    author_email="",
    description="edetek words",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://example.com",
    install_requires=[
        'python-docx==1.2.0',
        'pywin32==311',
        'loguru==0.7.3',
        'PyYAML==6.0.2',
        'lxml==6.0.0',
        'requests==2.32.4',
        'pycryptodome==3.23.0',
    ],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3.10",
    ],
    include_package_data=True,
    package_data={
        'edetek_words.docs': ['*.json'],  # 列出所有需要包含的文档类型
    }
)
