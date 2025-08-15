#!/usr/bin/env python3
"""
Q VEST - IBM Quantum Portfolio Prediction CLI

A quantum-powered investment portfolio optimization tool using IBM Quantum computers.
"""

__version__ = "1.0.0"
__author__ = "Minhal Rizvi"
__license__ = "MIT"

from .config_manager import ConfigManager
from .prediction import QuantumPortfolioOptimizer

__all__ = ["ConfigManager", "QuantumPortfolioOptimizer"]
