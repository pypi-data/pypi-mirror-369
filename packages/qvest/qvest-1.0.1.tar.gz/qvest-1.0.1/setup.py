#!/usr/bin/env python3
"""
Setup configuration for qvest - IBM Quantum Portfolio Prediction CLI
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    """Read README file for long description"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Q VEST - IBM Quantum Portfolio Prediction CLI"

setup(
    name="qvest",
    version="1.0.1",
    description="IBM Quantum-powered portfolio optimization CLI tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Minhal Rizvi",
    author_email="minhal@example.com",
    url="https://github.com/Minhal128/qvest",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "yfinance>=0.1.87",
        "scipy>=1.7.0",
        "qiskit>=0.45.0",
        "qiskit-ibm-runtime>=0.15.0",
        "qiskit-aer>=0.12.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "qvest=qvest.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    keywords="quantum computing, portfolio optimization, IBM Quantum, finance, investment",
    project_urls={
        "Bug Reports": "https://github.com/Minhal128/qvest/issues",
        "Source": "https://github.com/Minhal128/qvest",
        "Documentation": "https://github.com/Minhal128/qvest/README.md",
    },
    include_package_data=True,
    zip_safe=False,
)
