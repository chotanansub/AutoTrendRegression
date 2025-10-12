"""
Functional API for LLT decomposition.
"""
import numpy as np
from .llt_result import LLTResult
from .decompose_llt_class import DecomposeLLT


def decompose_llt(
    seq: np.ndarray,
    max_models: int = 10,
    window_size: int = 5,
    error_percentile: int = 40,
    percentile_step: int = 0,
    update_threshold: bool = False,
    is_quiet: bool = False,
    store_sequence: bool = True
) -> LLTResult:
    """
    Fit linear regression on high-error segments identified via sliding windows (functional API).
    
    This is a convenience wrapper around DecomposeLLT for quick, one-off decompositions.
    For repeated use with the same parameters, consider using DecomposeLLT directly.

    Args:
        seq: 1D input sequence.
        max_models: Maximum number of refinement rounds.
        window_size: Length of each training window.
        error_percentile: Initial percentile threshold for high errors.
        percentile_step: Step size to increase error threshold per round.
        update_threshold: Whether to update threshold each iteration.
        is_quiet: Whether to suppress printed output.
        store_sequence: Whether to store sequence in result for plotting convenience.

    Returns:
        LLTResult: Dataclass containing trend_marks, prediction_marks, models, and process_logs.
        
    Examples:
        >>> # Functional API (quick usage)
        >>> result = decompose_llt(seq, max_models=5, window_size=10)
        >>> result.plot_full_decomposition()
        
        >>> # Access components
        >>> trends = result.trend_marks
        >>> predictions = result.prediction_marks
        >>> models = result.models
        
        >>> # Get summary information
        >>> print(f"Completed {result.get_num_iterations()} iterations")
        >>> segments = result.get_trend_segments()
    """
    decomposer = DecomposeLLT(
        max_models=max_models,
        window_size=window_size,
        error_percentile=error_percentile,
        percentile_step=percentile_step,
        update_threshold=update_threshold,
        is_quiet=is_quiet,
        store_sequence=store_sequence
    )
    return decomposer.fit(seq)