"""
Django Query Analyzer - Automatic query performance logging
"""
from .analyzers import QueryAnalyzer
from .loggers import QueryLogger

__version__ = '0.1.0'

__all__ = ['QueryAnalyzer', 'QueryLogger']
