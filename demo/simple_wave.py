#!/usr/bin/env python3
"""
Demo: Simple Wave Pattern
Demonstrates LLT on sine wave with amplitude envelope and linear trend.
"""
from demo_utils import DemoConfig, run_single_demo
from autotrend import generate_simple_wave


def main():
    # Clean version
    config_clean = DemoConfig(
        name="Simple Wave (Clean)",
        data_generator=lambda: generate_simple_wave(add_noise=False),
        window_size=10,
        max_models=5,
        error_percentile=40
    )
    run_single_demo(config_clean, verbose=True)
    
    # Noisy version
    config_noisy = DemoConfig(
        name="Simple Wave (Noisy)",
        data_generator=lambda: generate_simple_wave(add_noise=True, noise_strength=2),
        window_size=10,
        max_models=5,
        error_percentile=40
    )
    run_single_demo(config_noisy, verbose=True)


if __name__ == "__main__":
    main()