"""
Input module for processing various data sources.

Functions:
- load_all: Process all available data sources and save to disk

Submodules (for access to individual data reading functions):
- emissions
- socioeconomics
- ndcs
- all (source file for load_all)

"""

# Expose complete submodules for advanced usage
# These allow imports like: from effortsharing.input import emissions
# or: from effortsharing.input import load_all
from . import emissions, ndcs, socioeconomics
from .all import load_all
