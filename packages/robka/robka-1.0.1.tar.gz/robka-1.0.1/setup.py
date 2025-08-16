#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for robka - A modern, optimized Python library for Rubika API
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="robka",
    version="1.0.1",
    author="htteX",
    author_email="httex@example.com",
    description="کتابخانه مدرن و بهینه‌شده پایتون برای API روبیکا - Modern, optimized Python library for Rubika API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/httex/robka",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "pycryptodome>=3.15.0",
        "websocket-client>=1.0.0",
        "aiohttp>=3.8.0",
        "tqdm>=4.60.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "media": [
            "tinytag>=1.8.0",
            "Pillow>=8.0.0",
        ],
    },
    keywords="rubika, api, bot, messenger, chat, robka, htteX",
    project_urls={
        "Bug Reports": "https://github.com/httex/robka/issues",
        "Source": "https://github.com/httex/robka",
        "Documentation": "https://robka.readthedocs.io/",
    },
    include_package_data=True,
    zip_safe=False,
)

