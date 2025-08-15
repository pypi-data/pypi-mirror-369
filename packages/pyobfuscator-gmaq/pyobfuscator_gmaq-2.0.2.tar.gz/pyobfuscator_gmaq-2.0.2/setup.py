"""
Setup configuration for PyObfusCrypt package
Prepares the library for PyPI distribution
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyobfuscator-gmaq",
    version="2.0.2",
    author="PyObfusCrypt Team",
    description="Advanced Python File Obfuscation with Multi-Layer Encryption",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.7",
    install_requires=[
        "cryptography>=3.4.8",
    ],
    entry_points={
        "console_scripts": [
            "pyobfuscator-gmaq=pyobfuscrypt.cli:main",
        ],
    },
)