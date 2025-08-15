"""
pydhis2 - Python DHIS2 Integration Library

A Python library for DHIS2 (District Health Information Software 2) integration.
This package provides tools and utilities for working with DHIS2 APIs and data management.
"""

__version__ = "0.1.0"
__author__ = "DHIS2 Team"
__email__ = "team@pydhis2.org"
__description__ = "Python library for DHIS2 integration"

# Main package imports
from .client import DHIS2Client
from .utils import DHISUtils

__all__ = ['DHIS2Client', 'DHISUtils']
