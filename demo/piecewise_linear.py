#!/usr/bin/env python3
"""
Demo: Piecewise Linear Sequences
Demonstrates LLT on sequences with distinct linear trend segments.
"""
from demo_utils import DemoConfig, run_single_demo
from autotrend import generate_piecewise_linear


def main():
    # Simple pattern: Increase -> Decrease -> Steady
    config_ids = DemoConfig(
        name="Piecewise Linear Sequence (IDS)",
        data_generator=lambda: generate_piecewise_linear(
            trends=['increase', 'decrease', 'steady'],
            total_length=300,
            min_seg_len=50,
            max_seg_len=150
        ),
        window_size=20,
        max_models=10,
        error_percentile=30,
        demo_type="piecewise_linear"
    )
    run_single_demo(config_ids, verbose=True)
    
    # Complex pattern with adaptive threshold
    config_complex = DemoConfig(
        name="Piecewise Linear Sequence (Complex)",
        data_generator=lambda: generate_piecewise_linear(
            trends=['increase', 'steady', 'decrease', 'increase', 'steady'],
            total_length=500,
            min_seg_len=60,
            max_seg_len=120
        ),
        window_size=25,
        max_models=15,
        error_percentile=50,
        percentile_step=2,
        update_threshold=True,
        demo_type="piecewise_linear"
    )
    run_single_demo(config_complex, verbose=True)


if __name__ == "__main__":
    main()