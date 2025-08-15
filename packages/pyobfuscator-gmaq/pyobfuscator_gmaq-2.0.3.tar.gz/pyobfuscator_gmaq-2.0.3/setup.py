from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyobfuscator-gmaq",
    version="2.0.3",
    author="GMAQ Security",
    author_email="admin@gmaq.security",
    description="A powerful Python obfuscation library with distributed password storage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gmaq/pyobfuscator-gmaq",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "cryptography>=3.4.8",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "pyobfuscator-gmaq=pyobfuscator_gmaq.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pyobfuscator_gmaq": ["fragments/*.py", "*.py"],
    },
)
