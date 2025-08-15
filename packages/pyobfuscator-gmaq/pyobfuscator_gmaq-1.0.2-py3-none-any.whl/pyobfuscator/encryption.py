"""
Advanced encryption module for protecting obfuscated code
"""

import os
import hashlib
import base64
import secrets
import marshal
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend


class AdvancedEncryption:
    """Advanced encryption system with multiple layers of protection"""
    
    def __init__(self, custom_key=None):
        """
        Initialize encryption system
        
        Args:
            custom_key (str, optional): Custom encryption key
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.backend = default_backend()
        
        # Generate or use custom key
        if custom_key:
            self.master_key = custom_key.encode('utf-8')
        else:
            self.master_key = secrets.token_bytes(32)
        
        # Encryption parameters
        self.salt = secrets.token_bytes(16)
        self.iterations = 100000
        self.key_length = 32
        
        # Derive encryption key
        self.encryption_key = self._derive_key()
        
        # Store for wrapper generation
        self.last_nonce = None
        self.last_tag = None
    
    def _derive_key(self):
        """Derive encryption key using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_length,
            salt=self.salt,
            iterations=self.iterations,
            backend=self.backend
        )
        
        return kdf.derive(self.master_key)
    
    def encrypt_code(self, source_code):
        """
        Encrypt Python source code
        
        Args:
            source_code (str): Source code to encrypt
            
        Returns:
            dict: Encrypted data with metadata
        """
        try:
            self.logger.debug("Starting code encryption process...")
            
            # Compile source code to bytecode
            compiled_code = compile(source_code, '<encrypted>', 'exec')
            
            # Serialize bytecode
            bytecode = marshal.dumps(compiled_code)
            
            # Apply multiple encryption layers
            encrypted_data = self._multi_layer_encrypt(bytecode)
            
            self.logger.debug("Code encryption completed successfully")
            
            return {
                'data': base64.b64encode(encrypted_data).decode('utf-8'),
                'algorithm': 'AES-256-GCM',
                'layers': 3,
                'checksum': hashlib.sha256(encrypted_data).hexdigest()
            }
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def _multi_layer_encrypt(self, data):
        """Apply multiple layers of encryption"""
        current_data = data
        
        # Layer 1: XOR obfuscation
        current_data = self._xor_encrypt(current_data)
        
        # Layer 2: AES-256-GCM encryption
        current_data = self._aes_encrypt(current_data)
        
        # Layer 3: Custom stream cipher
        current_data = self._stream_encrypt(current_data)
        
        return current_data
    
    def _xor_encrypt(self, data):
        """Simple XOR encryption layer"""
        key = hashlib.sha256(self.encryption_key + b'xor_layer').digest()
        
        encrypted = bytearray()
        for i, byte in enumerate(data):
            encrypted.append(byte ^ key[i % len(key)])
        
        return bytes(encrypted)
    
    def _aes_encrypt(self, data):
        """AES-256-GCM encryption"""
        # Generate random nonce
        nonce = secrets.token_bytes(12)
        self.last_nonce = nonce
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.encryption_key),
            modes.GCM(nonce),
            backend=self.backend
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Store tag for decryption
        self.last_tag = encryptor.tag
        
        # Combine nonce + ciphertext + tag
        return nonce + ciphertext + self.last_tag
    
    def _stream_encrypt(self, data):
        """Custom stream cipher layer"""
        # Generate stream key
        stream_key = hashlib.sha512(self.encryption_key + b'stream_layer').digest()
        
        # Simple stream cipher
        encrypted = bytearray()
        key_index = 0
        
        for byte in data:
            encrypted.append(byte ^ stream_key[key_index % len(stream_key)])
            key_index = (key_index + 1) % len(stream_key)
        
        return bytes(encrypted)
    
    def _generate_decryption_code(self):
        """Generate code for decrypting the payload"""
        decryption_template = """
def _decrypt_payload(encrypted_data, key, salt, nonce, tag):
    import hashlib
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    
    backend = default_backend()
    
    # Derive decryption key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=backend
    )
    
    decryption_key = kdf.derive(key.encode() if isinstance(key, str) else key)
    
    # Layer 3: Reverse custom stream cipher
    stream_key = hashlib.sha512(decryption_key + b'stream_layer').digest()
    decrypted = bytearray()
    key_index = 0
    
    for byte in encrypted_data:
        decrypted.append(byte ^ stream_key[key_index % len(stream_key)])
        key_index = (key_index + 1) % len(stream_key)
    
    current_data = bytes(decrypted)
    
    # Layer 2: AES-256-GCM decryption
    nonce_len = 12
    tag_len = 16
    
    actual_nonce = current_data[:nonce_len]
    ciphertext = current_data[nonce_len:-tag_len]
    actual_tag = current_data[-tag_len:]
    
    cipher = Cipher(
        algorithms.AES(decryption_key),
        modes.GCM(actual_nonce),
        backend=backend
    )
    
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(ciphertext) + decryptor.finalize_with_tag(actual_tag)
    
    # Layer 1: Reverse XOR obfuscation
    xor_key = hashlib.sha256(decryption_key + b'xor_layer').digest()
    final_data = bytearray()
    
    for i, byte in enumerate(decrypted):
        final_data.append(byte ^ xor_key[i % len(xor_key)])
    
    return bytes(final_data)
"""
        return decryption_template
    
    def get_key_data(self):
        """Get encryption key data for wrapper generation"""
        return {
            'key': base64.b64encode(self.master_key).decode('utf-8'),
            'salt': base64.b64encode(self.salt).decode('utf-8'),
            'nonce': base64.b64encode(self.last_nonce).decode('utf-8') if self.last_nonce else '',
            'tag': base64.b64encode(self.last_tag).decode('utf-8') if self.last_tag else ''
        }
    
    def create_secure_loader(self, encrypted_data):
        """Create a secure loader for encrypted code"""
        loader_code = f'''
import base64
import marshal
import hashlib
import sys
import os

# Integrity check
def _verify_integrity():
    """Verify the integrity of this file"""
    current_file = __file__
    if os.path.exists(current_file):
        with open(current_file, 'rb') as f:
            content = f.read()
        
        # Simple integrity check
        expected_patterns = [b'_decrypt_payload', b'_verify_integrity', b'base64']
        for pattern in expected_patterns:
            if pattern not in content:
                sys.exit(1)

def _anti_debug_check():
    """Basic anti-debugging check"""
    import psutil
    
    # Check for debugger processes
    debugger_names = ['gdb', 'lldb', 'pdb', 'windbg', 'x64dbg']
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() in debugger_names:
            sys.exit(1)

def _execute_protected_code():
    """Execute the protected code"""
    try:
        _verify_integrity()
        _anti_debug_check()
        
        # Decryption logic would be inserted here
        # This is a placeholder for the actual implementation
        
        encrypted_payload = {encrypted_data}
        
        # Decrypt and execute
        decrypted_bytecode = _decrypt_payload(
            base64.b64decode(encrypted_payload['data']),
            "{self.get_key_data()['key']}",
            base64.b64decode("{self.get_key_data()['salt']}"),
            base64.b64decode("{self.get_key_data()['nonce']}"),
            base64.b64decode("{self.get_key_data()['tag']}")
        )
        
        code_obj = marshal.loads(decrypted_bytecode)
        exec(code_obj, globals())
        
    except Exception:
        sys.exit(1)

{self._generate_decryption_code()}

if __name__ == "__main__":
    _execute_protected_code()
'''
        
        return loader_code


class KeyManager:
    """Manage encryption keys and their derivation"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_key_from_environment(self):
        """Generate key based on system environment"""
        # Collect system information
        system_info = [
            os.uname().machine if hasattr(os, 'uname') else 'unknown',
            str(os.getpid()),
            os.getcwd(),
        ]
        
        # Create deterministic but environment-specific key
        combined = ''.join(system_info).encode('utf-8')
        return hashlib.sha256(combined).digest()
    
    def obfuscate_key_in_code(self, key):
        """Obfuscate key storage in generated code"""
        # Split key into parts and reconstruct
        key_parts = [key[i:i+4] for i in range(0, len(key), 4)]
        
        obfuscated_parts = []
        for part in key_parts:
            encoded = base64.b64encode(part).decode('utf-8')
            obfuscated_parts.append(f"base64.b64decode('{encoded}')")
        
        reconstruction_code = " + ".join(obfuscated_parts)
        
        return f"({reconstruction_code})"


class PolymorphicEncryption:
    """Polymorphic encryption that changes its appearance"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.transformation_counter = 0
    
    def transform_encryption_code(self, encryption_code):
        """Transform encryption code to look different each time"""
        self.transformation_counter += 1
        
        # Apply various transformations
        transformations = [
            self._rename_variables,
            self._reorder_operations,
            self._add_dummy_operations,
            self._change_constants
        ]
        
        current_code = encryption_code
        for transform in transformations:
            current_code = transform(current_code)
        
        return current_code
    
    def _rename_variables(self, code):
        """Rename variables in encryption code"""
        # This would implement variable renaming in the encryption code
        # For now, return code as-is
        return code
    
    def _reorder_operations(self, code):
        """Reorder non-dependent operations"""
        # This would reorder operations that don't depend on each other
        return code
    
    def _add_dummy_operations(self, code):
        """Add operations that don't affect the result"""
        # Add dummy calculations that are optimized away
        dummy_ops = [
            "_ = 1 + 1 - 2",
            "_ = len('dummy') - 5",
            "_ = int(str(42))"
        ]
        
        # Insert random dummy operations
        lines = code.split('\n')
        for _ in range(3):
            insert_pos = len(lines) // 2
            lines.insert(insert_pos, f"    {secrets.choice(dummy_ops)}")
        
        return '\n'.join(lines)
    
    def _change_constants(self, code):
        """Change constant values while maintaining functionality"""
        # This would replace constants with equivalent expressions
        return code
