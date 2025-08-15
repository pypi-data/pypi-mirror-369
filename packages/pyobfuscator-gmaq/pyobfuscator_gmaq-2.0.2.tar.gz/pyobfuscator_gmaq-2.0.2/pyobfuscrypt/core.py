
"""
Core encryption and obfuscation engine
Implements multi-layer encryption with complete content obfuscation
"""

import os
import secrets
import hashlib
import base64
import binascii
import zlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


class PyObfusCrypt:
    """Main obfuscation engine with complete content protection"""
    
    def __init__(self):
        from .auth import PasswordManager
        self.password_manager = PasswordManager()
        
    def _generate_key(self, password: str, salt: bytes) -> bytes:
        """Generate encryption key from password and salt"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)[:32]
    
    def _aes_encrypt(self, data: bytes, key: bytes) -> tuple:
        """AES-256 encryption with random IV"""
        iv = secrets.token_bytes(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Add PKCS7 padding
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return encrypted, iv
    
    def _aes_decrypt(self, encrypted_data: bytes, key: bytes, iv: bytes) -> bytes:
        """AES-256 decryption"""
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Remove PKCS7 padding
        unpadder = padding.PKCS7(128).unpadder()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
        
        return decrypted
    
    def encrypt_file(self, input_path: str, output_path: str, password: str = None) -> bool:
        """
        Encrypt Python file with complete obfuscation
        Returns True if successful, False otherwise
        """
        try:
            # Check if input file exists
            if not os.path.exists(input_path):
                print(f"❌ Encryption failed: [Errno 2] No such file or directory: '{input_path}'")
                return False
            
            # Verify password
            if password is None:
                password = self.password_manager.get_master_password()
            
            if not self.password_manager.verify_password(password):
                print("❌ Invalid password")
                return False
            
            # Read source file
            with open(input_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Generate salt and key
            salt = secrets.token_bytes(32)
            key = self._generate_key(password, salt)
            
            # Step 1: Convert to bytes
            data_bytes = source_code.encode('utf-8')
            
            # Step 2: AES encryption
            encrypted_data, iv = self._aes_encrypt(data_bytes, key)
            
            # Step 3: Add metadata (salt + iv + encrypted_data)
            full_data = salt + iv + encrypted_data
            
            # Step 4: Apply multiple layers of obfuscation
            # Layer 1: Compression to eliminate patterns
            compressed = zlib.compress(full_data, 9)
            
            # Layer 2: Base64 encoding
            encoded = base64.b64encode(compressed)
            
            # Layer 3: Second compression pass for extra obfuscation
            double_compressed = zlib.compress(encoded, 9) 
            
            # Layer 4: Final base64 encoding
            final_encoded = base64.b64encode(double_compressed)
            
            # Step 5: Add simple padding for additional obfuscation
            header = secrets.token_bytes(64)
            footer = secrets.token_bytes(48)
            final_data = header + final_encoded + footer
            
            # Write completely obfuscated file
            with open(output_path, 'wb') as f:
                f.write(final_data)
            
            print(f"✅ File encrypted successfully: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Encryption failed: {str(e)}")
            return False
    
    def decrypt_file(self, input_path: str, output_path: str, password: str = None) -> bool:
        """
        Decrypt obfuscated Python file
        Returns True if successful, False otherwise
        """
        try:
            # Check if input file exists
            if not os.path.exists(input_path):
                print(f"❌ Decryption failed: [Errno 2] No such file or directory: '{input_path}'")
                return False
            
            # Verify password
            if password is None:
                password = self.password_manager.get_master_password()
            
            if not self.password_manager.verify_password(password):
                print("❌ Invalid password")
                return False
            
            # Read obfuscated file
            with open(input_path, 'rb') as f:
                obfuscated_data = f.read()
            
            # Step 1: Remove simple padding (header and footer)
            header_size = 64
            footer_size = 48
            
            if len(obfuscated_data) < header_size + footer_size:
                print("❌ Decryption failed: File too small or corrupted")
                return False
                
            encoded_data = obfuscated_data[header_size:-footer_size]
            
            # Step 2: Reverse the obfuscation layers
            # Reverse Layer 4: Final base64
            data = base64.b64decode(encoded_data)
            
            # Reverse Layer 3: Second compression
            data = zlib.decompress(data)
            
            # Reverse Layer 2: Base64 encoding
            data = base64.b64decode(data)
            
            # Reverse Layer 1: First compression
            decoded_data = zlib.decompress(data)
            
            # Step 4: Extract metadata
            if len(decoded_data) < 48:
                print("❌ Decryption failed: Invalid file format")
                return False
                
            salt = decoded_data[:32]
            iv = decoded_data[32:48]
            encrypted_data = decoded_data[48:]
            
            # Step 5: Generate key and decrypt
            key = self._generate_key(password, salt)
            decrypted_bytes = self._aes_decrypt(encrypted_data, key, iv)
            
            # Step 6: Convert back to source code
            source_code = decrypted_bytes.decode('utf-8')
            
            # Write decrypted file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(source_code)
            
            print(f"✅ File decrypted successfully: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Decryption failed: {str(e)}")
            return False
