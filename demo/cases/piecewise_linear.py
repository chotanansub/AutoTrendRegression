#!/usr/bin/env python3
"""
Demo: Piecewise Linear Sequences
Demonstrates LLT on sequences with distinct linear trend segments.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from demo.demo_runner import DemoRunner
from autotrend import generate_piecewise_linear


def main():
    runner = DemoRunner(output_subdir="piecewise_linear")
    
    # Demo 1: Simple pattern (Increase -> Decrease -> Steady)
    sequence_ids = generate_piecewise_linear(
        trends=['increase', 'decrease', 'steady'],
        total_length=300,
        min_seg_len=50,
        max_seg_len=150
    )
    
    runner.run(
        name="Piecewise Linear Sequence (IDS)",
        sequence=sequence_ids,
        window_size=20,
        max_models=10,
        error_percentile=30
    )
    
    # Demo 2: Complex pattern with adaptive threshold
    sequence_complex = generate_piecewise_linear(
        trends=['increase', 'steady', 'decrease', 'increase', 'steady'],
        total_length=500,
        min_seg_len=60,
        max_seg_len=120
    )
    
    runner.run(
        name="Piecewise Linear Sequence (Complex)",
        sequence=sequence_complex,
        window_size=25,
        max_models=15,
        error_percentile=50,
        percentile_step=2,
        update_threshold=True
    )


if __name__ == "__main__":
    main()