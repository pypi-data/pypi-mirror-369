# src/mdfile/__init__.py
"""
mdfile — Markdown File Manipulation Package
"""
from importlib.metadata import version

__version__ = version("your-package-name")

from .mdfile import app  # Expose the Typer app for CLI entry point

__version__ = version("mdfile")
__author__ = "Chuck Bass"
__email__ = "chuck@acrocad.net"

__all__ = ["app", "__version__", "__author__", "__email__"]
