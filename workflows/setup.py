#!/usr/bin/env python3
"""
Setup script for Claude Code Workflow Engine
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
    name="claude-code-workflow-engine",
    version="1.0.0",
    author="Claude Code Team",
    author_email="support@claude-code.ai",
    description="Workflow automation system for multi-agent orchestration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/claude-code/workflow-engine",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.2.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.1.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
        "docs": [
            "sphinx>=6.1.0",
            "sphinx-rtd-theme>=1.2.0",
            "mkdocs>=1.4.0",
            "mkdocs-material>=9.0.0",
        ],
        "postgres": [
            "asyncpg>=0.28.0",
            "psycopg2-binary>=2.9.5",
        ],
        "redis": [
            "aioredis>=2.0.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "workflow=workflows.cli:main",
            "workflow-dashboard=workflows.dashboard:main",
        ],
    },
    include_package_data=True,
    package_data={
        "workflows": [
            "workflow_templates/*.yaml",
            "examples/*.py",
            "examples/*.yaml",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/claude-code/workflow-engine/issues",
        "Source": "https://github.com/claude-code/workflow-engine",
        "Documentation": "https://docs.claude-code.ai/workflow-engine",
    },
)