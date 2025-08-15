"""
Command-line interface for PyObfuscator-GMAQ
"""

import click
import os
from .core import PyObfuscatorGMAQ


@click.group()
@click.version_option(version="2.0.3")
def main():
    """PyObfuscator-GMAQ v2.0.3 - Advanced Python Code Obfuscation"""
    pass


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
def encrypt(input_file, output_file):
    """Encrypt a Python file with distributed password storage"""
    
    # Validate input file is Python
    if not input_file.endswith('.py'):
        click.echo("Error: Input file must be a Python (.py) file", err=True)
        return
        
    # Check if output file already exists
    if os.path.exists(output_file):
        if not click.confirm(f"Output file {output_file} already exists. Overwrite?"):
            return
            
    try:
        obfuscator = PyObfuscatorGMAQ()
        obfuscator.encrypt_file(input_file, output_file)
        
        click.echo(f"✓ Successfully encrypted {input_file} -> {output_file}")
        click.echo(f"✓ Encrypted file can be executed with: python3 {output_file}")
        
    except Exception as e:
        click.echo(f"Error: Encryption failed - {e}", err=True)


@main.command()
@click.argument('file_path', type=click.Path(exists=True))
def info(file_path):
    """Display information about an encrypted file"""
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        if 'PyObfuscator-GMAQ' in content and 'ENCRYPTED_PAYLOAD' in content:
            click.echo(f"✓ {file_path} is a PyObfuscator-GMAQ encrypted file")
            click.echo(f"✓ Version: 2.0.3")
            click.echo(f"✓ Can be executed directly with: python3 {file_path}")
        else:
            click.echo(f"✗ {file_path} is not a PyObfuscator-GMAQ encrypted file")
            
    except Exception as e:
        click.echo(f"Error: Could not read file - {e}", err=True)


if __name__ == "__main__":
    main()
