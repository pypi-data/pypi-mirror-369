# PyObfuscator-GMAQ

A powerful Python code obfuscation library that encrypts Python files with distributed password storage and automatic decryption capabilities.

## Features

- **Strong Encryption**: Uses AES-256-CBC encryption with 500-character distributed password
- **Distributed Security**: Password split across 5 separate modules for enhanced security  
- **Automatic Decryption**: Encrypted files run seamlessly without manual password input
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Easy to Use**: Simple command-line interface for encryption

## Installation

```bash
pip install pyobfuscator-gmaq
```

## Quick Start

### Encrypt a Python file:
```bash
pyobfuscator-gmaq encrypt script.py encrypted_script.py
```

### Run the encrypted file directly:
```bash
python encrypted_script.py
```

The encrypted file will automatically decrypt and execute using the password stored within the library.

## Command Line Usage

```bash
# Encrypt a file
pyobfuscator-gmaq encrypt input.py output.py

# Get file information
pyobfuscator-gmaq info encrypted_file.py
```

## Administrative Interface

The AdminGMAQ.py tool provides additional administrative functions:

```bash
# Display admin information
python AdminGMAQ.py info

# Encrypt a file
python AdminGMAQ.py encrypt script.py encrypted_script.py

# Validate encrypted file
python AdminGMAQ.py validate encrypted_script.py

# Test encrypted file execution  
python AdminGMAQ.py test encrypted_script.py
```

## Security Architecture

- **500-Character Master Password**: Distributed across 5 fragment modules
- **Deterministic Encryption**: Consistent results across different environments
- **Fragment-Based Storage**: Each password fragment uses different obfuscation techniques
- **Fallback System**: Ensures functionality even if some fragments are missing
- **AES-256-CBC**: Industry-standard encryption with PBKDF2 key derivation

## Requirements

- Python 3.7+
- cryptography>=3.4.8
- click>=8.0.0

## License

MIT License - see LICENSE file for details.

## Version

Current version: 2.0.3