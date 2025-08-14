#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="niteco.agno-agent-tool",
    version="0.1.1",
    author="Niteco",
    author_email="info@niteco.com",
    description="A service that manages and executes agno agents with OPAL SDK integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/niteco/agno-agent-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.95.0",
        "agno>=1.7.0",
        "optimizely-opal.opal-tools-sdk>=0.1.0",
        "pydantic>=2.0.0",
        "uvicorn>=0.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0",
            "isort>=5.0",
            "mypy>=1.0",
        ],
    },
)