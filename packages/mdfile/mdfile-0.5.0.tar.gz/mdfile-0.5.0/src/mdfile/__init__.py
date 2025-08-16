# src/mdfile/__init__.py
"""
mdfile — Markdown File Manipulation Package
"""

from .mdfile import app  # Expose the Typer app for CLI entry point

__version__ = "0.5.0"
__author__ = "Chuck Bass"
__email__ = "chuck@acrocad.net"

__all__ = ["app", "__version__", "__author__", "__email__"]
