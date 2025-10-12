"""
Demo cases for LLT decomposition.

Each module contains specific data generation and parameter configurations
for demonstrating LLT on different types of time series patterns.
"""

from . import piecewise_linear
from . import simple_wave
from . import nonstationary

__all__ = [
    'piecewise_linear',
    'simple_wave',
    'nonstationary'
]