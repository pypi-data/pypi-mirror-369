
"""
Command Line Interface for PyObfusCrypt
Provides easy command-line access to encryption/decryption functionality
"""

import argparse
import sys
import os
from .core import PyObfusCrypt


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="PyObfusCrypt - Advanced Python File Obfuscation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pyobfuscator-gmaq encrypt input.py output.pyo
  pyobfuscator-gmaq decrypt output.pyo restored.py
  pyobfuscator-gmaq encrypt --password mypass script.py script.pyo
        """
    )
    
    parser.add_argument(
        'action',
        choices=['encrypt', 'decrypt'],
        help='Action to perform'
    )
    
    parser.add_argument(
        'input_file',
        help='Input file path'
    )
    
    parser.add_argument(
        'output_file',
        help='Output file path'
    )
    
    parser.add_argument(
        '--password',
        help='Custom password (optional - uses default if not provided)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='PyObfusCrypt 2.0.1'
    )
    
    # Parse arguments
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.exists(args.input_file):
        print(f"❌ Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    
    # Create obfuscator instance
    obfuscator = PyObfusCrypt()
    
    # Perform action
    if args.action == 'encrypt':
        print(f"🔒 Encrypting '{args.input_file}' to '{args.output_file}'...")
        success = obfuscator.encrypt_file(args.input_file, args.output_file, args.password)
    elif args.action == 'decrypt':
        print(f"🔓 Decrypting '{args.input_file}' to '{args.output_file}'...")
        success = obfuscator.decrypt_file(args.input_file, args.output_file, args.password)
    
    if success:
        print("✅ Operation completed successfully!")
        sys.exit(0)
    else:
        print("❌ Operation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
