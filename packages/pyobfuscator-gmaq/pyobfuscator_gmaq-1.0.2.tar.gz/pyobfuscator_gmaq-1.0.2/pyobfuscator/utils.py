"""
Utility functions for the obfuscation system
"""

import os
import sys
import random
import string
import base64
import hashlib
import logging
import ast
import keyword
from pathlib import Path


def setup_logging(level=logging.INFO):
    """
    Setup logging configuration
    
    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def generate_random_name(length=None, prefix=""):
    """
    Generate random variable/function name
    
    Args:
        length (int, optional): Length of the name
        prefix (str): Prefix for the name
        
    Returns:
        str: Random valid Python identifier
    """
    if length is None:
        length = random.randint(8, 16)
    
    # Start with letter or underscore
    first_chars = string.ascii_letters + '_'
    other_chars = string.ascii_letters + string.digits + '_'
    
    name = prefix + random.choice(first_chars)
    name += ''.join(random.choices(other_chars, k=length-1))
    
    # Ensure it's not a Python keyword
    while keyword.iskeyword(name) or name in ['print', 'input', 'len', 'str', 'int']:
        name = generate_random_name(length, prefix)
    
    return name


def encode_string(text):
    """
    Encode string using base64
    
    Args:
        text (str): Text to encode
        
    Returns:
        str: Base64 encoded string
    """
    return base64.b64encode(text.encode('utf-8')).decode('ascii')


def decode_string(encoded):
    """
    Decode base64 encoded string
    
    Args:
        encoded (str): Base64 encoded string
        
    Returns:
        str: Decoded text
    """
    return base64.b64decode(encoded.encode('ascii')).decode('utf-8')


def calculate_file_hash(file_path):
    """
    Calculate SHA256 hash of a file
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: SHA256 hash in hexadecimal
    """
    hash_sha256 = hashlib.sha256()
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception:
        return ""


def validate_python_file(file_path):
    """
    Validate if file is a valid Python file
    
    Args:
        file_path (str): Path to the Python file
        
    Returns:
        bool: True if valid Python file
    """
    if not os.path.exists(file_path):
        return False
    
    if not file_path.endswith('.py'):
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Try to parse the AST
        ast.parse(source_code)
        return True
    except Exception:
        return False


def get_python_version():
    """
    Get current Python version info
    
    Returns:
        tuple: Python version tuple
    """
    return sys.version_info


def ensure_directory(directory_path):
    """
    Ensure directory exists, create if necessary
    
    Args:
        directory_path (str): Path to directory
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def get_random_string(length=32, include_special=False):
    """
    Generate random string
    
    Args:
        length (int): Length of string
        include_special (bool): Include special characters
        
    Returns:
        str: Random string
    """
    chars = string.ascii_letters + string.digits
    if include_special:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    return ''.join(random.choices(chars, k=length))


def obfuscate_constants():
    """
    Generate obfuscated constants for use in code
    
    Returns:
        dict: Dictionary of obfuscated constants
    """
    constants = {}
    
    # Common values with obfuscated expressions
    constants['zero'] = f"(len('{get_random_string(10)}') - {random.randint(8, 12)})"
    constants['one'] = f"(len('{get_random_string(1)}'))"
    constants['true'] = f"(not not {random.randint(1, 100)})"
    constants['false'] = f"(not {random.randint(1, 100)})"
    
    return constants


def generate_fake_metadata():
    """
    Generate fake metadata to hide real origins
    
    Returns:
        dict: Fake metadata dictionary
    """
    fake_authors = [
        "system_generator", "auto_compiler", "code_transformer",
        "binary_converter", "script_processor", "app_builder"
    ]
    
    fake_descriptions = [
        "Auto-generated system utility",
        "Compiled application bundle", 
        "Binary conversion tool",
        "System optimization script",
        "Application runtime loader"
    ]
    
    return {
        'author': random.choice(fake_authors),
        'description': random.choice(fake_descriptions),
        'version': f"{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 99)}",
        'build_id': get_random_string(16),
        'timestamp': 'auto-generated'
    }


def clean_source_traces(code):
    """
    Remove traces that could identify original source
    
    Args:
        code (str): Source code
        
    Returns:
        str: Cleaned source code
    """
    lines = code.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove comments that might contain identifying information
        if line.strip().startswith('#'):
            # Keep structural comments but remove content
            if any(keyword in line.lower() for keyword in ['todo', 'fixme', 'hack', 'author', 'copyright']):
                continue
        
        # Remove docstrings with identifying information
        if '"""' in line or "'''" in line:
            if any(keyword in line.lower() for keyword in ['author', 'copyright', 'license', 'created']):
                continue
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def generate_decoy_functions():
    """
    Generate decoy functions to confuse analysis
    
    Returns:
        list: List of decoy function definitions
    """
    decoy_functions = []
    
    for i in range(random.randint(5, 15)):
        func_name = generate_random_name()
        param_name = generate_random_name()
        
        # Generate different types of decoy functions
        function_types = [
            f"def {func_name}({param_name}):\n    return len(str({param_name})) * 42",
            f"def {func_name}({param_name}):\n    return sum(ord(c) for c in str({param_name}))",
            f"def {func_name}({param_name}):\n    import hashlib\n    return hashlib.md5(str({param_name}).encode()).hexdigest()",
            f"def {func_name}({param_name}):\n    return {param_name} if {param_name} else 'default'"
        ]
        
        decoy_functions.append(random.choice(function_types))
    
    return decoy_functions


def create_anti_analysis_header():
    """
    Create header with anti-analysis warnings
    
    Returns:
        str: Anti-analysis header
    """
    return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROTECTED APPLICATION

This file contains proprietary algorithms and is protected against:
- Reverse engineering
- Code analysis
- Unauthorized modification
- Debugging attempts

Any attempt to analyze, modify, or reverse engineer this code
may result in system instability or application failure.

This file is automatically generated and optimized.
Manual modification is not recommended.
"""

import sys
import os

# Integrity and protection checks
if __name__ != "__main__":
    # Prevent import analysis
    import random
    import time
    time.sleep(random.uniform(0.1, 0.5))

'''


class CodeAnalyzer:
    """Analyze code structure for optimization of obfuscation"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze_code_complexity(self, source_code):
        """
        Analyze code complexity to determine obfuscation strategy
        
        Args:
            source_code (str): Source code to analyze
            
        Returns:
            dict: Analysis results
        """
        try:
            tree = ast.parse(source_code)
            
            analysis = {
                'functions': 0,
                'classes': 0,
                'imports': 0,
                'variables': set(),
                'string_literals': 0,
                'loops': 0,
                'conditionals': 0,
                'complexity_score': 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis['functions'] += 1
                elif isinstance(node, ast.ClassDef):
                    analysis['classes'] += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    analysis['imports'] += 1
                elif isinstance(node, ast.Name):
                    analysis['variables'].add(node.id)
                elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                    analysis['string_literals'] += 1
                elif isinstance(node, (ast.For, ast.While)):
                    analysis['loops'] += 1
                elif isinstance(node, ast.If):
                    analysis['conditionals'] += 1
            
            # Calculate complexity score
            analysis['complexity_score'] = (
                analysis['functions'] * 2 +
                analysis['classes'] * 3 +
                analysis['loops'] * 2 +
                analysis['conditionals'] +
                len(analysis['variables'])
            )
            
            analysis['variables'] = len(analysis['variables'])
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Code analysis failed: {str(e)}")
            return {'complexity_score': 0}
    
    def recommend_obfuscation_level(self, analysis):
        """
        Recommend obfuscation level based on analysis
        
        Args:
            analysis (dict): Code analysis results
            
        Returns:
            str: Recommended obfuscation level
        """
        complexity = analysis.get('complexity_score', 0)
        
        if complexity > 100:
            return 'maximum'
        elif complexity > 50:
            return 'high'
        elif complexity > 20:
            return 'medium'
        else:
            return 'basic'


def format_code_professionally(code):
    """
    Format code to look professionally generated
    
    Args:
        code (str): Source code
        
    Returns:
        str: Professionally formatted code
    """
    # Add professional header
    header = create_anti_analysis_header()
    
    # Add fake metadata as comments
    metadata = generate_fake_metadata()
    metadata_comment = f"""
# Application Metadata
# Version: {metadata['version']}
# Build ID: {metadata['build_id']}
# Generated: {metadata['timestamp']}
# Description: {metadata['description']}

"""
    
    return header + metadata_comment + code


def get_system_info():
    """
    Get system information for environment-specific obfuscation
    
    Returns:
        dict: System information
    """
    info = {
        'platform': sys.platform,
        'python_version': '.'.join(map(str, sys.version_info[:3])),
        'architecture': 'x64' if sys.maxsize > 2**32 else 'x32',
        'byte_order': sys.byteorder
    }
    
    try:
        info['username'] = os.getenv('USER', os.getenv('USERNAME', 'unknown'))
        info['hostname'] = os.uname().nodename if hasattr(os, 'uname') else 'unknown'
    except:
        info['username'] = 'unknown'
        info['hostname'] = 'unknown'
    
    return info
