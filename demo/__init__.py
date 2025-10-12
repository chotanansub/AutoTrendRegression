"""
LLT Demo Package

Demonstrates AutoTrend's Local Linear Trend (LLT) decomposition on various synthetic time series patterns.

Package Structure:
    demo_runner: Reusable utility for running demos with consistent output
    cases: Collection of demo scenarios with different data patterns

Demo Cases:
    - piecewise_linear: Linear segments with trend changes
    - simple_wave: Stationary sinusoidal patterns
    - nonstationary: Non-stationary waves with varying amplitude

Quick Start:
    # Run all demos at once
    $ python demo/00_run_all.py
    
    # Run specific demo
    $ python -m demo.cases.piecewise_linear
    $ python -m demo.cases.simple_wave
    $ python -m demo.cases.nonstationary

Adding New Demos:
    1. Create new file in demo/cases/
    2. Import DemoRunner from demo.demo_runner
    3. Define main() function with data generation and runner.run() calls
    4. Add import to demo/cases/__init__.py
    5. Add to demo list in demo/00_run_all.py

Output:
    All demos save results to output/ directory organized by demo type:
    - {demo_name}_error.png
    - {demo_name}_slopes.png
    - {demo_name}_full_decomposition.png
    - {demo_name}_iteration_grid.png
    - {demo_name}_model_statistics.png
    - {demo_name}_log.txt
"""

__all__ = []