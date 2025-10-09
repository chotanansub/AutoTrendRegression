"""
Demo: Behavioral Sequence with LLT Decomposition

This demo shows how to use the Local Linear Trend (LLT) method
on a behavioral sequence with distinct trend patterns 
(increase, steady, decrease).
"""

import numpy as np
import matplotlib.pyplot as plt
from autotrend import decompose_llt, plot_error, plot_slope_comparison
from autotrend import generate_behavioral_sequence


def main():
    print("=" * 70)
    print("Demo: Behavioral Sequence Decomposition with LLT")
    print("=" * 70)
    
    # ============================================================
    # Generate Behavioral Sequence
    # ============================================================
    print("\n📊 Generating behavioral sequence...")
    
    behaviors = ['increase', 'steady', 'decrease', 'increase', 'steady']
    
    sequence = generate_behavioral_sequence(
        behaviors=behaviors,
        total_length=500,
        min_seg_len=50,
        max_seg_len=150
    )
    
    print(f"   - Sequence length: {len(sequence)}")
    print(f"   - Behavior patterns: {behaviors}")
    print(f"   - Min value: {np.min(sequence):.2f}")
    print(f"   - Max value: {np.max(sequence):.2f}")
    print(f"   - Mean value: {np.mean(sequence):.2f}")
    
    # ============================================================
    # Run LLT Decomposition with Adaptive Threshold
    # ============================================================
    print("\n🔍 Running LLT decomposition with adaptive threshold...")
    
    result = decompose_llt(
        seq=sequence,
        max_models=15,
        window_size=10,
        error_percentile=30,
        percentile_step=5,
        update_threshold=True  # Adaptive threshold
    )
    
    # ============================================================
    # Display Results
    # ============================================================
    print(f"\n✅ Decomposition Complete!")
    print(f"   - Iterations completed: {result.get_num_iterations()}")
    print(f"   - Models generated: {len(result.models)}")
    print(f"   - Trend marks shape: {result.trend_marks.shape}")
    print(f"   - Prediction marks shape: {result.prediction_marks.shape}")
    
    # Show trend segments
    print(f"\n📈 Trend Segments Detected:")
    segments = result.get_trend_segments()
    print(f"   Total segments: {len(segments)}")
    
    for start, end, iteration in segments[:15]:  # Show first 15
        segment_length = end - start
        segment_data = sequence[start:end]
        segment_slope = (segment_data[-1] - segment_data[0]) / segment_length if segment_length > 0 else 0
        print(f"   Iteration {iteration:2d}: [{start:3d}:{end:3d}] "
              f"({segment_length:3d} pts) slope≈{segment_slope:6.3f}")
    
    if len(segments) > 15:
        print(f"   ... and {len(segments) - 15} more segments")
    
    # Show iteration-wise statistics
    print(f"\n🎯 Iteration Analysis:")
    for i in range(1, result.get_num_iterations() + 1):
        indices, predictions = result.get_predictions_by_iteration(i)
        if len(indices) > 0:
            actual_values = sequence[indices]
            errors = np.abs(actual_values - predictions)
            print(f"   Iteration {i:2d}: {len(indices):3d} points, "
                  f"avg error: {np.mean(errors):.4f}, "
                  f"max error: {np.max(errors):.4f}, "
                  f"std error: {np.std(errors):.4f}")
    
    # Show model parameters and categorize trends
    print(f"\n📐 Model Parameters & Trend Classification:")
    for i, model in enumerate(result.models, 1):
        slope = model.coef_[0]
        intercept = model.intercept_
        angle_deg = np.degrees(np.arctan(slope))
        
        # Classify trend based on slope
        if slope > 0.1:
            trend_type = "INCREASE"
        elif slope < -0.1:
            trend_type = "DECREASE"
        else:
            trend_type = "STEADY  "
        
        print(f"   Model {i:2d} [{trend_type}]: slope={slope:7.4f}, "
              f"intercept={intercept:7.4f}, angle={angle_deg:6.2f}°")
    
    # ============================================================
    # Prediction Quality Analysis
    # ============================================================
    print(f"\n📊 Prediction Quality:")
    
    # Calculate prediction errors
    valid_mask = ~np.isnan(result.prediction_marks)
    prediction_errors = np.abs(sequence - result.prediction_marks)
    valid_errors = prediction_errors[valid_mask]
    
    print(f"   - Mean Absolute Error: {np.mean(valid_errors):.4f}")
    print(f"   - Median Absolute Error: {np.median(valid_errors):.4f}")
    print(f"   - Max Absolute Error: {np.max(valid_errors):.4f}")
    print(f"   - Std Dev of Errors: {np.std(valid_errors):.4f}")
    print(f"   - Coverage: {np.sum(valid_mask) / len(sequence) * 100:.1f}%")
    
    # Error percentiles
    percentiles = [25, 50, 75, 90, 95]
    print(f"\n   Error Percentiles:")
    for p in percentiles:
        print(f"      {p}th percentile: {np.percentile(valid_errors, p):.4f}")
    
    # ============================================================
    # Trend Type Distribution
    # ============================================================
    print(f"\n📊 Trend Type Distribution:")
    
    increasing_models = sum(1 for m in result.models if m.coef_[0] > 0.1)
    decreasing_models = sum(1 for m in result.models if m.coef_[0] < -0.1)
    steady_models = len(result.models) - increasing_models - decreasing_models
    
    print(f"   - Increasing trends: {increasing_models} models "
          f"({increasing_models/len(result.models)*100:.1f}%)")
    print(f"   - Decreasing trends: {decreasing_models} models "
          f"({decreasing_models/len(result.models)*100:.1f}%)")
    print(f"   - Steady trends: {steady_models} models "
          f"({steady_models/len(result.models)*100:.1f}%)")
    
    # ============================================================
    # Visualizations
    # ============================================================
    print("\n🎨 Generating visualizations...")
    
    # Plot 1: Detailed error analysis
    print("   - Creating detailed error plot...")
    plot_error(sequence, result.process_logs, window_size=10)
    
    # Plot 2: Slope comparison
    print("   - Creating slope comparison plot...")
    plot_slope_comparison(result.models, x_range=(-10, 10))
    
    # Plot 3: Predictions vs Actual with Behavior Annotation
    print("   - Creating predictions comparison plot...")
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    
    # Subplot 1: Original vs Predictions
    ax1 = axes[0]
    ax1.plot(sequence, label='Original Behavioral Sequence', 
             linewidth=2, alpha=0.7, color='black')
    ax1.plot(result.prediction_marks, label='LLT Predictions', 
             linewidth=2, linestyle='--', alpha=0.8, color='purple')
    ax1.set_title('Behavioral Sequence: Original vs LLT Predictions', 
                  fontsize=14, fontweight='bold')
    ax1.set_ylabel('Value')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Subplot 2: Prediction Errors
    ax2 = axes[1]
    ax2.plot(prediction_errors, linewidth=1.5, color='red', alpha=0.7)
    ax2.fill_between(range(len(prediction_errors)), 0, prediction_errors, 
                      alpha=0.3, color='red')
    
    # Add statistics lines
    ax2.axhline(np.mean(valid_errors), color='blue', linestyle='--', 
               label=f'Mean: {np.mean(valid_errors):.4f}', linewidth=2)
    ax2.axhline(np.median(valid_errors), color='green', linestyle='--', 
               label=f'Median: {np.median(valid_errors):.4f}', linewidth=2)
    
    ax2.set_title('Absolute Prediction Error', 
                  fontsize=14, fontweight='bold')
    ax2.set_ylabel('|Error|')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    
    # Subplot 3: Trend Classification
    ax3 = axes[2]
    
    # Color-code by detected trend type
    for start, end, iteration in segments:
        model = result.models[iteration - 1]
        slope = model.coef_[0]
        
        if slope > 0.1:
            color = 'green'
            alpha = 0.3
        elif slope < -0.1:
            color = 'red'
            alpha = 0.3
        else:
            color = 'blue'
            alpha = 0.2
        
        ax3.axvspan(start, end, facecolor=color, alpha=alpha)
    
    ax3.plot(sequence, color='black', linewidth=1.5, alpha=0.8)
    ax3.set_title('Detected Trend Types (Green=Increase, Red=Decrease, Blue=Steady)', 
                  fontsize=14, fontweight='bold')
    ax3.set_xlabel('Time Index')
    ax3.set_ylabel('Value')
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Plot 4: Iteration-wise coverage
    print("   - Creating iteration coverage plot...")
    fig, ax = plt.subplots(figsize=(14, 6))
    
    unique_trends = np.unique(result.trend_marks[~np.isnan(result.trend_marks)])
    colors = plt.cm.viridis(np.linspace(0, 1, len(unique_trends)))
    
    bottom = np.zeros(len(sequence))
    
    for i, trend_val in enumerate(unique_trends):
        mask = result.trend_marks == trend_val
        heights = mask.astype(float)
        ax.bar(range(len(sequence)), heights, bottom=bottom, 
              color=colors[i], alpha=0.7, width=1.0,
              label=f'Iteration {int(trend_val)}')
        bottom += heights
    
    ax.set_title('Coverage by Iteration', fontsize=14, fontweight='bold')
    ax.set_xlabel('Time Index')
    ax.set_ylabel('Iteration')
    ax.legend(loc='upper right', ncol=3)
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.show()
    
    # Plot 5: Model slopes distribution
    print("   - Creating model slopes distribution...")
    fig, ax = plt.subplots(figsize=(10, 6))
    
    slopes = [m.coef_[0] for m in result.models]
    colors_bar = ['green' if s > 0.1 else 'red' if s < -0.1 else 'blue' 
                  for s in slopes]
    
    bars = ax.bar(range(1, len(slopes) + 1), slopes, color=colors_bar, alpha=0.7)
    ax.axhline(0, color='black', linewidth=1, linestyle='-')
    ax.axhline(0.1, color='green', linewidth=1, linestyle='--', alpha=0.5)
    ax.axhline(-0.1, color='red', linewidth=1, linestyle='--', alpha=0.5)
    
    ax.set_title('Model Slopes Distribution', fontsize=14, fontweight='bold')
    ax.set_xlabel('Model (Iteration)')
    ax.set_ylabel('Slope')
    ax.grid(True, alpha=0.3)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', alpha=0.7, label='Increasing (slope > 0.1)'),
        Patch(facecolor='blue', alpha=0.7, label='Steady (-0.1 ≤ slope ≤ 0.1)'),
        Patch(facecolor='red', alpha=0.7, label='Decreasing (slope < -0.1)')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.show()
    
    print("\n" + "=" * 70)
    print("✨ Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()