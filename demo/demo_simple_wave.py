"""
Demo: Simple Wave with LLT Decomposition

This demo shows how to use the Local Linear Trend (LLT) method
on a simple sinusoidal wave with varying amplitude and noise.
"""

import numpy as np
import matplotlib.pyplot as plt
from autotrend import decompose_llt, plot_error, plot_slope_comparison
from autotrend import generate_simeple_wave


def main():
    print("=" * 70)
    print("Demo: Simple Wave Decomposition with Local Linear Trend (LLT)")
    print("=" * 70)
    
    # ============================================================
    # Generate Test Data
    # ============================================================
    print("\n📊 Generating test data...")
    
    sequence = generate_simeple_wave(
        add_noise=True,
        noise_strength=2,
        seed=6969
    )
    
    print(f"   - Sequence length: {len(sequence)}")
    print(f"   - Min value: {np.min(sequence):.2f}")
    print(f"   - Max value: {np.max(sequence):.2f}")
    print(f"   - Mean value: {np.mean(sequence):.2f}")
    
    # ============================================================
    # Run LLT Decomposition
    # ============================================================
    print("\n🔍 Running LLT decomposition...")
    
    result = decompose_llt(
        seq=sequence,
        max_models=10,
        window_size=5,
        error_percentile=40,
        percentile_step=0,
        update_threshold=False
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
    for start, end, iteration in segments[:10]:  # Show first 10
        segment_length = end - start
        print(f"   Iteration {iteration}: [{start:3d}:{end:3d}] "
              f"({segment_length:3d} points)")
    
    if len(segments) > 10:
        print(f"   ... and {len(segments) - 10} more segments")
    
    # Show iteration-wise statistics
    print(f"\n🎯 Iteration Statistics:")
    for i in range(1, result.get_num_iterations() + 1):
        indices, predictions = result.get_predictions_by_iteration(i)
        if len(indices) > 0:
            actual_values = sequence[indices]
            errors = np.abs(actual_values - predictions)
            print(f"   Iteration {i}: {len(indices):3d} points, "
                  f"avg error: {np.mean(errors):.4f}, "
                  f"max error: {np.max(errors):.4f}")
    
    # Show model parameters
    print(f"\n📐 Model Parameters:")
    for i, model in enumerate(result.models, 1):
        slope = model.coef_[0]
        intercept = model.intercept_
        angle_deg = np.degrees(np.arctan(slope))
        print(f"   Model {i}: slope={slope:7.4f}, "
              f"intercept={intercept:7.4f}, "
              f"angle={angle_deg:6.2f}°")
    
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
    
    # ============================================================
    # Visualizations
    # ============================================================
    print("\n🎨 Generating visualizations...")
    
    # Plot 1: Detailed error analysis
    print("   - Creating detailed error plot...")
    plot_error(sequence, result.process_logs, window_size=5)
    
    # Plot 2: Slope comparison
    print("   - Creating slope comparison plot...")
    plot_slope_comparison(result.models)
    
    # Plot 3: Predictions vs Actual
    print("   - Creating predictions comparison plot...")
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Subplot 1: Original vs Predictions
    ax1 = axes[0]
    ax1.plot(sequence, label='Original Series', 
             linewidth=2, alpha=0.7, color='black')
    ax1.plot(result.prediction_marks, label='LLT Predictions', 
             linewidth=2, linestyle='--', alpha=0.8, color='purple')
    ax1.set_title('Simple Wave: Original Series vs LLT Predictions', 
                  fontsize=14, fontweight='bold')
    ax1.set_xlabel('Time Index')
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
    ax2.set_xlabel('Time Index')
    ax2.set_ylabel('|Error|')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Plot 4: Trend marks visualization
    print("   - Creating trend marks visualization...")
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Create color map for iterations
    unique_trends = np.unique(result.trend_marks[~np.isnan(result.trend_marks)])
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_trends)))
    
    # Plot original series
    ax.plot(sequence, color='lightgray', linewidth=1, alpha=0.5, 
            label='Original Series')
    
    # Overlay trend segments with different colors
    for i, trend_val in enumerate(unique_trends):
        mask = result.trend_marks == trend_val
        indices = np.where(mask)[0]
        ax.scatter(indices, sequence[indices], 
                  color=colors[i], s=20, alpha=0.6,
                  label=f'Iteration {int(trend_val)}')
    
    ax.set_title('Trend Segmentation by Iteration', 
                fontsize=14, fontweight='bold')
    ax.set_xlabel('Time Index')
    ax.set_ylabel('Value')
    ax.legend(loc='upper left', ncol=2)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    print("\n" + "=" * 70)
    print("✨ Demo Complete!")
    print("=" * 70)


def run_simple_wave_demo():
    """Alias for main() for backward compatibility."""
    main()


if __name__ == "__main__":
    main()