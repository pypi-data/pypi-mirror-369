#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read README for long description
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

setup(
    name="acheron-sdk",
    version="1.0.0",
    description="Official Python SDK for Acheron AI Governance Platform",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author="Acheron AI",
    author_email="sdk@acheron.ai",
    url="https://github.com/acheron-ai/acheron-python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/acheron-ai/acheron/issues",
        "Documentation": "https://docs.acheron.ai/sdks/python",
        "Source Code": "https://github.com/acheron-ai/acheron-python-sdk",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "websocket-client>=1.6.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
        "urllib3>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "sphinx-autodoc-typehints>=1.19.0",
        ],
        "async": [
            "aiohttp>=3.8.0",
            "websockets>=11.0.0",
        ],
    },
    keywords=[
        "acheron",
        "ai-governance", 
        "compliance",
        "policy-engine",
        "gdpr",
        "hipaa",
        "soc2",
        "iso42001",
        "ai-safety",
        "machine-learning",
        "artificial-intelligence",
    ],
    zip_safe=False,
    include_package_data=True,
    package_data={
        "acheron": ["py.typed"],
    },
) 