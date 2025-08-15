
"""
Authentication and password management system
Handles distributed password fragments and verification
"""

import os
import hashlib


class PasswordManager:
    """Handles password management and verification"""
    
    def __init__(self):
        self.master_password = "@G_M_A_Q-10-11"
        
    def get_master_password(self) -> str:
        """Get master password from fragments or default"""
        try:
            # Try to reconstruct from fragments
            fragments = []
            for i in range(1, 6):
                fragment_path = f"pyobfuscrypt/fragments/f{i}.py"
                if os.path.exists(fragment_path):
                    with open(fragment_path, 'r') as f:
                        content = f.read()
                        # Extract fragment from file content
                        if f"FRAGMENT_{i}" in content:
                            start = content.find(f'"{i}') + 1
                            end = content.find('"', start)
                            if start > 0 and end > start:
                                fragments.append(content[start:end])
            
            # If we have enough fragments, reconstruct
            if len(fragments) >= 3:
                return ''.join(fragments)
            
        except Exception:
            pass
        
        # Return default password
        return self.master_password
    
    def verify_password(self, password: str) -> bool:
        """Verify provided password"""
        master = self.get_master_password()
        return password == master
    
    def hash_password(self, password: str) -> str:
        """Generate SHA-256 hash of password"""
        return hashlib.sha256(password.encode()).hexdigest()
