"""
PyObfusCrypt - Advanced Python File Obfuscation Library
Complete multi-layer encryption for Python source code protection
"""

__version__ = "1.0.0"
__author__ = "PyObfusCrypt Team"
__description__ = "Advanced Python file obfuscation with multi-layer encryption"

from .core import PyObfusCrypt
from .cli import main

__all__ = ['PyObfusCrypt', 'main']
