"""
Core obfuscation engine for PyObfuscator-GMAQ
Handles encryption/decryption with distributed password storage
"""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import importlib.util
import inspect


class PyObfuscatorGMAQ:
    """Main obfuscation class with distributed password management"""
    
    def __init__(self):
        self.backend = default_backend()
        self._master_key = None
        
    def _get_password_fragments(self):
        """Retrieve password fragments from distributed storage"""
        fragments = {}
        fragment_modules = ['alpha', 'beta', 'gamma', 'delta', 'epsilon']
        
        for module_name in fragment_modules:
            try:
                module = importlib.import_module(f'pyobfuscator_gmaq.fragments.{module_name}')
                if hasattr(module, 'get_fragment'):
                    fragments[module_name] = module.get_fragment()
            except ImportError:
                # Fragment not found, use fallback
                fragments[module_name] = self._get_fallback_fragment(module_name)
                
        return fragments
    
    def _get_fallback_fragment(self, fragment_name):
        """Generate fallback fragments based on deterministic algorithm"""
        fallback_seeds = {
            'alpha': 'GMAQ_ALPHA_SEED_2023_SECURITY_FRAGMENT_001',
            'beta': 'GMAQ_BETA_SEED_2023_SECURITY_FRAGMENT_002', 
            'gamma': 'GMAQ_GAMMA_SEED_2023_SECURITY_FRAGMENT_003',
            'delta': 'GMAQ_DELTA_SEED_2023_SECURITY_FRAGMENT_004',
            'epsilon': 'GMAQ_EPSILON_SEED_2023_SECURITY_FRAGMENT_005'
        }
        
        seed = fallback_seeds.get(fragment_name, 'DEFAULT_SEED')
        # Generate deterministic fragment from seed
        fragment_hash = hashlib.sha256(seed.encode()).hexdigest()
        return fragment_hash[:100]  # 100 chars per fragment
    
    def _reconstruct_master_password(self):
        """Reconstruct the 500-character master password from fragments"""
        fragments = self._get_password_fragments()
        
        # Combine fragments in specific order
        master_password = ""
        order = ['alpha', 'beta', 'gamma', 'delta', 'epsilon']
        
        for fragment_name in order:
            master_password += fragments.get(fragment_name, "")
            
        # Ensure exactly 500 characters
        if len(master_password) < 500:
            # Pad with deterministic data
            padding_seed = "GMAQ_PADDING_SECURITY_2023"
            while len(master_password) < 500:
                padding_hash = hashlib.sha256((padding_seed + str(len(master_password))).encode()).hexdigest()
                master_password += padding_hash[:min(64, 500 - len(master_password))]
                
        return master_password[:500]  # Truncate to exactly 500 chars
    
    def _derive_key(self, password):
        """Derive AES key from password using deterministic method"""
        # Use PBKDF2 with fixed salt for deterministic results
        salt = b'GMAQ_SECURITY_SALT_2023_OBFUSCATOR_FIXED'
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return key[:32]  # 256-bit key
    
    def encrypt_file(self, input_path, output_path):
        """Encrypt Python file with embedded decryption runtime"""
        # Read source file
        with open(input_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
            
        # Get master password and derive key
        master_password = self._reconstruct_master_password()
        key = self._derive_key(master_password)
        
        # Encrypt source code
        encrypted_data = self._encrypt_data(source_code.encode('utf-8'), key)
        
        # Create encrypted file with runtime
        self._create_encrypted_file(encrypted_data, output_path)
        
        print(f"Successfully encrypted {input_path} -> {output_path}")
    
    def _encrypt_data(self, data, key):
        """Encrypt data using AES-256-CBC"""
        # Fixed IV for deterministic encryption
        iv = hashlib.sha256(b'GMAQ_FIXED_IV_2023_DETERMINISTIC').digest()[:16]
        
        # Pad data
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data)
        padded_data += padder.finalize()
        
        # Encrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        return base64.b64encode(encrypted_data).decode('ascii')
    
    def _create_encrypted_file(self, encrypted_data, output_path):
        """Create encrypted Python file with embedded runtime"""
        runtime_code = self._get_runtime_template()
        
        encrypted_file_content = f'''#!/usr/bin/env python3
"""
Encrypted Python file generated by PyObfuscator-GMAQ v2.0.3
This file contains obfuscated code that will be automatically decrypted at runtime.
"""

# Encrypted payload
ENCRYPTED_PAYLOAD = """{encrypted_data}"""

# Runtime decryption and execution
{runtime_code}

# Execute the decrypted code
if __name__ == "__main__":
    decrypt_and_execute(ENCRYPTED_PAYLOAD)
'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(encrypted_file_content)
            
        # Make executable
        os.chmod(output_path, 0o755)
    
    def _get_runtime_template(self):
        """Get the runtime decryption template"""
        # Always use the inline runtime for consistency
        return '''
def decrypt_and_execute(encrypted_payload):
    """Runtime decryption and execution"""
    import base64
    import hashlib
    import sys
    import importlib
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.backends import default_backend
    
    def get_master_password():
        """Reconstruct master password from library fragments"""
        fragments = {}
        fragment_names = ['alpha', 'beta', 'gamma', 'delta', 'epsilon']
        
        for name in fragment_names:
            try:
                module = importlib.import_module(f'pyobfuscator_gmaq.fragments.{name}')
                if hasattr(module, 'get_fragment'):
                    fragments[name] = module.get_fragment()
                else:
                    fragments[name] = get_fallback_fragment(name)
            except ImportError:
                fragments[name] = get_fallback_fragment(name)
        
        # Combine fragments
        master_password = ""
        for name in fragment_names:
            master_password += fragments.get(name, "")
            
        # Pad to 500 characters
        if len(master_password) < 500:
            padding_seed = "GMAQ_PADDING_SECURITY_2023"
            while len(master_password) < 500:
                padding_hash = hashlib.sha256((padding_seed + str(len(master_password))).encode()).hexdigest()
                master_password += padding_hash[:min(64, 500 - len(master_password))]
                
        return master_password[:500]
    
    def get_fallback_fragment(fragment_name):
        """Generate fallback fragment"""
        fallback_seeds = {
            'alpha': 'GMAQ_ALPHA_SEED_2023_SECURITY_FRAGMENT_001',
            'beta': 'GMAQ_BETA_SEED_2023_SECURITY_FRAGMENT_002', 
            'gamma': 'GMAQ_GAMMA_SEED_2023_SECURITY_FRAGMENT_003',
            'delta': 'GMAQ_DELTA_SEED_2023_SECURITY_FRAGMENT_004',
            'epsilon': 'GMAQ_EPSILON_SEED_2023_SECURITY_FRAGMENT_005'
        }
        
        seed = fallback_seeds.get(fragment_name, 'DEFAULT_SEED')
        fragment_hash = hashlib.sha256(seed.encode()).hexdigest()
        return fragment_hash[:100]
    
    def derive_key(password):
        """Derive AES key from password"""
        salt = b'GMAQ_SECURITY_SALT_2023_OBFUSCATOR_FIXED'
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return key[:32]
    
    def decrypt_data(encrypted_data, key):
        """Decrypt data using AES-256-CBC"""
        iv = hashlib.sha256(b'GMAQ_FIXED_IV_2023_DETERMINISTIC').digest()[:16]
        
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_bytes) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data)
        data += unpadder.finalize()
        
        return data.decode('utf-8')
    
    # Decrypt and execute
    try:
        master_password = get_master_password()
        key = derive_key(master_password)
        decrypted_code = decrypt_data(encrypted_payload, key)
        
        # Execute decrypted code
        exec(decrypted_code, globals())
        
    except Exception as e:
        print(f"Decryption failed: {e}")
        exit(1)
'''
