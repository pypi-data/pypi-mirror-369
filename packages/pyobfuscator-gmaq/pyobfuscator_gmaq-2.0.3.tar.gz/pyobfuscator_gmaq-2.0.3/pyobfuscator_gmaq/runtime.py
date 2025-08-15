"""
Runtime decryption module for encrypted Python files
Handles automatic decryption and execution
"""

import base64
import hashlib
import sys
import importlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os


def decrypt_and_execute(encrypted_payload):
    """
    Runtime decryption and execution function
    This function is embedded into encrypted files for automatic decryption
    """
    
    def get_master_password():
        """Reconstruct master password from library fragments"""
        fragments = {}
        fragment_names = ['alpha', 'beta', 'gamma', 'delta', 'epsilon']
        
        for name in fragment_names:
            try:
                # Try to import fragment module
                module = importlib.import_module(f'pyobfuscator_gmaq.fragments.{name}')
                if hasattr(module, 'get_fragment'):
                    fragments[name] = module.get_fragment()
                else:
                    fragments[name] = get_fallback_fragment(name)
            except ImportError:
                # Use fallback if module not available
                fragments[name] = get_fallback_fragment(name)
        
        # Combine fragments in correct order
        master_password = ""
        for name in fragment_names:
            master_password += fragments.get(name, "")
            
        # Ensure exactly 500 characters
        if len(master_password) < 500:
            padding_seed = "GMAQ_PADDING_SECURITY_2023"
            while len(master_password) < 500:
                padding_hash = hashlib.sha256((padding_seed + str(len(master_password))).encode()).hexdigest()
                master_password += padding_hash[:min(64, 500 - len(master_password))]
                
        return master_password[:500]
    
    def get_fallback_fragment(fragment_name):
        """Generate fallback fragment when library not available"""
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
        """Derive AES key from master password"""
        salt = b'GMAQ_SECURITY_SALT_2023_OBFUSCATOR_FIXED'
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return key[:32]
    
    def decrypt_data(encrypted_data, key):
        """Decrypt data using AES-256-CBC"""
        # Fixed IV for deterministic decryption
        iv = hashlib.sha256(b'GMAQ_FIXED_IV_2023_DETERMINISTIC').digest()[:16]
        
        try:
            # Decode base64 encrypted data
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Create cipher and decrypt
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(encrypted_bytes) + decryptor.finalize()
            
            # Remove padding
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(padded_data)
            data += unpadder.finalize()
            
            return data.decode('utf-8')
            
        except Exception as e:
            raise DecryptionError(f"Failed to decrypt data: {e}")
    
    # Main decryption and execution logic
    try:
        # Get master password from fragments
        master_password = get_master_password()
        
        # Derive decryption key
        key = derive_key(master_password)
        
        # Decrypt the payload
        decrypted_code = decrypt_data(encrypted_payload, key)
        
        # Execute the decrypted Python code
        compiled_code = compile(decrypted_code, '<encrypted_file>', 'exec')
        exec(compiled_code, globals())
        
    except Exception as e:
        print(f"PyObfuscator-GMAQ: Decryption failed - {e}")
        print("Please ensure the pyobfuscator-gmaq library is properly installed.")
        sys.exit(1)


class DecryptionError(Exception):
    """Custom exception for decryption failures"""
    pass


def validate_encrypted_file(file_path):
    """Validate if a file is properly encrypted with PyObfuscator-GMAQ"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Check for required markers
        markers = [
            'PyObfuscator-GMAQ',
            'ENCRYPTED_PAYLOAD',
            'decrypt_and_execute'
        ]
        
        return all(marker in content for marker in markers)
        
    except Exception:
        return False


def get_runtime_info():
    """Get runtime information for debugging"""
    return {
        'version': '2.0.3',
        'backend': 'cryptography',
        'algorithm': 'AES-256-CBC',
        'key_derivation': 'PBKDF2-SHA256',
        'fragment_count': 5,
        'password_length': 500
    }
