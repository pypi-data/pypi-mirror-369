"""
Setup configuration for pydhis2 package
"""

from setuptools import setup, find_packages
import os

# Read the README file
current_dir = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(current_dir, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = """
pydhis2 - Python DHIS2 Integration Library

A comprehensive Python library for DHIS2 (District Health Information Software 2) integration.
This package provides tools and utilities for working with DHIS2 APIs, data management, 
and health information system operations.

Features:
- DHIS2 API client with authentication
- Data validation utilities
- Batch processing capabilities
- Easy-to-use interface for common DHIS2 operations

Perfect for health informatics professionals, developers, and organizations working with DHIS2.
"""

setup(
    name="pydhis2",
    version="0.1.0",
    author="DHIS2 Development Team",
    author_email="team@pydhis2.org",
    description="Python library for DHIS2 integration and health information management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pydhis2/pydhis2",
    project_urls={
        "Bug Tracker": "https://github.com/pydhis2/pydhis2/issues",
        "Documentation": "https://pydhis2.readthedocs.io/",
        "Source Code": "https://github.com/pydhis2/pydhis2",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=3.7.4;python_version<'3.8'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "isort>=5.0",
            "flake8>=3.8",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    keywords="dhis2, health, data, api, integration, health-informatics, who, healthcare",
    include_package_data=True,
    zip_safe=False,
)
