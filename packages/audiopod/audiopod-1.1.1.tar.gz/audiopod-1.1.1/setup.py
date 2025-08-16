#!/usr/bin/env python3
"""
AudioPod API Client - Setup Configuration
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "AudioPod API Client - Professional Audio Processing SDK"

# Read requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return [
            "requests>=2.28.0",
            "aiohttp>=3.8.0",
            "pydantic>=1.10.0",
            "python-dotenv>=0.19.0",
            "tqdm>=4.64.0",
            "websockets>=10.4",
        ]

setup(
    name="audiopod",
    version="1.1.0",
    author="AudioPod AI",
    author_email="support@audiopod.ai",
    description="Professional Audio Processing API Client for Python",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/audiopod-ai/audiopod-python",
    project_urls={
        "Homepage": "https://audiopod.ai",
        "Documentation": "https://docs.audiopod.ai",
        "API Reference": "https://api.audiopod.ai/docs",
        "Bug Tracker": "https://github.com/audiopod-ai/audiopod-python/issues",
    },
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
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "twine>=4.0.0",
            "build>=0.10.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "sphinx-autodoc-typehints>=1.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "audiopod=audiopod.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "audio", "processing", "ai", "voice", "cloning", "transcription", 
        "translation", "music", "generation", "denoising", "api", "sdk"
    ],
)
