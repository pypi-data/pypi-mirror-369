#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Get version from package
def get_version():
    here = os.path.abspath(os.path.dirname(__file__))
    version_file = os.path.join(here, "hostinger_cli", "__init__.py")
    
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    
    raise RuntimeError("Unable to find version string.")

setup(
    name="hostinger-cli",
    version=get_version(),
    author="Hostinger CLI Contributors",
    author_email="support@hostinger.com",
    description="A comprehensive command-line interface for Hostinger API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/hostinger/hostinger-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "hostinger=hostinger_cli.main:main",
            "hapi=hostinger_cli.main:main",  # Short alias
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "hostinger",
        "api",
        "cli",
        "cloud",
        "vps",
        "domains",
        "dns",
        "hosting",
        "web hosting",
        "server management",
        "domain management",
    ],
    project_urls={
        "Bug Reports": "https://github.com/hostinger/hostinger-cli/issues",
        "Source": "https://github.com/hostinger/hostinger-cli",
        "Documentation": "https://developers.hostinger.com",
        "API Documentation": "https://developers.hostinger.com",
    },
)
