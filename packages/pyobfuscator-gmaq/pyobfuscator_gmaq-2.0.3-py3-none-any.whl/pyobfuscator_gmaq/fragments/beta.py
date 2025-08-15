"""
Beta fragment - Second component of distributed password storage
Security Level: High - Fragment 2/5
"""

import hashlib
import base64


def get_fragment():
    """Retrieve beta fragment of master password"""
    # Base fragment data
    base_data = "GMAQ_BETA_SECURITY_2023_ADVANCED_OBFUSCATION_FRAGMENT_PART_002_DISTRIBUTED_PASSWORD_SYSTEM"
    
    # Generate deterministic fragment using different method
    fragment_hash = hashlib.sha512(base_data.encode()).hexdigest()
    
    # Apply base64 encoding and decoding for additional obfuscation
    encoded = base64.b64encode(fragment_hash[:150].encode()).decode()
    
    # Character manipulation
    obfuscated = ""
    for i, char in enumerate(encoded):
        # Different shifting pattern than alpha
        if i % 2 == 0:
            shifted = chr((ord(char) + 7) % 256)
        else:
            shifted = chr((ord(char) - 3) % 256)
        obfuscated += shifted
        
    # Return exactly 100 characters
    final_fragment = obfuscated[:100]
    
    return final_fragment


def verify_fragment():
    """Verify fragment integrity"""
    fragment = get_fragment()
    return len(fragment) == 100 and isinstance(fragment, str)


# Decoy functions and data
def _encryption_helper():
    """Dummy encryption helper"""
    dummy_key = hashlib.sha256(b"dummy_key_beta").hexdigest()
    return dummy_key


def _access_control():
    """Dummy access control"""
    return {'authorized': True, 'level': 'beta'}


# Additional metadata noise
BETA_CONFIG = {
    'algorithm': 'sha512',
    'encoding': 'base64',
    'shift_pattern': 'alternating',
    'fragment_id': 'beta_002'
}

# Dummy constants
SECURITY_CONSTANTS = [
    "BETA_SECURITY_LAYER",
    "FRAGMENT_VALIDATION",
    "OBFUSCATION_LEVEL_2"
]
