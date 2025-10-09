#!/usr/bin/env python3
"""
Demo: Behavioral Sequences
Demonstrates LLT on sequences with distinct behavioral segments.
"""
from demo_utils import DemoConfig, run_single_demo
from autotrend import generate_behavioral_sequence


def main():
    # Simple pattern: Increase -> Decrease -> Steady
    config_ids = DemoConfig(
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
    run_single_demo(config_ids, verbose=True)
    
    # Complex pattern with adaptive threshold
    config_complex = DemoConfig(
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
    run_single_demo(config_complex, verbose=True)


if __name__ == "__main__":
    main()