#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="beets-lyrics-manager",
    version="0.0.3",
    author="zytx",
    author_email="zywsad@gmail.com",
    description="A beets plugin for managing lyrics files alongside music files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zytx/beets-lyrics-manager",
    packages=find_namespace_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    python_requires=">=3.7",
    install_requires=[
        "beets>=1.6.0",
    ],
) 