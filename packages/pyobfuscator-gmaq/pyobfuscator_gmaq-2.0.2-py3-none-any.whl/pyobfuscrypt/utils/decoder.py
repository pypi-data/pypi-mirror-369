"""
Multi-layer decoder for reversing obfuscation
Implements decoding layers to restore encrypted content
"""

import base64
import binascii
import zlib


class MultiLayerDecoder:
    """Handles multi-layer decoding for content restoration"""

    def __init__(self):
        pass

    def reverse_all_layers(self, encoded_data: str) -> bytes:
        """Reverse all encoding layers"""
        # Reverse Layer 5: Final base64 decoding
        data = base64.b64decode(encoded_data.encode('ascii'))

        # Reverse Layer 4: Hexadecimal decoding
        data = binascii.unhexlify(data)

        # Reverse Layer 3: Standard base64 decoding
        data = base64.b64decode(data)

        # Reverse Layer 2: Decompression
        data = zlib.decompress(data)

        # Reverse Layer 1: URL-safe base64 decoding
        data = base64.urlsafe_b64decode(data)

        return data