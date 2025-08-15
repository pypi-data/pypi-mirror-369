#!/usr/bin/env python3
"""
PyObfuscator CLI Interface
Command-line interface for the PyObfuscator package
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Import pyobfuscator modules
try:
    from . import obfuscate_code, obfuscate_file
    from .core import PyObfuscatorCore
    from .utils import setup_logging
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from pyobfuscator import obfuscate_code, obfuscate_file
    from pyobfuscator.core import PyObfuscatorCore
    from pyobfuscator.utils import setup_logging

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='PyObfuscator - Advanced Python Code Protection System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pyobfuscator script.py                     # Basic obfuscation
  pyobfuscator script.py -o protected.py    # Custom output file
  pyobfuscator script.py --max-security     # Maximum protection
  pyobfuscator script.py --library          # Create importable library
  pyobfuscator script.py --custom-key secret # Use custom encryption key

For more information, visit: https://github.com/MohamedQM/PyObfuscator
        """
    )
    
    # Input file argument
    parser.add_argument('input_file', 
                       help='Python file to obfuscate')
    
    # Output options
    parser.add_argument('-o', '--output', 
                       help='Output file path (default: input_file_obfuscated.py)')
    
    # Security options
    parser.add_argument('--max-security', 
                       action='store_true',
                       help='Enable maximum security protection')
    
    parser.add_argument('--custom-key', 
                       help='Use custom encryption key')
    
    parser.add_argument('--no-anti-debug', 
                       action='store_true',
                       help='Disable anti-debugging protection')
    
    # Output format options
    parser.add_argument('--library', 
                       action='store_true',
                       help='Create importable library module')
    
    
    
    # Logging options
    parser.add_argument('-v', '--verbose', 
                       action='store_true',
                       help='Enable verbose output')
    
    parser.add_argument('-q', '--quiet', 
                       action='store_true',
                       help='Suppress output messages')
    
    args = parser.parse_args()
    
    # Setup logging
    if args.quiet:
        log_level = logging.ERROR
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    setup_logging(level=log_level)
    logger = logging.getLogger('PyObfuscator')
    
    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        logger.error(f"Input file not found: {args.input_file}")
        sys.exit(1)
    
    if not input_path.suffix.lower() == '.py':
        logger.error(f"Input file must be a Python file (.py): {args.input_file}")
        sys.exit(1)
    
    # Generate output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_obfuscated.py"
    
    # Configuration
    config = {
        'max_security': args.max_security,
        'custom_key': args.custom_key,
        'anti_debug': not args.no_anti_debug,
        'library_mode': args.library
    }
    
    if not args.quiet:
        print("=" * 60)
        print("PyObfuscator - Advanced Python Code Protection")
        print("=" * 60)
        print(f"Input:  {input_path}")
        print(f"Output: {output_path}")
        if args.max_security:
            print("Security: Maximum Protection")
        elif args.custom_key:
            print("Security: Custom Encryption Key")
        else:
            print("Security: Standard Protection")
        print("=" * 60)
    
    try:
        # Perform obfuscation
        success = obfuscate_file(
            str(input_path), 
            str(output_path),
            **config
        )
        
        if success:
            if not args.quiet:
                print(f"✓ Obfuscation completed successfully!")
                print(f"✓ Protected file saved: {output_path}")
                
                # Show file sizes
                original_size = input_path.stat().st_size
                obfuscated_size = output_path.stat().st_size
                print(f"Original size: {original_size:,} bytes")
                print(f"Protected size: {obfuscated_size:,} bytes")
                
                if config['library_mode']:
                    print(f"✓ Library mode: Import as 'import {output_path.stem}'")
            
            sys.exit(0)
        else:
            logger.error("Obfuscation failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.error("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()