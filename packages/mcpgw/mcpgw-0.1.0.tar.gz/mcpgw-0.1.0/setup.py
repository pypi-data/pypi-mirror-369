#!/usr/bin/env python3
"""
Setup script for MCP Gateway
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mcpgw",
    version="0.1.0",
    author="Mark Lechner",
    author_email="hello@marklechner.dev",
    description="A lightweight, security-focused FastAPI gateway for Model Context Protocol (MCP) servers",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/marklechner/mcpgw",
    project_urls={
        "Bug Tracker": "https://github.com/marklechner/mcpgw/issues",
        "Documentation": "https://github.com/marklechner/mcpgw#readme",
        "Source Code": "https://github.com/marklechner/mcpgw",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
        "Environment :: Web Environment",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "redis": [
            "redis>=4.5.0",
        ],
        "postgres": [
            "asyncpg>=0.28.0",
            "sqlalchemy>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mcpgw=mcpgw.main:main",
            "mcpgw-server=mcpgw.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mcpgw": [
            "config.yaml",
            "*.md",
        ],
    },
    keywords=[
        "mcp",
        "model-context-protocol",
        "gateway",
        "api-gateway",
        "security",
        "fastapi",
        "authentication",
        "authorization",
        "rate-limiting",
        "proxy",
        "middleware",
    ],
    zip_safe=False,
)
