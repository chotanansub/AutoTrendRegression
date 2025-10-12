"""
Core LLT algorithm and utility functions.

This module contains the fundamental Local Linear Trend extraction algorithm
and supporting utilities for range manipulation and data processing.
"""

from .llt_result import LLTResult
from .decompose_llt_class import DecomposeLLT
from .functional_api import decompose_llt
from .utility import extract_ranges, split_by_gap

__all__ = [
    'decompose_llt',
    'DecomposeLLT',
    'LLTResult',
    'extract_ranges',
    'split_by_gap'
]