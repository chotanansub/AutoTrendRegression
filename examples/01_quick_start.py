#!/usr/bin/env python3
"""
Quick Start Example for AutoTrend

This example demonstrates the simplest way to use AutoTrend for
Local Linear Trend (LLT) decomposition on a time series.
"""
import numpy as np
from autotrend import decompose_llt, generate_simple_wave

# Generate a simple sine wave with linear trend
sequence = generate_simple_wave(length=500, add_noise=False)

# Run LLT decomposition with default parameters
result = decompose_llt(seq=sequence)

# Print basic results
print(f"Decomposition completed!")
print(f"  - Number of iterations: {result.get_num_iterations()}")
print(f"  - Number of models: {len(result.models)}")
print(f"  - Trend segments: {len(result.get_trend_segments())}")

# Access decomposition results
print(f"\nTrend Segments:")
for start, end, iteration in result.get_trend_segments():
    print(f"  [{start:4d}, {end:4d}) -> Iteration {iteration}")

# Display model parameters
print(f"\nModel Parameters:")
for i, model in enumerate(result.models, 1):
    slope = model.coef_[0]
    intercept = model.intercept_
    print(f"  Model {i}: slope={slope:.6f}, intercept={intercept:.6f}")

# Generate visualization (displays interactively)
result.plot_full_decomposition()

# Optionally: save all plots to a directory
# result.plot_all(output_dir="my_results", prefix="quick_start", show=False)