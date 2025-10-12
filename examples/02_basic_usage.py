#!/usr/bin/env python3
"""
Basic Usage Example for AutoTrend

This example demonstrates common usage patterns and API features:
- Functional API vs Object-based API
- Parameter customization
- Accessing decomposition results
- Generating different visualizations
"""
import numpy as np
from autotrend import decompose_llt, DecomposeLLT, generate_piecewise_linear

print("="*60)
print("AutoTrend: Basic Usage Examples")
print("="*60)

# Generate a piecewise linear sequence
sequence = generate_piecewise_linear(
    trends=['increase', 'decrease', 'steady'],
    total_length=300,
    min_seg_len=50,
    max_seg_len=150
)

print(f"\nGenerated sequence with length: {len(sequence)}")

# ============================================================
# Example 1: Functional API (Quick, one-off usage)
# ============================================================
print("\n" + "="*60)
print("Example 1: Functional API")
print("="*60)

result = decompose_llt(
    seq=sequence,
    max_models=10,
    window_size=20,
    error_percentile=40,
    is_quiet=True
)

print(f"✓ Decomposition completed")
print(f"  - Iterations: {result.get_num_iterations()}")
print(f"  - Models trained: {len(result.models)}")

# Access specific iteration results
indices, predictions = result.get_predictions_by_iteration(iteration=1)
print(f"  - Iteration 1 covered {len(indices)} points")

# ============================================================
# Example 2: Object-based API (Reusable configuration)
# ============================================================
print("\n" + "="*60)
print("Example 2: Object-based API")
print("="*60)

# Create decomposer with custom parameters
decomposer = DecomposeLLT(
    max_models=10,
    window_size=20,
    error_percentile=40,
    update_threshold=True,
    percentile_step=2,
    is_quiet=True
)

# Fit to sequence
result2 = decomposer.fit(sequence)

print(f"✓ Decomposition completed")
print(f"  - Iterations: {result2.get_num_iterations()}")
print(f"  - Configuration can be reused for multiple sequences")

# Get estimator parameters (scikit-learn style)
params = decomposer.get_params()
print(f"  - Current parameters: {params}")

# ============================================================
# Example 3: Accessing Decomposition Components
# ============================================================
print("\n" + "="*60)
print("Example 3: Accessing Results")
print("="*60)

# Trend marks: which iteration labeled each point
print(f"Trend marks shape: {result.trend_marks.shape}")
print(f"Unique iterations: {np.unique(result.trend_marks[~np.isnan(result.trend_marks)])}")

# Prediction marks: predicted values for each point
print(f"Prediction marks shape: {result.prediction_marks.shape}")
print(f"Points with predictions: {np.sum(~np.isnan(result.prediction_marks))}")

# Models: linear regression models from each iteration
print(f"Number of models: {len(result.models)}")

# Trend segments: contiguous regions
segments = result.get_trend_segments()
print(f"Number of trend segments: {len(segments)}")
for i, (start, end, iteration) in enumerate(segments[:3], 1):
    print(f"  Segment {i}: indices [{start}, {end}), iteration {iteration}")

# ============================================================
# Example 4: Visualization Options
# ============================================================
print("\n" + "="*60)
print("Example 4: Visualization")
print("="*60)

# Individual plots
print("Generating individual plots...")

# 1. Full decomposition view
result.plot_full_decomposition()
print("  ✓ Full decomposition plot")

# 2. Error analysis
result.plot_error()
print("  ✓ Error analysis plot")

# 3. Slope comparison
result.plot_slopes()
print("  ✓ Slope comparison plot")

# 4. Iteration grid
result.plot_iteration_grid()
print("  ✓ Iteration grid plot")

# 5. Model statistics
result.plot_statistics()
print("  ✓ Model statistics plot")

# Generate all plots at once (saves to directory)
# result.plot_all(output_dir="output/basic_usage", prefix="example", show=False)

print("\n" + "="*60)
print("✓ Basic usage examples completed!")
print("="*60)

# ============================================================
# Example 5: Convenience Method (fit and plot)
# ============================================================
print("\n" + "="*60)
print("Example 5: Fit and Plot (Convenience)")
print("="*60)

# One-liner to fit and visualize
decomposer = DecomposeLLT(window_size=15, max_models=8, is_quiet=True)
result3 = decomposer.fit_plot(
    sequence,
    plot_types=['full_decomposition'],  # Specify which plots to generate
    show=True  # Display interactively
)

print(f"✓ Fitted and plotted in one call")
print(f"  - Iterations: {result3.get_num_iterations()}")