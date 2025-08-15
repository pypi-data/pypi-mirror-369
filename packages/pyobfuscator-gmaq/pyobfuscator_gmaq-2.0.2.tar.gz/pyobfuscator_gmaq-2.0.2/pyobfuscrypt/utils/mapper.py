"""
Character mapper for final obfuscation layer
Implements custom character mapping for additional security
"""

import secrets
import string


class CharacterMapper:
    """Handles character mapping for obfuscation"""

    def __init__(self):
        self.mapping_table = None
        self.reverse_table = None

    def create_mapping(self, seed: str = None) -> dict:
        """Create character mapping table"""
        chars = string.ascii_letters + string.digits + "+/="
        shuffled_chars = list(chars)

        if seed:
            # Use seed for reproducible mapping
            import random
            random.seed(seed)
            random.shuffle(shuffled_chars)
        else:
            # Random mapping
            secrets.SystemRandom().shuffle(shuffled_chars)

        self.mapping_table = dict(zip(chars, shuffled_chars))
        self.reverse_table = dict(zip(shuffled_chars, chars))

        return self.mapping_table

    def map_string(self, data: str) -> str:
        """Map string using character table"""
        if not self.mapping_table:
            return data

        return ''.join(self.mapping_table.get(c, c) for c in data)

    def unmap_string(self, data: str) -> str:
        """Reverse map string using character table"""
        if not self.reverse_table:
            return data

        return ''.join(self.reverse_table.get(c, c) for c in data)
"""
Character mapping utility for final obfuscation layer
Provides custom character substitution for pattern elimination
"""

import secrets
import string


class CharacterMapper:
    """Handles custom character mapping for final obfuscation"""
    
    def __init__(self):
        self.mapping_table = self._generate_mapping_table()
        self.reverse_table = {v: k for k, v in self.mapping_table.items()}
    
    def _generate_mapping_table(self) -> dict:
        """Generate a custom character mapping table"""
        chars = string.ascii_letters + string.digits + "+=/"
        shuffled = list(chars)
        
        # Deterministic shuffle based on a seed for reproducibility
        seed = "PyObfusCrypt_Mapping_Seed_2024"
        random_gen = secrets.SystemRandom()
        random_gen.seed(hash(seed) % (2**32))
        
        for i in range(len(shuffled) - 1, 0, -1):
            j = random_gen.randint(0, i)
            shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
        
        return dict(zip(chars, shuffled))
    
    def map_characters(self, data: str) -> str:
        """Apply character mapping to data"""
        return ''.join(self.mapping_table.get(char, char) for char in data)
    
    def unmap_characters(self, data: str) -> str:
        """Reverse character mapping"""
        return ''.join(self.reverse_table.get(char, char) for char in data)
