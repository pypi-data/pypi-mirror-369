"""
AppImage Fixer - Automatic AppImage Desktop File Manager

A Python package that automatically fixes AppImageLauncher-generated desktop files by:
- Cleaning up icon references (removing version numbers)
- Adding --no-sandbox flags for Electron-based applications
- Refreshing system desktop database and icon cache

Author: AI Assistant & akopylov
License: MIT
Version: 1.1.0
"""

__version__ = "1.2.10"
__author__ = "AI Assistant & akopylov"
__email__ = "user@example.com"
__license__ = "MIT"

from .core import AppImageFixer
from .config import get_app_config, FIXER_SETTINGS
from .database import AppImageDatabase

__all__ = ["AppImageFixer", "get_app_config", "FIXER_SETTINGS", "AppImageDatabase"]
