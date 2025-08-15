# PyObfuscator - Advanced Python Code Protection System

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-linux-green.svg)](https://linux.org)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

A comprehensive Python code obfuscation and encryption system designed for Linux environments. Provides military-grade protection against reverse engineering, code analysis, and unauthorized access through multiple layers of security.

## 🛡️ Security Features

- **AES-256-GCM Encryption** - Military-grade encryption for maximum security
- **AST-Based Obfuscation** - Advanced Abstract Syntax Tree manipulation
- **Anti-Tampering Protection** - Runtime integrity checks and modification detection
- **Anti-Debugging** - Detects and prevents debugging attempts
- **Variable & Function Renaming** - Systematic identifier obfuscation
- **String Obfuscation** - Advanced string encoding and hiding
- **Dead Code Injection** - Confuses static analysis tools
- **Bytecode Protection** - Low-level bytecode manipulation

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/MohamedQM/PyObfuscator.git
cd PyObfuscator

# Install dependencies (simple method)
python3 install.py

# Or install manually
pip3 install cryptography psutil
```

### Basic Usage

```bash
# Obfuscate a Python file
python3 main.py your_script.py

# Maximum security protection
python3 main.py your_script.py --max-security

# Create importable library
python3 main.py your_script.py --library
```

### Programmatic Usage

```python
from pyobfuscator import obfuscate_code, obfuscate_file

# Obfuscate code directly
code = """
def hello():
    print("Hello World!")
hello()
"""
protected_code = obfuscate_code(code, max_security=True)

# Obfuscate a file
success = obfuscate_file("input.py", "output.py")
```

## 📁 Project Structure

```
PyObfuscator/
├── pyobfuscator/           # Core library
│   ├── __init__.py        # Main API interface
│   ├── core.py           # Core obfuscation engine
│   ├── obfuscator.py     # AST manipulation
│   ├── encryption.py     # AES-256-GCM encryption
│   ├── anti_tamper.py    # Anti-tampering protection
│   └── utils.py          # Utility functions
├── examples/              # Usage examples
│   ├── sample_code.py    # Sample code for testing
│   └── usage_example.py  # Integration examples
├── main.py               # CLI interface
├── install.py            # Simple installer
├── test_basic.py         # Basic functionality tests
└── README.md             # This file
```

## 🔒 Protection Levels

### Basic Protection
- Variable and function renaming
- String encoding and obfuscation
- Basic dead code injection
- Simple control flow changes

### Advanced Protection
- AES-256-GCM encryption with PBKDF2
- Advanced AST transformations
- Metadata removal
- Enhanced anti-debugging

### Maximum Security
- All protection features enabled
- Real-time tampering detection
- Environment analysis
- Process monitoring
- Bytecode encryption

## 🧪 Testing

```bash
# Run basic functionality tests
python3 test_basic.py

# Test with sample code
python3 main.py examples/sample_code.py
python3 examples/sample_code_obfuscated.py
```

## 💻 System Requirements

- **OS**: Linux (Ubuntu 18.04+ recommended)
- **Python**: 3.7+ (tested on 3.8-3.11)
- **RAM**: 512MB minimum
- **Dependencies**: `cryptography`, `psutil`

## 📖 CLI Options

```bash
python3 main.py [INPUT_FILE] [OPTIONS]

Options:
  -o, --output FILE        Output file path
  --max-security          Enable maximum protection
  --custom-key KEY        Use custom encryption key
  --library              Create importable library
  --no-anti-debug        Disable anti-debugging
  --preserve-names       Keep original function names
```

## 🔧 Advanced Configuration

### Custom Encryption Key
```python
from pyobfuscator.encryption import AdvancedEncryption

encryptor = AdvancedEncryption()
key = encryptor.generate_key("your_custom_password")
obfuscated = obfuscate_code(source, encryption_key=key)
```

### Selective Protection
```python
from pyobfuscator.core import PyObfuscatorCore

obfuscator = PyObfuscatorCore()
obfuscator.config.rename_variables = True
obfuscator.config.encrypt_strings = True
obfuscator.config.add_fake_code = False
result = obfuscator.obfuscate(source_code)
```

## ⚠️ Important Notes

1. **Linux Only**: This tool is optimized for Linux environments
2. **Backup Your Code**: Always keep original source code backups
3. **Test Thoroughly**: Test obfuscated code before deployment
4. **GitHub Safe**: No sensitive data included - safe for public repositories

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- **Repository**: https://github.com/MohamedQM/PyObfuscator
- **Issues**: https://github.com/MohamedQM/PyObfuscator/issues
- **Documentation**: See `README_SIMPLE.md` for Arabic documentation

---

**Developed with ❤️ for the Python security community**

*Last Updated: August 2024*