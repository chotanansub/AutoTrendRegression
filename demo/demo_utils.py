"""
Utility functions and configurations for running LLT demos.
This module provides reusable components that demo scripts can import.
"""
import sys
from pathlib import Path

# Add parent directory to path to import autotrend
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Callable, Dict

from autotrend import (
    decompose_llt,
    plot_error,
    plot_slope_comparison,
    plot_full_decomposition,
    plot_iteration_grid,
    plot_model_statistics
)


@dataclass
class DemoConfig:
    """Configuration for a single demo run."""
    name: str
    data_generator: Callable[[], np.ndarray]
    window_size: int = 10
    max_models: int = 5
    error_percentile: int = 40
    percentile_step: int = 0
    update_threshold: bool = False
    output_dir: str = "output"
    demo_type: str = "general"  # Used for subdirectory organization
    
    def get_output_path(self, suffix: str = "") -> Path:
        """Generate output file path in demo-type subdirectory."""
        # Create subdirectory based on demo type
        output_subdir = Path(self.output_dir) / self.demo_type
        
        # Clean filename from demo name
        base_name = self.name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        
        if suffix:
            return output_subdir / f"{base_name}_{suffix}.png"
        return output_subdir / f"{base_name}.png"


def run_single_demo(config: DemoConfig, verbose: bool = False) -> None:
    """
    Execute a single demo with given configuration.
    
    Args:
        config: Demo configuration
        verbose: Whether to print detailed logs
    """
    print(f"\n{'='*60}")
    print(f"Running: {config.name}")
    print(f"{'='*60}")
    
    # Ensure output directory exists (including subdirectory)
    output_subdir = Path(config.output_dir) / config.demo_type
    output_subdir.mkdir(parents=True, exist_ok=True)
    
    # Generate data
    sequence = config.data_generator()
    print(f"  Sequence length: {len(sequence)}")
    
    # Run LLT decomposition with new API
    result = decompose_llt(
        seq=sequence,
        max_models=config.max_models,
        window_size=config.window_size,
        error_percentile=config.error_percentile,
        percentile_step=config.percentile_step,
        update_threshold=config.update_threshold,
        is_quiet=not verbose,
        store_sequence=True  # Store sequence for plotting
    )
    
    print(f"  Iterations: {result.get_num_iterations()}, Models: {len(result.models)}")
    
    # 1. Generate and save error plot
    error_plot_path = config.get_output_path("error")
    error_plot_path.parent.mkdir(parents=True, exist_ok=True)
    
    result.plot_error()
    plt.savefig(error_plot_path, dpi=150, bbox_inches='tight')
    plt.close('all')
    print(f"  ✓ {error_plot_path}")
    
    # 2. Generate and save slope comparison plot
    if len(result.models) > 0:
        slope_plot_path = config.get_output_path("slopes")
        slope_plot_path.parent.mkdir(parents=True, exist_ok=True)
        
        result.plot_slopes(x_range=(-5, 5))
        plt.savefig(slope_plot_path, dpi=150, bbox_inches='tight')
        plt.close('all')
        print(f"  ✓ {slope_plot_path}")
    
    # 3. Generate and save full decomposition plot
    full_decomp_path = config.get_output_path("full_decomposition")
    full_decomp_path.parent.mkdir(parents=True, exist_ok=True)
    
    result.plot_full_decomposition(figsize=(16, 10))
    plt.savefig(full_decomp_path, dpi=150, bbox_inches='tight')
    plt.close('all')
    print(f"  ✓ {full_decomp_path}")
    
    # 4. Generate and save iteration grid plot
    iteration_grid_path = config.get_output_path("iteration_grid")
    iteration_grid_path.parent.mkdir(parents=True, exist_ok=True)
    
    result.plot_iteration_grid(figsize=(16, 12))
    plt.savefig(iteration_grid_path, dpi=150, bbox_inches='tight')
    plt.close('all')
    print(f"  ✓ {iteration_grid_path}")
    
    # 5. Generate and save model statistics plot
    model_stats_path = config.get_output_path("model_statistics")
    model_stats_path.parent.mkdir(parents=True, exist_ok=True)
    
    result.plot_statistics(figsize=(14, 8))
    plt.savefig(model_stats_path, dpi=150, bbox_inches='tight')
    plt.close('all')
    print(f"  ✓ {model_stats_path}")
    
    # Save summary log
    log_path = config.get_output_path("log").with_suffix('.txt')
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, 'w') as f:
        f.write(f"Demo: {config.name}\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"Configuration:\n")
        f.write(f"  - Sequence length: {len(sequence)}\n")
        f.write(f"  - Window size: {config.window_size}\n")
        f.write(f"  - Max models: {config.max_models}\n")
        f.write(f"  - Error percentile: {config.error_percentile}\n")
        f.write(f"  - Percentile step: {config.percentile_step}\n")
        f.write(f"  - Update threshold: {config.update_threshold}\n\n")
        
        f.write(f"Results:\n")
        f.write(f"  - Iterations completed: {result.get_num_iterations()}\n")
        f.write(f"  - Models trained: {len(result.models)}\n\n")
        
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
    print(f"{'='*60}\n")


def get_demo_configs() -> Dict[str, DemoConfig]:
    """
    Get all predefined demo configurations.
    
    Returns:
        Dictionary mapping demo keys to DemoConfig objects
    """
    from autotrend import generate_simple_wave, generate_piecewise_linear
    
    configs = {}
    
    # Demo 1: Simple Wave (Clean)
    configs['simple_wave_clean'] = DemoConfig(
        name="Simple Wave (Clean)",
        data_generator=lambda: generate_simple_wave(add_noise=False),
        window_size=10,
        max_models=5,
        error_percentile=40,
        demo_type="simple_wave"
    )
    
    # Demo 2: Simple Wave (Noisy)
    configs['simple_wave_noisy'] = DemoConfig(
        name="Simple Wave (Noisy)",
        data_generator=lambda: generate_simple_wave(add_noise=True, noise_strength=2),
        window_size=10,
        max_models=5,
        error_percentile=40,
        demo_type="simple_wave"
    )
    
    # Demo 3: Piecewise Linear Sequence (Increase-Decrease-Steady)
    configs['piecewise_ids'] = DemoConfig(
        name="Piecewise Linear Sequence (IDS)",
        data_generator=lambda: generate_piecewise_linear(
            trends=['increase', 'decrease', 'steady'],
            total_length=300,
            min_seg_len=50,
            max_seg_len=150
        ),
        window_size=5,
        max_models=10,
        error_percentile=50,
        demo_type="piecewise_linear"
    )
    
    # Demo 4: Piecewise Linear Sequence (Complex Pattern)
    configs['piecewise_complex'] = DemoConfig(
        name="Piecewise Linear Sequence (Complex)",
        data_generator=lambda: generate_piecewise_linear(
            trends=['increase', 'steady', 'decrease', 'increase', 'steady'],
            total_length=500,
            min_seg_len=60,
            max_seg_len=120
        ),
        window_size=25,
        max_models=15,
        error_percentile=35,
        percentile_step=2,
        update_threshold=True,
        demo_type="piecewise_linear"
    )
    
    return configs