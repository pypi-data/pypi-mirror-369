"""
Fire App - A modern performance finance tracker built with PySide6.

A comprehensive personal finance dashboard application that helps you
track your net worth, assets, liabilities, and cash flow with a 
beautiful, modern interface.

Author: Ismael Jimenez
License: MIT
"""

__version__ = "0.1.0"
__author__ = "Ismael Jimenez"
__email__ = "ismael@example.com"
__license__ = "MIT"

from .main import FinanceDashboard, main

__all__ = ["FinanceDashboard", "main", "__version__"]