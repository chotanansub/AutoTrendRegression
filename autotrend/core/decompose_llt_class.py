"""
DecomposeLLT class: Object-based API for LLT decomposition.
"""
import numpy as np
from typing import List, Optional
from .llt_result import LLTResult
from .llt_algorithm import decompose_llt_internal


class DecomposeLLT:
    """
    Local Linear Trend (LLT) decomposition estimator.
    
    This class provides a scikit-learn style interface for LLT decomposition,
    allowing parameter configuration and reuse across multiple sequences.
    
    Parameters:
        max_models: Maximum number of refinement iterations.
        window_size: Length of each training window.
        error_percentile: Initial percentile threshold for high errors.
        percentile_step: Step size to increase error threshold per iteration.
        update_threshold: Whether to update threshold each iteration.
        is_quiet: Whether to suppress printed output.
        store_sequence: Whether to store sequence in result for plotting convenience.
    
    Attributes:
        result_: LLTResult object from the last fit operation.
        n_iterations_: Number of iterations performed in the last fit.
    
    Examples:
        >>> # Object-based API
        >>> decomposer = DecomposeLLT(window_size=10, max_models=5)
        >>> result = decomposer.fit(sequence)
        >>> result.plot_all()
        
        >>> # Reuse configuration
        >>> result1 = decomposer.fit(sequence1)
        >>> result2 = decomposer.fit(sequence2)
        
        >>> # Convenience method
        >>> result = DecomposeLLT(window_size=10).fit_plot(sequence)
    """
    
    def __init__(
        self,
        max_models: int = 10,
        window_size: int = 5,
        error_percentile: int = 40,
        percentile_step: int = 0,
        update_threshold: bool = False,
        is_quiet: bool = False,
        store_sequence: bool = True
    ):
        self.max_models = max_models
        self.window_size = window_size
        self.error_percentile = error_percentile
        self.percentile_step = percentile_step
        self.update_threshold = update_threshold
        self.is_quiet = is_quiet
        self.store_sequence = store_sequence
        
        # Fitted attributes (set after fit)
        self.result_ = None
        self.n_iterations_ = None
    
    def fit(self, seq: np.ndarray) -> LLTResult:
        """
        Fit LLT decomposition to a sequence.
        
        Args:
            seq: 1D input sequence.
            
        Returns:
            LLTResult object containing decomposition results.
        """
        self.result_ = decompose_llt_internal(
            seq=seq,
            max_models=self.max_models,
            window_size=self.window_size,
            error_percentile=self.error_percentile,
            percentile_step=self.percentile_step,
            update_threshold=self.update_threshold,
            is_quiet=self.is_quiet,
            store_sequence=self.store_sequence
        )
        self.n_iterations_ = self.result_.get_num_iterations()
        return self.result_
    
    def fit_plot(
        self, 
        seq: np.ndarray, 
        plot_types: Optional[List[str]] = None,
        output_dir: Optional[str] = None,
        prefix: str = "llt",
        show: bool = True
    ) -> LLTResult:
        """
        Fit and immediately visualize results (convenience method).
        
        Args:
            seq: 1D input sequence.
            plot_types: List of plot types to generate. Options: 'error', 'slopes', 
                       'full_decomposition', 'iteration_grid', 'statistics', 'all'.
                       Default is ['full_decomposition'].
            output_dir: Directory to save plots (if None, displays interactively).
            prefix: Filename prefix for saved plots.
            show: Whether to display plots interactively.
            
        Returns:
            LLTResult object containing decomposition results.
        """
        import matplotlib.pyplot as plt
        from pathlib import Path
        
        result = self.fit(seq)
        
        if plot_types is None:
            plot_types = ['full_decomposition']
        
        if 'all' in plot_types:
            result.plot_all(output_dir=output_dir, prefix=prefix, show=show)
        else:
            plot_map = {
                'error': result.plot_error,
                'slopes': result.plot_slopes,
                'full_decomposition': result.plot_full_decomposition,
                'iteration_grid': result.plot_iteration_grid,
                'statistics': result.plot_statistics
            }
            
            for plot_type in plot_types:
                if plot_type not in plot_map:
                    raise ValueError(f"Unknown plot type: {plot_type}. "
                                   f"Options: {list(plot_map.keys()) + ['all']}")
                
                fig = plot_map[plot_type]()
                
                if output_dir is not None:
                    output_path = Path(output_dir)
                    output_path.mkdir(parents=True, exist_ok=True)
                    save_path = output_path / f"{prefix}_{plot_type}.png"
                    fig.savefig(save_path, dpi=150, bbox_inches='tight')
                    plt.close(fig)
                    print(f"  ✓ Saved: {save_path}")
            
            if output_dir is None and show:
                plt.show()
        
        return result
    
    def get_params(self, deep: bool = True) -> dict:
        """
        Get parameters for this estimator (scikit-learn compatible).
        
        Args:
            deep: Not used, kept for scikit-learn compatibility.
            
        Returns:
            Dictionary of parameter names mapped to their values.
        """
        return {
            'max_models': self.max_models,
            'window_size': self.window_size,
            'error_percentile': self.error_percentile,
            'percentile_step': self.percentile_step,
            'update_threshold': self.update_threshold,
            'is_quiet': self.is_quiet,
            'store_sequence': self.store_sequence
        }
    
    def set_params(self, **params) -> 'DecomposeLLT':
        """
        Set parameters for this estimator (scikit-learn compatible).
        
        Args:
            **params: Estimator parameters.
            
        Returns:
            Self (for method chaining).
        """
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Invalid parameter: {key}")
        return self
    
    def __repr__(self) -> str:
        """String representation of the estimator."""
        params = self.get_params()
        param_str = ", ".join(f"{k}={v}" for k, v in params.items())
        return f"DecomposeLLT({param_str})"