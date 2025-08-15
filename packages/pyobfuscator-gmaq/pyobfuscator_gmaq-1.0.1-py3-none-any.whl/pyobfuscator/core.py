"""
Core obfuscation engine that orchestrates all protection mechanisms
"""

import os
import sys
import logging
import hashlib
import time
from pathlib import Path

from .obfuscator import CodeObfuscator
from .encryption import AdvancedEncryption
from .anti_tamper import AntiTamperProtection
from .utils import generate_random_name, calculate_file_hash

class PyObfuscatorCore:
    """Main obfuscation engine that coordinates all protection mechanisms"""
    
    def __init__(self, max_security=False, custom_key=None, iterations=3,
                 anti_debug=False, remove_docstrings=False, library_mode=False):
        """
        Initialize the obfuscation core
        
        Args:
            max_security (bool): Enable maximum security mode
            custom_key (str): Custom encryption key
            iterations (int): Number of obfuscation passes
            anti_debug (bool): Enable anti-debugging
            remove_docstrings (bool): Remove docstrings and comments
            library_mode (bool): Generate importable library
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Configuration
        self.max_security = max_security
        self.iterations = iterations if not max_security else 5
        self.anti_debug = anti_debug or max_security
        self.remove_docstrings = remove_docstrings or max_security
        self.library_mode = library_mode
        
        # Initialize components
        self.obfuscator = CodeObfuscator(
            remove_docstrings=self.remove_docstrings,
            max_obfuscation=max_security
        )
        
        self.encryption = AdvancedEncryption(custom_key=custom_key)
        
        self.anti_tamper = AntiTamperProtection(
            enable_debug_detection=self.anti_debug,
            enable_modification_detection=True,
            max_security=max_security
        )
        
        # Statistics
        self.stats = {
            'start_time': None,
            'end_time': None,
            'original_size': 0,
            'obfuscated_size': 0,
            'compression_ratio': 0,
            'obfuscation_passes': 0,
            'security_features': []
        }
    
    def obfuscate_string(self, source_code):
        """
        Obfuscate Python source code string
        
        Args:
            source_code (str): Python source code
            
        Returns:
            str: Obfuscated and encrypted code
        """
        self.stats['start_time'] = time.time()
        self.stats['original_size'] = len(source_code)
        
        try:
            self.logger.info("Starting code obfuscation process...")
            
            # Step 1: Multiple obfuscation passes
            obfuscated_code = source_code
            for i in range(self.iterations):
                self.logger.debug(f"Obfuscation pass {i+1}/{self.iterations}")
                obfuscated_code = self.obfuscator.obfuscate(obfuscated_code)
                self.stats['obfuscation_passes'] += 1
            
            # Step 2: Add anti-tamper protection
            if self.anti_debug or self.max_security:
                self.logger.debug("Adding anti-tamper protection...")
                obfuscated_code = self.anti_tamper.wrap_code(obfuscated_code)
                self.stats['security_features'].append('anti_tamper')
            
            # Step 3: Encrypt the final code
            self.logger.debug("Encrypting obfuscated code...")
            encrypted_code = self.encryption.encrypt_code(obfuscated_code)
            self.stats['security_features'].append('encryption')
            
            # Step 4: Generate final executable wrapper
            if self.library_mode:
                final_code = self._generate_library_wrapper(encrypted_code)
            else:
                final_code = self._generate_executable_wrapper(encrypted_code)
            
            self.stats['end_time'] = time.time()
            self.stats['obfuscated_size'] = len(final_code)
            self.stats['compression_ratio'] = (
                self.stats['obfuscated_size'] / self.stats['original_size']
                if self.stats['original_size'] > 0 else 0
            )
            
            self.logger.info("Code obfuscation completed successfully")
            return final_code
            
        except Exception as e:
            self.logger.error(f"Obfuscation failed: {str(e)}")
            raise
    
    def obfuscate_file(self, input_file, output_file=None):
        """
        Obfuscate a Python file
        
        Args:
            input_file (str): Path to input Python file
            output_file (str): Path to output file
            
        Returns:
            bool: True if successful
        """
        try:
            # Read input file
            with open(input_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Calculate original file hash for integrity checking
            original_hash = calculate_file_hash(input_file)
            self.logger.debug(f"Original file hash: {original_hash}")
            
            # Obfuscate code
            obfuscated_code = self.obfuscate_string(source_code)
            
            # Determine output file
            if output_file is None:
                input_path = Path(input_file)
                output_file = input_path.parent / f"{input_path.stem}_obfuscated{input_path.suffix}"
            
            # Write obfuscated file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(obfuscated_code)
            
            # Make executable if not in library mode
            if not self.library_mode:
                os.chmod(output_file, 0o755)
            
            self.logger.info(f"Obfuscated file saved: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"File obfuscation failed: {str(e)}")
            return False
    
    def _generate_executable_wrapper(self, encrypted_code):
        """Generate standalone executable wrapper"""
        wrapper_template = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Protected Python Application
This file contains encrypted and obfuscated code.
Reverse engineering attempts will be detected and prevented.
"""

import sys
import os
import base64
import marshal
import types
import hashlib
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# Anti-debugging and tamper detection
def _check_environment():
    """Detect debugging and analysis attempts"""
    import psutil
    import threading
    
    # Check for common debuggers
    debugger_names = ['gdb', 'strace', 'ltrace', 'python-dbg', 'pdb']
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in debugger_names:
            sys.exit(1)
    
    # Check execution time (anti-analysis)
    start_time = time.time()
    time.sleep(0.01)
    if time.time() - start_time > 0.1:
        sys.exit(1)
    
    # Verify file integrity
    current_file = __file__
    if os.path.exists(current_file):
        expected_hash = "{file_hash}"
        with open(current_file, 'rb') as f:
            content = f.read()
        actual_hash = hashlib.sha256(content).hexdigest()
        if actual_hash != expected_hash:
            sys.exit(1)

def _decrypt_and_execute():
    """Decrypt and execute the protected code"""
    try:
        _check_environment()
        
        # Encrypted payload
        encrypted_data = {encrypted_payload}
        
        # Decrypt
        key = {decryption_key}
        salt = {salt}
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(key.encode())
        
        cipher = Cipher(algorithms.AES(key), modes.GCM({nonce}), backend=default_backend())
        decryptor = cipher.decryptor()
        
        decrypted = decryptor.update(encrypted_data) + decryptor.finalize_with_tag({tag})
        
        # Execute decrypted code
        code_obj = marshal.loads(decrypted)
        exec(code_obj, globals())
        
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    _decrypt_and_execute()
'''
        
        # Generate encryption components
        key_data = self.encryption.get_key_data()
        file_hash = hashlib.sha256(wrapper_template.encode()).hexdigest()
        
        return wrapper_template.format(
            encrypted_payload=encrypted_code['data'],
            decryption_key=repr(key_data['key']),
            salt=key_data['salt'],
            nonce=key_data['nonce'],
            tag=key_data['tag'],
            file_hash=file_hash
        )
    
    def _generate_library_wrapper(self, encrypted_code):
        """Generate importable library wrapper"""
        library_template = '''"""
Protected Python Library Module
This module contains encrypted and obfuscated code.
"""

import sys
import os
import base64
import marshal
import types
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# Module initialization with protection
_initialized = False
_module_functions = {{}}

def _initialize_module():
    """Initialize the protected module"""
    global _initialized, _module_functions
    
    if _initialized:
        return _module_functions
    
    try:
        # Encrypted payload
        encrypted_data = {encrypted_payload}
        
        # Decrypt
        key = {decryption_key}
        salt = {salt}
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(key.encode())
        
        cipher = Cipher(algorithms.AES(key), modes.GCM({nonce}), backend=default_backend())
        decryptor = cipher.decryptor()
        
        decrypted = decryptor.update(encrypted_data) + decryptor.finalize_with_tag({tag})
        
        # Execute decrypted code in isolated namespace
        namespace = {{}}
        code_obj = marshal.loads(decrypted)
        exec(code_obj, namespace)
        
        # Extract functions and classes for module interface
        _module_functions = {{k: v for k, v in namespace.items() 
                            if not k.startswith('_')}}
        _initialized = True
        
        return _module_functions
        
    except Exception:
        return {{}}

# Dynamic attribute access
def __getattr__(name):
    functions = _initialize_module()
    if name in functions:
        return functions[name]
    raise AttributeError(f"module has no attribute '{{name}}'")

# Module initialization
_initialize_module()
'''
        
        # Generate encryption components
        key_data = self.encryption.get_key_data()
        
        return library_template.format(
            encrypted_payload=encrypted_code['data'],
            decryption_key=repr(key_data['key']),
            salt=key_data['salt'],
            nonce=key_data['nonce'],
            tag=key_data['tag']
        )
    
    def get_statistics(self):
        """Get obfuscation statistics"""
        if self.stats['start_time'] and self.stats['end_time']:
            self.stats['execution_time'] = self.stats['end_time'] - self.stats['start_time']
        
        return self.stats.copy()
