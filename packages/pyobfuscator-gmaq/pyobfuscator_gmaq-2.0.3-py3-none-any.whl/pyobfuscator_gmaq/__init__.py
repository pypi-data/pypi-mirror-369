"""
PyObfuscator-GMAQ: Advanced Python Code Obfuscation Library
Version 2.0.3

A sophisticated obfuscation tool that provides strong encryption for Python files
with distributed password storage and automatic decryption capabilities.
"""

__version__ = "2.0.3"
__author__ = "GMAQ Security"
__email__ = "admin@gmaq.security"

from .core import PyObfuscatorGMAQ
from .runtime import decrypt_and_execute

__all__ = ["PyObfuscatorGMAQ", "decrypt_and_execute"]
