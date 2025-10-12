#!/usr/bin/env python3
"""
Quick Start Example for AutoTrend

This example demonstrates the simplest way to use AutoTrend for
Local Linear Trend (LLT) decomposition on a time series.
"""
import numpy as np
from autotrend import decompose_llt, generate_simple_wave

# Generate a simple sine wave 
sequence = generate_simple_wave(length=500, frequency=4, add_noise=True)

# Run LLT decomposition with default parameters
result = decompose_llt(seq=sequence)

# Generate visualization (displays interactively)
result.plot_full_decomposition()

# Save all plots 
result.plot_all(output_dir="my_results")