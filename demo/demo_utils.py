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

from autotrend import decompose_llt, plot_error, plot_slope_comparison


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
    
    def get_output_path(self, suffix: str = "") -> Path:
        """Generate output file path."""
        base_name = self.name.lower().replace(" ", "_")
        if suffix:
            return Path(self.output_dir) / f"{base_name}_{suffix}.png"
        return Path(self.output_dir) / f"{base_name}.png"


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
    
    # Ensure output directory exists
    output_path = Path(config.output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate data
    sequence = config.data_generator()
    print(f"  Sequence length: {len(sequence)}")
    
    # Run LLT decomposition
    result = decompose_llt(
        seq=sequence,
        max_models=config.max_models,
        window_size=config.window_size,
        error_percentile=config.error_percentile,
        percentile_step=config.percentile_step,
        update_threshold=config.update_threshold,
        is_quiet=not verbose
    )
    
    print(f"  Iterations: {result.get_num_iterations()}, Models: {len(result.models)}")
    
    # Generate and save error plot
    plot_error(sequence, result.process_logs, config.window_size)
    error_plot_path = config.get_output_path("error")
    plt.savefig(error_plot_path, dpi=150, bbox_inches='tight')
    plt.close('all')
    print(f"  ✓ {error_plot_path}")
    
    # Generate and save slope comparison plot
    if len(result.models) > 0:
        plot_slope_comparison(result.models, x_range=(-5, 5))
        slope_plot_path = config.get_output_path("slopes")
        plt.savefig(slope_plot_path, dpi=150, bbox_inches='tight')
        plt.close('all')
        print(f"  ✓ {slope_plot_path}")
    
    # Save summary log
    log_path = config.get_output_path("log").with_suffix('.txt')
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
    from autotrend import generate_simeple_wave, generate_behavioral_sequence
    
    configs = {}
    
    # Demo 1: Simple Wave (Clean)
    configs['simple_wave_clean'] = DemoConfig(
        name="Simple Wave (Clean)",
        data_generator=lambda: generate_simeple_wave(add_noise=False),
        window_size=10,
        max_models=5,
        error_percentile=40
    )
    
    # Demo 2: Simple Wave (Noisy)
    configs['simple_wave_noisy'] = DemoConfig(
        name="Simple Wave (Noisy)",
        data_generator=lambda: generate_simeple_wave(add_noise=True, noise_strength=2),
        window_size=10,
        max_models=5,
        error_percentile=40
    )
    
    # Demo 3: Behavioral Sequence (Increase-Decrease-Steady)
    configs['behavioral_ids'] = DemoConfig(
        name="Behavioral Sequence (IDS)",
        data_generator=lambda: generate_behavioral_sequence(
            behaviors=['increase', 'decrease', 'steady'],
            total_length=300,
            min_seg_len=50,
            max_seg_len=150
        ),
        window_size=20,
        max_models=10,
        error_percentile=30
    )
    
    # Demo 4: Behavioral Sequence (Complex Pattern)
    configs['behavioral_complex'] = DemoConfig(
        name="Behavioral Sequence (Complex)",
        data_generator=lambda: generate_behavioral_sequence(
            behaviors=['increase', 'steady', 'decrease', 'increase', 'steady'],
            total_length=500,
            min_seg_len=60,
            max_seg_len=120
        ),
        window_size=25,
        max_models=15,
        error_percentile=35,
        percentile_step=2,
        update_threshold=True
    )
    
    return configs