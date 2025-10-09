"""
Visualization utilities for LLT decomposition results.

This module provides comprehensive plotting functions for analyzing
and visualizing Local Linear Trend decomposition, including error analysis,
slope comparisons, full decomposition views, iteration grids, and statistical summaries.
"""

from .plot_error import plot_error
from .plot_slope import plot_slope_comparison
from .plot_full_decomposition import plot_full_decomposition
from .plot_iteration_grid import plot_iteration_grid
from .plot_model_statistics import plot_model_statistics

__all__ = [
    'plot_error',
    'plot_slope_comparison',
    'plot_full_decomposition',
    'plot_iteration_grid',
    'plot_model_statistics'
]