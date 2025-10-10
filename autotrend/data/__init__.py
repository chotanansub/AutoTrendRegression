"""
Data utilities for AutoTrend.

This module provides:
- gen_data: Synthetic data generators for testing and demonstrations
- datasets: Real-world dataset loaders (future)
"""

from .sythn_data import (
    generate_simple_wave,
    generate_nonstationary_wave,
    generate_piecewise_linear
)

__all__ = [
    'generate_simple_wave',
    'generate_nonstationary_wave',
    'generate_piecewise_linear'
]