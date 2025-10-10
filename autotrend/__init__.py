"""
AutoTrend: Local Linear Trend Extraction and Visualization

Main exports:
- decompose_llt: Core LLT decomposition algorithm
- LLTResult: Result dataclass with trend and prediction marks
- Plotting functions: plot_error, plot_slope_comparison, plot_full_decomposition, etc.
- Data generators: generate_simple_wave, generate_nonstationary_wave, generate_piecewise_linear
"""

from .core.local_linear_trend import decompose_llt, LLTResult
from .visualization.plot import (
    plot_error,
    plot_slope_comparison,
    plot_full_decomposition,
    plot_iteration_grid,
    plot_model_statistics
)
from .data import (
    generate_simple_wave,
    generate_nonstationary_wave,
    generate_piecewise_linear
)

__all__ = [
    # Core algorithm
    'decompose_llt',
    'LLTResult',
    
    # Plotting functions
    'plot_error',
    'plot_slope_comparison',
    'plot_full_decomposition',
    'plot_iteration_grid',
    'plot_model_statistics',
    
    # Data generators
    'generate_simple_wave',
    'generate_nonstationary_wave',
    'generate_piecewise_linear'
]