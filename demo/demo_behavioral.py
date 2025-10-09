"""
Demo: Behavioral Sequence Decomposition
"""
import logging
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

from autotrend import decompose_llt, generate_behavioral_sequence, plot_error, plot_slope_comparison


def run_behavioral_demo(timestamp):
    """Run behavioral sequence decomposition demo"""
    
    logging.info("Generating behavioral sequence data...")
    
    # Generate data with different behaviors
    behaviors = ['increase', 'steady', 'decrease', 'increase', 'steady']
    np.random.seed(123)
    sequence = generate_behavioral_sequence(
        behaviors=behaviors,
        total_length=500,
        min_seg_len=50,
        max_seg_len=150
    )
    
    logging.info(f"  - Sequence length: {len(sequence)}")
    logging.info(f"  - Behaviors: {' -> '.join(behaviors)}")
    logging.info(f"  - Sequence range: [{sequence.min():.2f}, {sequence.max():.2f}]")
    logging.info(f"  - Mean: {sequence.mean():.2f}, Std: {sequence.std():.2f}")
    logging.info("")
    
    # Run decomposition
    logging.info("Running local linear trend decomposition...")
    logging.info("  Parameters:")
    logging.info("    - max_models: 8")
    logging.info("    - window_size: 15")
    logging.info("    - error_percentile: 50")
    logging.info("    - percentile_step: 3")
    logging.info("")
    
    trend_marks, models, process_logs = decompose_llt(
        seq=sequence,
        max_models=8,
        window_size=15,
        error_percentile=50,
        percentile_step=3,
        update_threshold=True
    )
    
    logging.info("Decomposition complete!")
    logging.info(f"  - Number of models fitted: {len(models)}")
    logging.info(f"  - Number of iterations: {len(process_logs)}")
    logging.info("")
    
    # Log model details
    logging.info("Model Details:")
    slopes = []
    for i, model in enumerate(models):
        slope = model.coef_[0]
        slopes.append(slope)
        intercept = model.intercept_
        trend_type = 'increasing' if slope > 0.1 else 'decreasing' if slope < -0.1 else 'steady'
        logging.info(f"  Model {i+1}: slope={slope:.6f}, intercept={intercept:.6f} ({trend_type})")
    logging.info("")
    
    # Analyze trend diversity
    logging.info("Trend Analysis:")
    has_increase = any(s > 0.1 for s in slopes)
    has_decrease = any(s < -0.1 for s in slopes)
    has_steady = any(-0.1 <= s <= 0.1 for s in slopes)
    logging.info(f"  - Captured increasing trends: {'Yes' if has_increase else 'No'}")
    logging.info(f"  - Captured decreasing trends: {'Yes' if has_decrease else 'No'}")
    logging.info(f"  - Captured steady trends: {'Yes' if has_steady else 'No'}")
    logging.info(f"  - Slope range: [{min(slopes):.4f}, {max(slopes):.4f}]")
    logging.info("")
    
    # Log iteration statistics
    logging.info("Iteration Statistics:")
    for i, (preds, errors, ranges, flags, threshold) in enumerate(process_logs):
        num_high_error = sum(flags)
        num_low_error = len(flags) - num_high_error
        avg_error = np.mean(errors)
        max_error = np.max(errors)
        
        logging.info(f"  Iteration {i+1}:")
        logging.info(f"    - Predictions made: {len(preds)}")
        logging.info(f"    - Average error: {avg_error:.4f}")
        logging.info(f"    - Max error: {max_error:.4f}")
        logging.info(f"    - Threshold (P{50 + i*3}): {threshold:.4f}")
        logging.info(f"    - High error points: {num_high_error}")
        logging.info(f"    - Low error points: {num_low_error}")
        logging.info(f"    - Focus ranges: {len(ranges)}")
    logging.info("")
    
    # Generate and save plots
    fig_dir = Path('outputs/figures')
    
    logging.info("Generating visualizations...")
    
    # Error plot
    logging.info("  - Creating error analysis plot...")
    plot_error(sequence, process_logs, window_size=15)
    error_plot = fig_dir / f'behavioral_error_{timestamp}.png'
    plt.savefig(error_plot, dpi=150, bbox_inches='tight')
    plt.close()
    logging.info(f"    Saved: {error_plot}")
    
    # Slope comparison plot
    logging.info("  - Creating slope comparison plot...")
    plot_slope_comparison(models, x_range=(-10, 10))
    slope_plot = fig_dir / f'behavioral_slopes_{timestamp}.png'
    plt.savefig(slope_plot, dpi=150, bbox_inches='tight')
    plt.close()
    logging.info(f"    Saved: {slope_plot}")
    
    logging.info("")