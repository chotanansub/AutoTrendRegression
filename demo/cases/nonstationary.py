#!/usr/bin/env python3
"""
Demo: Non-stationary Wave Pattern
Demonstrates LLT on sine wave with variable amplitude envelope and linear trend.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from demo.demo_runner import DemoRunner
from autotrend import generate_nonstationary_wave


def main():
    runner = DemoRunner(output_subdir="nonstationary_wave")
    
    # Demo 1: Clean version
    sequence_clean = generate_nonstationary_wave(add_noise=False)
    
    runner.run(
        name="Nonstationary Wave (Clean)",
        sequence=sequence_clean,
        window_size=15,
        max_models=8,
        error_percentile=45
    )
    
    # Demo 2: Noisy version
    sequence_noisy = generate_nonstationary_wave(add_noise=True, noise_strength=2)
    
    runner.run(
        name="Nonstationary Wave (Noisy)",
        sequence=sequence_noisy,
        window_size=15,
        max_models=10,
        error_percentile=50,
        percentile_step=3,
        update_threshold=True
    )


if __name__ == "__main__":
    main()