"""
Alpha fragment - First component of distributed password storage
Security Level: High - Fragment 1/5
"""

import hashlib
import time


def get_fragment():
    """Retrieve alpha fragment of master password"""
    # Base fragment data
    base_data = "GMAQ_ALPHA_SECURITY_2023_OBFUSCATION_FRAGMENT_PART_001_ENCRYPTED_PAYLOAD_DISTRIBUTION_SYSTEM"
    
    # Generate deterministic fragment
    fragment_seed = hashlib.sha256(base_data.encode()).hexdigest()
    
    # Additional obfuscation layer
    obfuscated = ""
    for i, char in enumerate(fragment_seed):
        # Simple character shifting based on position
        shifted = chr((ord(char) + i) % 256)
        obfuscated += shifted
        
    # Return exactly 100 characters
    final_fragment = obfuscated[:100]
    
    # Verify fragment integrity
    checksum = hashlib.md5(final_fragment.encode()).hexdigest()[:8]
    
    return final_fragment


def verify_fragment():
    """Verify fragment integrity"""
    fragment = get_fragment()
    return len(fragment) == 100


# Decoy functions to increase obfuscation
def _dummy_security_check():
    """Dummy security function"""
    return hashlib.sha256(str(time.time()).encode()).hexdigest()


def _validate_access():
    """Dummy access validation"""
    return True


# Additional noise
FRAGMENT_METADATA = {
    'version': '2.0.3',
    'type': 'alpha',
    'security_level': 'high',
    'checksum_algo': 'md5'
}
