"""
LLTResult dataclass for storing decomposition results.
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class LLTResult:
    """
    Results from Local Linear Trend (LLT) decomposition.
    
    Attributes:
        trend_marks: Array indicating which iteration labeled each point.
                     Values represent the iteration number (1, 2, 3, ...) or NaN if unlabeled.
        prediction_marks: Array of predicted values for each point.
                         NaN for points without predictions.
        models: List of LinearRegression models from each iteration.
        process_logs: Detailed logs from each iteration for visualization.
                     Each log is a tuple of (predictions, errors, focus_ranges, high_error_flag, threshold_value).
        _sequence: Original sequence (stored for plotting convenience).
        _window_size: Window size used in decomposition.
    """
    trend_marks: np.ndarray
    prediction_marks: np.ndarray
    models: List[LinearRegression]
    process_logs: List[Tuple]
    _sequence: Optional[np.ndarray] = None
    _window_size: Optional[int] = None
    
    def get_num_iterations(self) -> int:
        """Get the number of iterations performed."""
        return len(self.models)
    
    def get_trend_segments(self) -> List[Tuple[int, int, int]]:
        """
        Extract contiguous trend segments.
        
        Returns:
            List of tuples (start_idx, end_idx, iteration_number)
        """
        segments = []
        current_trend = None
        start_idx = None
        
        for i, trend in enumerate(self.trend_marks):
            if not np.isnan(trend):
                if trend != current_trend:
                    if current_trend is not None:
                        segments.append((start_idx, i, int(current_trend)))
                    current_trend = trend
                    start_idx = i
            else:
                if current_trend is not None:
                    segments.append((start_idx, i, int(current_trend)))
                    current_trend = None
                    start_idx = None
        
        if current_trend is not None:
            segments.append((start_idx, len(self.trend_marks), int(current_trend)))
        
        return segments
    
    def get_predictions_by_iteration(self, iteration: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get indices and predictions for a specific iteration.
        
        Args:
            iteration: Iteration number (1-indexed)
            
        Returns:
            Tuple of (indices, predictions) for points labeled in that iteration
        """
        mask = self.trend_marks == iteration
        indices = np.where(mask)[0]
        predictions = self.prediction_marks[mask]
        return indices, predictions
    
    # ========== PLOTTING CONVENIENCE METHODS ==========
    
    def plot_error(self, sequence=None, window_size=None, **kwargs):
        """
        Plot error analysis visualization.
        
        Args:
            sequence: Original sequence (optional if stored internally)
            window_size: Window size (optional if stored internally)
            **kwargs: Additional arguments passed to plot_error()
            
        Returns:
            matplotlib Figure object
        """
        from ..visualization import plot_error
        
        seq = sequence if sequence is not None else self._sequence
        ws = window_size if window_size is not None else self._window_size
        
        if seq is None:
            raise ValueError("Sequence must be provided either during decomposition or when plotting")
        if ws is None:
            raise ValueError("Window size must be provided either during decomposition or when plotting")
        
        return plot_error(seq, self.process_logs, ws, **kwargs)
    
    def plot_slopes(self, **kwargs):
        """
        Plot slope comparison across models.
        
        Args:
            **kwargs: Additional arguments passed to plot_slope_comparison()
            
        Returns:
            matplotlib Figure object
        """
        from ..visualization import plot_slope_comparison
        return plot_slope_comparison(self.models, **kwargs)
    
    def plot_full_decomposition(self, sequence=None, **kwargs):
        """
        Plot full decomposition visualization.
        
        Args:
            sequence: Original sequence (optional if stored internally)
            **kwargs: Additional arguments passed to plot_full_decomposition()
            
        Returns:
            matplotlib Figure object
        """
        from ..visualization import plot_full_decomposition
        
        seq = sequence if sequence is not None else self._sequence
        if seq is None:
            raise ValueError("Sequence must be provided either during decomposition or when plotting")
        
        return plot_full_decomposition(seq, self, **kwargs)
    
    def plot_iteration_grid(self, sequence=None, **kwargs):
        """
        Plot iteration-by-iteration grid visualization.
        
        Args:
            sequence: Original sequence (optional if stored internally)
            **kwargs: Additional arguments passed to plot_iteration_grid()
            
        Returns:
            matplotlib Figure object
        """
        from ..visualization import plot_iteration_grid
        
        seq = sequence if sequence is not None else self._sequence
        if seq is None:
            raise ValueError("Sequence must be provided either during decomposition or when plotting")
        
        return plot_iteration_grid(seq, self, **kwargs)
    
    def plot_statistics(self, **kwargs):
        """
        Plot model statistics summary.
        
        Args:
            **kwargs: Additional arguments passed to plot_model_statistics()
            
        Returns:
            matplotlib Figure object
        """
        from ..visualization import plot_model_statistics
        return plot_model_statistics(self, **kwargs)
    
    def plot_all(self, sequence=None, window_size=None, output_dir=None, prefix="llt", show=True):
        """
        Generate all visualization plots at once.
        
        Args:
            sequence: Original sequence (optional if stored internally)
            window_size: Window size (optional if stored internally)
            output_dir: Directory to save plots (if None, displays interactively)
            prefix: Filename prefix for saved plots
            show: Whether to display plots interactively (only if output_dir is None)
            
        Returns:
            Dictionary mapping plot names to Figure objects
        """
        import matplotlib.pyplot as plt
        from pathlib import Path
        
        seq = sequence if sequence is not None else self._sequence
        ws = window_size if window_size is not None else self._window_size
        
        plots = {}
        
        # Generate all plots
        plots['error'] = self.plot_error(seq, ws)
        plots['slopes'] = self.plot_slopes()
        plots['full_decomposition'] = self.plot_full_decomposition(seq)
        plots['iteration_grid'] = self.plot_iteration_grid(seq)
        plots['statistics'] = self.plot_statistics()
        
        # Save if output directory specified
        if output_dir is not None:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            for name, fig in plots.items():
                save_path = output_path / f"{prefix}_{name}.png"
                fig.savefig(save_path, dpi=150, bbox_inches='tight')
                plt.close(fig)
                print(f"  ✓ Saved: {save_path}")
        elif show:
            plt.show()
        
        return plots