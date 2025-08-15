# PyObfuscator-GMAQ

**Advanced Python File Obfuscation with Multi-Layer Encryption**

PyObfusCrypt is a powerful Python library that provides complete obfuscation of Python source code through multi-layer encryption. The encrypted files appear as completely unreadable binary data, ensuring zero comprehensibility of the original source code.

## 🔒 Key Features

- **Complete Content Obfuscation**: Encrypted files contain absolutely no readable text
- **Multi-Layer Encryption**: AES-256 + Base64 + Hex + Compression + Custom Mapping
- **Distributed Password Protection**: Master password split across multiple fragments (~1% discovery probability)
- **Zero Pattern Recognition**: Output appears as random binary data
- **Command-Line Interface**: Easy-to-use CLI for encryption/decryption
- **PyPI Ready**: Fully packaged for distribution

## 🛡️ Security Features

- **AES-256 Encryption** with random salt and IV
- **Multiple Encoding Layers** for pattern elimination
- **Custom Character Mapping** for final obfuscation
- **Random Noise Injection** to eliminate any readable patterns
- **Fragment-Based Password** distribution across 5 separate files
- **SHA-256 Hash Verification** for authentication

## 📦 Installation

```bash
pip install pyobfuscator-gmaq
