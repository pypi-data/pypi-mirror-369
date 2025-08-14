"""
Hostinger CLI - A comprehensive command-line interface for Hostinger API
"""

__version__ = "1.0.0"
__author__ = "Hostinger CLI Contributors"
__email__ = "support@hostinger.com"
__description__ = "Command-line interface for managing Hostinger services"

from .main import main, cli

__all__ = ["main", "cli", "__version__"]
