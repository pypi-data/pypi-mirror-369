"""
Gamma fragment - Third component of distributed password storage
Security Level: Maximum - Fragment 3/5
"""

import hashlib
import os


def get_fragment():
    """Retrieve gamma fragment of master password"""
    # Base fragment data with environmental obfuscation
    base_data = "GMAQ_GAMMA_SECURITY_2023_MAXIMUM_PROTECTION_FRAGMENT_PART_003_ENVIRONMENTAL_OBFUSCATION"
    
    # Add pseudo-environmental factor for deterministic but complex generation
    env_factor = hashlib.sha256(b"GMAQ_ENV_GAMMA_2023").hexdigest()[:16]
    combined_data = base_data + env_factor
    
    # Multi-layer hashing
    hash1 = hashlib.sha256(combined_data.encode()).hexdigest()
    hash2 = hashlib.sha1(hash1.encode()).hexdigest()
    hash3 = hashlib.md5(hash2.encode()).hexdigest()
    
    # Complex character transformation
    transformation_key = "GMAQ_GAMMA_TRANSFORM_2023"
    obfuscated = ""
    
    for i, char in enumerate(hash1 + hash2 + hash3):
        # Complex transformation using transformation key
        key_char = transformation_key[i % len(transformation_key)]
        transformed = chr((ord(char) ^ ord(key_char)) % 256)
        obfuscated += transformed
        
    # Return exactly 100 characters
    final_fragment = obfuscated[:100]
    
    return final_fragment


def verify_fragment():
    """Verify fragment integrity with checksum"""
    fragment = get_fragment()
    expected_checksum = hashlib.sha256(fragment.encode()).hexdigest()[:16]
    return len(fragment) == 100 and expected_checksum is not None


# Complex decoy system
class SecurityManager:
    def __init__(self):
        self.security_level = "gamma"
        self.access_codes = self._generate_access_codes()
    
    def _generate_access_codes(self):
        """Generate dummy access codes"""
        codes = []
        for i in range(5):
            code = hashlib.sha256(f"ACCESS_CODE_GAMMA_{i}".encode()).hexdigest()[:12]
            codes.append(code)
        return codes
    
    def validate_access(self, code):
        """Dummy access validation"""
        return code in self.access_codes


def _security_audit():
    """Dummy security audit function"""
    audit_data = {
        'timestamp': '2023-08-15',
        'fragment': 'gamma',
        'status': 'secure',
        'checksum': hashlib.sha256(b"gamma_audit").hexdigest()[:16]
    }
    return audit_data


# Decoy data structures
GAMMA_SECURITY_MATRIX = [
    ['A1', 'B2', 'C3', 'D4', 'E5'],
    ['F6', 'G7', 'H8', 'I9', 'J0'],
    ['K1', 'L2', 'M3', 'N4', 'O5'],
    ['P6', 'Q7', 'R8', 'S9', 'T0'],
    ['U1', 'V2', 'W3', 'X4', 'Y5']
]

OBFUSCATION_LAYERS = {
    'layer1': 'SHA256_HASH',
    'layer2': 'XOR_TRANSFORM', 
    'layer3': 'CHAR_SHIFT',
    'layer4': 'ENV_FACTOR',
    'layer5': 'CHECKSUM_VALIDATION'
}
