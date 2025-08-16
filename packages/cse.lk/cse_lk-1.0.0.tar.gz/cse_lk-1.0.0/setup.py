#!/usr/bin/env python3
"""Setup configuration for cse.lk package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cse.lk",
    version="1.0.0",
    author="CSE API Client",
    author_email="contact@example.com",
    description="A comprehensive Python client for the Colombo Stock Exchange (CSE) API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/cse.lk",
    project_urls={
        "Bug Tracker": "https://github.com/your-username/cse.lk/issues",
        "Documentation": "https://github.com/your-username/cse.lk#readme",
        "Source Code": "https://github.com/your-username/cse.lk",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",

        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=3.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "pre-commit>=2.0",
            "build>=0.8.0",
            "twine>=4.0.0",
        ],
    },
    keywords="colombo stock exchange cse api finance sri lanka stocks trading",
    include_package_data=True,
    zip_safe=False,
) 