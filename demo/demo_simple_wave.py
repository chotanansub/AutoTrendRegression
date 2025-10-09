"""
Demo: Simple Wave Decomposition
"""
import logging
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path

from autotrend import decompose_llt, generate_simeple_wave, plot_error, plot_slope_comparison


def run_simple_wave_demo(timestamp):
    """Run simple wave decomposition demo"""
    
    logging.info("Generating simple wave data...")
    
    # Generate data
    sequence = generate_simeple_wave(add_noise=True, noise_strength=1.5, seed=42)
    
    logging.info(f"  - Sequence length: {len(sequence)}")
    logging.info(f"  - Sequence range: [{sequence.min():.2f}, {sequence.max():.2f}]")
    logging.info(f"  - Mean: {sequence.mean():.2f}, Std: {sequence.std():.2f}")
    logging.info("")
    
    # Run decomposition
    logging.info("Running local linear trend decomposition...")
    logging.info("  Parameters:")
    logging.info("    - max_models: 5")
    logging.info("    - window_size: 10")
    logging.info("    - error_percentile: 60")
    logging.info("    - percentile_step: 5")
    logging.info("")
    
    trend_marks, models, process_logs = decompose_llt(
        seq=sequence,
        max_models=5,
        window_size=10,
        error_percentile=60,
        percentile_step=5,
        update_threshold=True
    )
    
    logging.info("Decomposition complete!")
    logging.info(f"  - Number of models fitted: {len(models)}")
    logging.info(f"  - Number of iterations: {len(process_logs)}")
    logging.info("")
    
    # Log model details
    logging.info("Model Details:")
    for i, model in enumerate(models):
        slope = model.coef_[0]
        intercept = model.intercept_
        trend_type = 'increasing' if slope > 0.1 else 'decreasing' if slope < -0.1 else 'flat'
        logging.info(f"  Model {i+1}: slope={slope:.6f}, intercept={intercept:.6f} ({trend_type})")
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
        logging.info(f"    - Threshold (P60): {threshold:.4f}")
        logging.info(f"    - High error points: {num_high_error}")
        logging.info(f"    - Low error points: {num_low_error}")
    logging.info("")
    
    # Generate and save plots
    fig_dir = Path('outputs/figures')
    
    logging.info("Generating visualizations...")
    
    # Error plot
    logging.info("  - Creating error analysis plot...")
    plot_error(sequence, process_logs, window_size=10)
    error_plot = fig_dir / f'simple_wave_error_{timestamp}.png'
    plt.savefig(error_plot, dpi=150, bbox_inches='tight')
    plt.close()
    logging.info(f"    Saved: {error_plot}")
    
    # Slope comparison plot
    logging.info("  - Creating slope comparison plot...")
    plot_slope_comparison(models, x_range=(-5, 5))
    slope_plot = fig_dir / f'simple_wave_slopes_{timestamp}.png'
    plt.savefig(slope_plot, dpi=150, bbox_inches='tight')
    plt.close()
    logging.info(f"    Saved: {slope_plot}")
    
    logging.info("")