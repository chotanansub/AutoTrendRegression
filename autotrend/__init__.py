"""
AutoTrend: Local Linear Trend Extraction and Visualization

Main exports:
- decompose_llt: Functional API for LLT decomposition
- DecomposeLLT: Object-based API for LLT decomposition (scikit-learn style)
- LLTResult: Result dataclass with trend and prediction marks
- Plotting functions: plot_error, plot_slope_comparison, plot_full_decomposition, etc.
- Data generators: generate_simple_wave, generate_nonstationary_wave, generate_piecewise_linear

Usage Examples:
    # Option A: Functional API (quick usage)
    >>> from autotrend import decompose_llt
    >>> result = decompose_llt(sequence, window_size=10)
    >>> result.plot_all()
    
    # Option B: Object-based API (advanced usage)
    >>> from autotrend import DecomposeLLT
    >>> decomposer = DecomposeLLT(window_size=10, max_models=5)
    >>> result = decomposer.fit(sequence)
    >>> result.plot_full_decomposition()
    
    # Option C: Convenience wrapper
    >>> result = DecomposeLLT(window_size=10).fit_plot(sequence)
"""

from .core.local_linear_trend import decompose_llt, DecomposeLLT, LLTResult
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

__version__ = '0.2.0'

__all__ = [
    # Core algorithm
    'decompose_llt',
    'DecomposeLLT',
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