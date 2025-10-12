"""
Reusable demo runner for LLT demonstrations.
Handles data generation, decomposition, visualization, and logging.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from autotrend import decompose_llt


class DemoRunner:
    """
    Reusable runner for LLT demos.
    
    Usage:
        runner = DemoRunner(output_subdir="simple_wave")
        runner.run(
            name="Simple Wave (Clean)",
            sequence=my_sequence,
            window_size=10,
            max_models=5,
            error_percentile=40
        )
    """
    
    def __init__(self, output_subdir="general"):
        """
        Initialize demo runner.
        
        Args:
            output_subdir: Subdirectory under output/ for organizing results
        """
        self.output_dir = Path("output") / output_subdir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def run(self, name, sequence, window_size=10, max_models=5, 
            error_percentile=40, percentile_step=0, update_threshold=False,
            verbose=2):
        """
        Run a complete demo: decomposition + visualization + logging.
        
        Args:
            name: Demo name (used for output filenames)
            sequence: Time series data (numpy array)
            window_size: LLT window size
            max_models: Maximum iterations
            error_percentile: Error threshold percentile
            percentile_step: Percentile increment per iteration
            update_threshold: Whether to update threshold each iteration
            verbose: Verbosity level (0=silent, 1=basic, 2=detailed)
        """
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print(f"{'='*60}")
        
        base_name = self._clean_filename(name)
        
        print(f"  Sequence length: {len(sequence)}")
        
        # Run decomposition
        result = decompose_llt(
            seq=sequence,
            max_models=max_models,
            window_size=window_size,
            error_percentile=error_percentile,
            percentile_step=percentile_step,
            update_threshold=update_threshold,
            verbose=verbose,
            store_sequence=True
        )
        
        print(f"  Iterations: {result.get_num_iterations()}")
        
        # Generate all plots
        self._save_plot(result.plot_error, base_name, "error")
        self._save_plot(lambda: result.plot_slopes(x_range=(-5, 5)), base_name, "slopes")
        self._save_plot(lambda: result.plot_full_decomposition(figsize=(16, 10)), 
                       base_name, "full_decomposition")
        self._save_plot(lambda: result.plot_iteration_grid(figsize=(16, 12)), 
                       base_name, "iteration_grid")
        self._save_plot(lambda: result.plot_statistics(figsize=(14, 8)), 
                       base_name, "model_statistics")
        
        # Save log file
        self._save_log(name, sequence, result, base_name, 
                      window_size, max_models, error_percentile)
        
        print(f"{'='*60}\n")
        
        return result
    
    def _clean_filename(self, name):
        """Convert demo name to clean filename."""
        return name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    
    def _save_plot(self, plot_func, base_name, suffix):
        """Generate and save a plot."""
        plot_func()
        save_path = self.output_dir / f"{base_name}_{suffix}.png"
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close('all')
        print(f"  ✓ {save_path}")
    
    def _save_log(self, name, sequence, result, base_name, 
                  window_size, max_models, error_percentile):
        """Save summary log file."""
        log_path = self.output_dir / f"{base_name}_log.txt"
        
        with open(log_path, 'w') as f:
            f.write(f"Demo: {name}\n{'='*60}\n\n")
            f.write(f"Configuration:\n")
            f.write(f"  - Sequence length: {len(sequence)}\n")
            f.write(f"  - Window size: {window_size}\n")
            f.write(f"  - Max models: {max_models}\n")
            f.write(f"  - Error percentile: {error_percentile}\n\n")
            f.write(f"Results:\n")
            f.write(f"  - Iterations: {result.get_num_iterations()}\n")
            f.write(f"  - Models: {len(result.models)}\n\n")
            f.write(f"Model Slopes:\n")
            for i, model in enumerate(result.models, 1):
                slope = model.coef_[0]
                intercept = model.intercept_
                f.write(f"  Model {i}: slope={slope:.6f}, intercept={intercept:.6f}\n")
            
            f.write(f"\nTrend Segments:\n")
            segments = result.get_trend_segments()
            for start, end, iteration in segments:
                f.write(f"  [{start:4d}, {end:4d}) -> Iteration {iteration}\n")
        
        print(f"  ✓ {log_path}")