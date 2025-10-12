#!/usr/bin/env python3
"""
Demo: Simple Wave Pattern
Demonstrates LLT on sine wave with amplitude envelope and linear trend.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from demo.demo_runner import DemoRunner
from autotrend import generate_simple_wave


def main():
    runner = DemoRunner(output_subdir="simple_wave")
    
    # Demo 1: Clean version
    sequence_clean = generate_simple_wave(add_noise=False)
    
    runner.run(
        name="Simple Wave (Clean)",
        sequence=sequence_clean,
        window_size=10,
        max_models=5,
        error_percentile=40
    )
    
    # Demo 2: Noisy version
    sequence_noisy = generate_simple_wave(add_noise=True, noise_strength=2)
    
    runner.run(
        name="Simple Wave (Noisy)",
        sequence=sequence_noisy,
        window_size=10,
        max_models=5,
        error_percentile=40
    )


if __name__ == "__main__":
    main()