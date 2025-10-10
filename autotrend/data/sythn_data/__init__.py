"""
Synthetic data generation utilities for testing and demonstrations.

This module provides generators for various time series patterns:
- Simple stationary sine waves
- Non-stationary waves with amplitude modulation
- Piecewise linear sequences with trend changes
"""

from .generate_simple_wave import generate_simple_wave
from .generate_nonstationary_wave import generate_nonstationary_wave
from .generate_piecewise_linear import generate_piecewise_linear

__all__ = [
    'generate_simple_wave',
    'generate_nonstationary_wave',
    'generate_piecewise_linear'
]