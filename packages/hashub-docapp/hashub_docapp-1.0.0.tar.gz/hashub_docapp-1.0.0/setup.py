#!/usr/bin/env python3
"""
Setup script for HashubDocApp Python SDK
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = (this_directory / "requirements.txt").read_text(encoding='utf-8').strip().split('\n')
requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="hashub-docapp",
    version="1.0.0",
    author="Hashub Team",
    author_email="support@hashub.dev",
    description="Professional Python SDK for the HashubDocApp API - Advanced OCR, document conversion, and text extraction service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hasanbahadir/hashub-doc-sdk",
    project_urls={
        "Documentation": "https://doc.hashub.dev",
        "API Reference": "https://doc.hashub.dev/api",
        "Bug Reports": "https://github.com/hasanbahadir/hashub-doc-sdk/issues",
        "Source": "https://github.com/hasanbahadir/hashub-doc-sdk",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "hashub-docapp=hashub_docapp.cli:main",
        ],
    },
    keywords=[
        "ocr", "pdf", "document", "conversion", "text-extraction", 
        "image-processing", "api-client", "hashub", "batch-processing"
    ],
    include_package_data=True,
    zip_safe=False,
)
