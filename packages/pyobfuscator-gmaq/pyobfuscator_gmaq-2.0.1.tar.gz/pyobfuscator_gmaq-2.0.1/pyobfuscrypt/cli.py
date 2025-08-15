"""
Command-line interface for PyObfusCrypt
Provides easy-to-use commands for encryption and decryption
"""

import argparse
import sys
import os
from .core import PyObfusCrypt


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='PyObfusCrypt - Advanced Python File Obfuscation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s encrypt script.py encrypted.pyo
  %(prog)s decrypt encrypted.pyo decrypted.py
  %(prog)s encrypt -p mypassword script.py encrypted.pyo
        """
    )
    
    parser.add_argument('action', choices=['encrypt', 'decrypt'], 
                       help='Action to perform')
    parser.add_argument('input', help='Input file path')
    parser.add_argument('output', help='Output file path')
    parser.add_argument('-p', '--password', help='Custom password (optional)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file '{args.input}' does not exist")
        sys.exit(1)
    
    # Create output directory if needed
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Initialize obfuscation engine
    obfuscator = PyObfusCrypt()
    
    if args.verbose:
        print(f"🔧 Action: {args.action}")
        print(f"📁 Input: {args.input}")
        print(f"📁 Output: {args.output}")
        print("🔒 Using advanced multi-layer obfuscation...")
    
    # Perform action
    success = False
    if args.action == 'encrypt':
        success = obfuscator.encrypt_file(args.input, args.output, args.password)
        if success and args.verbose:
            print("🛡️  File completely obfuscated - zero readable content remains")
    
    elif args.action == 'decrypt':
        success = obfuscator.decrypt_file(args.input, args.output, args.password)
        if success and args.verbose:
            print("🔓 File successfully restored to original Python code")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
