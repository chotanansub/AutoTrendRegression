"""
Core LLT algorithm and utility functions.

This module contains the fundamental Local Linear Trend extraction algorithm
and supporting utilities for range manipulation and data processing.
"""

from .local_linear_trend import decompose_llt, LLTResult
from .utility import extract_ranges, split_by_gap

__all__ = [
    'decompose_llt',
    'LLTResult',
    'extract_ranges',
    'split_by_gap'
]