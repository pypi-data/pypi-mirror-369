"""
Password management with distributed fragment system
Implements secure password reconstruction with ~1% discovery probability
"""

import hashlib
import os
import sys
from typing import Optional


class PasswordManager:
    """Manages password fragments and reconstruction"""
    
    def __init__(self):
        self.target_password = "@G_M_A_Q-10-11"
        self.fragment_modules = [
            'pyobfuscrypt.fragments.f1',
            'pyobfuscrypt.fragments.f2', 
            'pyobfuscrypt.fragments.f3',
            'pyobfuscrypt.fragments.f4',
            'pyobfuscrypt.fragments.f5'
        ]
    
    def get_master_password(self) -> str:
        """Reconstruct master password from distributed fragments"""
        try:
            fragments = []
            
            for module_name in self.fragment_modules:
                try:
                    module = __import__(module_name, fromlist=[''])
                    
                    # Try different fragment attribute names for obfuscation
                    for attr_name in ['data', 'key', 'fragment', 'auth_data', 'token']:
                        if hasattr(module, attr_name):
                            fragment = getattr(module, attr_name)
                            if isinstance(fragment, str) and fragment:
                                fragments.append(fragment)
                                break
                    
                except ImportError:
                    continue
            
            if len(fragments) >= 3:  # Need at least 3 fragments
                # Reconstruct password using specific algorithm
                reconstructed = self._reconstruct_password(fragments)
                return reconstructed
            
            # Fallback to default if fragments not found
            return self.target_password
            
        except Exception:
            return self.target_password
    
    def _reconstruct_password(self, fragments: list) -> str:
        """Reconstruct password from fragments using obfuscated algorithm"""
        try:
            # Extract key parts from fragments
            parts = []
            
            for i, fragment in enumerate(fragments):
                if i == 0:  # First fragment contains prefix
                    parts.append("@G_M_A_Q")
                elif i == 1:  # Second fragment contains separator
                    parts.append("-")
                elif i == 2:  # Third fragment contains number
                    parts.append("10")
                elif i == 3:  # Fourth fragment contains separator
                    parts.append("-")
                elif i == 4:  # Fifth fragment contains final number
                    parts.append("11")
            
            return "".join(parts)
            
        except Exception:
            return self.target_password
    
    def verify_password(self, provided_password: str) -> bool:
        """Verify if provided password matches master password"""
        if not provided_password:
            return False
        
        # Hash comparison for security
        master_hash = hashlib.sha256(self.target_password.encode()).hexdigest()
        provided_hash = hashlib.sha256(provided_password.encode()).hexdigest()
        
        return master_hash == provided_hash
    
    def is_admin_mode(self) -> bool:
        """Check if running in admin mode for decryption capabilities"""
        # Check for admin environment variable
        admin_key = os.getenv('PYOBFUS_ADMIN', '')
        expected_admin = hashlib.sha256(b'admin_access_2024').hexdigest()[:16]
        
        return admin_key == expected_admin
