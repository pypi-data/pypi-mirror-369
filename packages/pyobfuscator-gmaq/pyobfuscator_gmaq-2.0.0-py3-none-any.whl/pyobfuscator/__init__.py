"""
Advanced Python Code Obfuscator and Encryption System
A comprehensive solution for protecting Python source code
"""

__version__ = "1.0.0"
__author__ = "PyObfuscator"
__description__ = "Advanced Python Code Obfuscation and Encryption System"

from .core import PyObfuscatorCore
from .obfuscator import CodeObfuscator
from .encryption import AdvancedEncryption
from .anti_tamper import AntiTamperProtection

# Library interface for programmatic usage
def obfuscate_code(source_code, **kwargs):
    """
    Obfuscate Python source code programmatically
    
    Args:
        source_code (str): Python source code to obfuscate
        **kwargs: Configuration options
    
    Returns:
        str: Obfuscated code
    """
    obfuscator = PyObfuscatorCore(**kwargs)
    return obfuscator.obfuscate_string(source_code)

def obfuscate_file(input_file, output_file=None, **kwargs):
    """
    Obfuscate a Python file
    
    Args:
        input_file (str): Path to input Python file
        output_file (str, optional): Path to output file
        **kwargs: Configuration options
    
    Returns:
        bool: True if successful, False otherwise
    """
    obfuscator = PyObfuscatorCore(**kwargs)
    return obfuscator.obfuscate_file(input_file, output_file)

# Export main classes
__all__ = [
    'PyObfuscatorCore',
    'CodeObfuscator', 
    'AdvancedEncryption',
    'AntiTamperProtection',
    'obfuscate_code',
    'obfuscate_file'
]
