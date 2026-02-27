#!/usr/bin/env python3
"""
SPYGLASS - SEO Intelligence Platform
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="spyglass-seo",
    version="0.1.0",
    author="ssecgroup",
    author_email="ssecgroup@users.noreply.github.com",
    description="Advanced open-source SEO intelligence platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ssecgroup/spyglass",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.9.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "dnspython>=2.4.0",
        "cryptography>=41.0.0",
        "pyOpenSSL>=23.0.0",
    ],
    entry_points={
        "console_scripts": [
            "spyglass=pipelines.cli:main",
        ],
    },
    include_package_data=True,
)
