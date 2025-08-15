"""
Setup configuration for PyObfusCrypt package
Prepares the library for PyPI distribution
"""

from setuptools import setup, find_packages

# Read README file
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Advanced Python file obfuscation library with multi-layer encryption"

setup(
    name="pyobfuscrypt",
    version="1.0.0",
    author="PyObfusCrypt Team",
    author_email="dev@pyobfuscrypt.com",
    description="Advanced Python file obfuscation with multi-layer encryption",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pyobfuscrypt/pyobfuscrypt",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "cryptography>=3.4.8",
    ],
    entry_points={
        "console_scripts": [
            "pyobfuscrypt=pyobfuscrypt.cli:main",
        ],
    },
    keywords="obfuscation encryption python security cryptography",
    project_urls={
        "Bug Reports": "https://github.com/pyobfuscrypt/pyobfuscrypt/issues",
        "Source": "https://github.com/pyobfuscrypt/pyobfuscrypt",
        "Documentation": "https://pyobfuscrypt.readthedocs.io/",
    },
    include_package_data=True,
    zip_safe=False,
)
