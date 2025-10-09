"""
Data generation utilities for testing and demonstrations.

This module provides synthetic data generators for creating various
time series patterns including sinusoidal waves and piecewise linear sequences.
"""

from .gen_data import generate_simple_wave, generate_piecewise_linear

__all__ = [
    'generate_simple_wave',
    'generate_piecewise_linear'
]