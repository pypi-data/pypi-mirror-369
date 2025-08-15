#!/usr/bin/env python3
"""
AdminGMAQ.py - Administrative interface for PyObfuscator-GMAQ
Version 2.0.3

This admin tool provides direct access to encryption functionality
and can be run from any directory to encrypt Python files.
"""

import os
import sys
import argparse
from pathlib import Path

# Try to import the library
try:
    from pyobfuscator_gmaq import PyObfuscatorGMAQ
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False
    print("Warning: pyobfuscator-gmaq library not installed")
    print("Install with: pip install pyobfuscator-gmaq")


class AdminGMAQ:
    """Administrative interface for PyObfuscator-GMAQ"""
    
    def __init__(self):
        self.version = "2.0.3"
        self.obfuscator = None
        
        if LIBRARY_AVAILABLE:
            self.obfuscator = PyObfuscatorGMAQ()
    
    def encrypt_file(self, input_path, output_path=None):
        """Encrypt a Python file"""
        
        if not LIBRARY_AVAILABLE:
            print("Error: PyObfuscator-GMAQ library not available")
            return False
            
        # Validate input file
        input_file = Path(input_path)
        if not input_file.exists():
            print(f"Error: Input file '{input_path}' not found")
            return False
            
        if not input_file.suffix == '.py':
            print(f"Error: Input file must be a Python (.py) file")
            return False
            
        # Generate output path if not provided
        if output_path is None:
            output_path = input_file.parent / f"{input_file.stem}_encrypted{input_file.suffix}"
        else:
            output_path = Path(output_path)
            
        print(f"AdminGMAQ v{self.version} - Encrypting Python File")
        print(f"Input:  {input_file.absolute()}")
        print(f"Output: {output_path.absolute()}")
        print("-" * 60)
        
        try:
            # Perform encryption
            self.obfuscator.encrypt_file(str(input_file), str(output_path))
            
            print("-" * 60)
            print("✓ Encryption completed successfully!")
            print(f"✓ Encrypted file: {output_path.absolute()}")
            print(f"✓ Run with: python3 {output_path}")
            print(f"✓ File size: {output_path.stat().st_size} bytes")
            
            return True
            
        except Exception as e:
            print(f"✗ Encryption failed: {e}")
            return False
    
    def info(self):
        """Display admin information"""
        print(f"AdminGMAQ v{self.version}")
        print("=" * 50)
        print("PyObfuscator-GMAQ Administrative Interface")
        print("")
        print("Features:")
        print("• Encrypt Python files with 500-character distributed password")
        print("• Automatic decryption runtime injection")
        print("• Cross-directory encryption support")
        print("• Deterministic encryption algorithm")
        print("")
        
        if LIBRARY_AVAILABLE:
            print("Library Status: ✓ Available")
            print("Backend: cryptography")
            print("Algorithm: AES-256-CBC")
            print("Key Derivation: PBKDF2-SHA256")
            print("Password Fragments: 5 distributed modules")
        else:
            print("Library Status: ✗ Not Available")
            print("Install: pip install pyobfuscator-gmaq")
    
    def validate_encrypted_file(self, file_path):
        """Validate an encrypted file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"Error: File '{file_path}' not found")
            return False
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for encryption markers
            markers = [
                'PyObfuscator-GMAQ',
                'ENCRYPTED_PAYLOAD',
                'decrypt_and_execute'
            ]
            
            found_markers = [marker for marker in markers if marker in content]
            
            print(f"File: {file_path.absolute()}")
            print(f"Size: {file_path.stat().st_size} bytes")
            print(f"Markers found: {len(found_markers)}/{len(markers)}")
            
            if len(found_markers) == len(markers):
                print("✓ Valid PyObfuscator-GMAQ encrypted file")
                print("✓ Can be executed directly")
                return True
            else:
                print("✗ Not a valid encrypted file")
                print(f"Missing markers: {set(markers) - set(found_markers)}")
                return False
                
        except Exception as e:
            print(f"Error validating file: {e}")
            return False
    
    def test_execution(self, encrypted_file_path):
        """Test execution of encrypted file"""
        file_path = Path(encrypted_file_path)
        
        if not file_path.exists():
            print(f"Error: Encrypted file '{file_path}' not found")
            return False
            
        print(f"Testing execution of: {file_path.absolute()}")
        print("Note: This will actually execute the encrypted file!")
        
        try:
            import subprocess
            result = subprocess.run([sys.executable, str(file_path)], 
                                  capture_output=True, text=True, timeout=30)
            
            print("Execution Result:")
            print(f"Return code: {result.returncode}")
            
            if result.stdout:
                print("STDOUT:")
                print(result.stdout)
                
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
                
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("✗ Execution timed out (30 seconds)")
            return False
        except Exception as e:
            print(f"✗ Execution test failed: {e}")
            return False


def main():
    """Main entry point for AdminGMAQ"""
    parser = argparse.ArgumentParser(
        description="AdminGMAQ v2.0.3 - PyObfuscator-GMAQ Administrative Interface"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Encrypt command
    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt a Python file')
    encrypt_parser.add_argument('input', help='Input Python file path')
    encrypt_parser.add_argument('output', nargs='?', help='Output encrypted file path (optional)')
    
    # Info command
    subparsers.add_parser('info', help='Display admin information')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate encrypted file')
    validate_parser.add_argument('file', help='Encrypted file path')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test encrypted file execution')
    test_parser.add_argument('file', help='Encrypted file path')
    
    args = parser.parse_args()
    
    admin = AdminGMAQ()
    
    if args.command == 'encrypt':
        admin.encrypt_file(args.input, args.output)
    elif args.command == 'info':
        admin.info()
    elif args.command == 'validate':
        admin.validate_encrypted_file(args.file)
    elif args.command == 'test':
        admin.test_execution(args.file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
