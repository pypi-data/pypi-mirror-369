"""
Core encryption and obfuscation engine
Implements multi-layer encryption with complete content obfuscation
"""

import os
import secrets
import hashlib
import base64
import binascii
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from .auth import PasswordManager
from .utils.encoder import MultiLayerEncoder
from .utils.decoder import MultiLayerDecoder
from .utils.mapper import CharacterMapper


class PyObfusCrypt:
    """Main obfuscation engine with complete content protection"""
    
    def __init__(self):
        self.password_manager = PasswordManager()
        self.encoder = MultiLayerEncoder()
        self.decoder = MultiLayerDecoder()
        self.mapper = CharacterMapper()
        
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
    
    def encrypt_file(self, input_path: str, output_path: str, password: str | None = None) -> bool:
        """
        Encrypt Python file with complete obfuscation
        Returns True if successful, False otherwise
        """
        try:
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
            
            # Step 4: Apply multiple layers of obfuscation for complete unreadability
            import base64
            import zlib
            
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
    
    def decrypt_file(self, input_path: str, output_path: str, password: str | None = None) -> bool:
        """
        Decrypt obfuscated Python file
        Returns True if successful, False otherwise
        """
        try:
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
            encoded_data = obfuscated_data[header_size:-footer_size]
            
            # Step 2: Reverse the obfuscation layers
            import base64
            import zlib
            
            # Reverse Layer 4: Final base64
            data = base64.b64decode(encoded_data)
            
            # Reverse Layer 3: Second compression
            data = zlib.decompress(data)
            
            # Reverse Layer 2: Base64 encoding
            data = base64.b64decode(data)
            
            # Reverse Layer 1: First compression
            decoded_data = zlib.decompress(data)
            
            # Step 4: Extract metadata
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
    
    def _add_random_noise(self, data: bytes) -> bytes:
        """Add random noise and padding to make output completely unrecognizable"""
        # Add deterministic but seemingly random header/footer
        header_size = 32 + (len(data) % 16)  # Deterministic based on data length
        footer_size = 24 + (len(data) % 12)
        
        # Generate pseudo-random but reproducible noise
        header = secrets.token_bytes(header_size)
        footer = secrets.token_bytes(footer_size)
        
        # Store original data length for reliable extraction
        data_length = len(data).to_bytes(4, 'big')
        
        # Simple but effective obfuscation: just add padding around data
        # Format: header + header_size + data_length + data + footer_size + footer
        final_data = (header + 
                     header_size.to_bytes(2, 'big') + 
                     data_length + 
                     data + 
                     footer_size.to_bytes(2, 'big') + 
                     footer)
        
        return final_data
    
    def _remove_random_noise(self, data: bytes) -> bytes:
        """Remove random noise and padding"""
        try:
            # Extract footer size from end
            footer_size = int.from_bytes(data[-2:], 'big')
            
            # Calculate positions
            footer_start = len(data) - footer_size - 2
            header_size_pos = footer_start - 2
            header_size = int.from_bytes(data[header_size_pos:footer_start], 'big')
            
            # Extract data length and actual data
            data_length_pos = header_size + 2
            data_length = int.from_bytes(data[data_length_pos:data_length_pos + 4], 'big')
            
            # Extract the actual data
            data_start = data_length_pos + 4
            data_end = data_start + data_length
            
            actual_data = data[data_start:data_end]
            
            return actual_data
            
        except Exception as e:
            # Fallback: try to extract data without noise removal
            print(f"Debug: Noise removal failed: {e}")
            if len(data) > 100:
                extracted = data[50:-50]
                # Ensure even length for hex
                if len(extracted) % 2 == 1:
                    extracted = extracted[:-1]
                return extracted
            return data
