import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def plot_full_decomposition(sequence, result, figsize=(16, 10)):
    """
    Plot full LLT decomposition showing predictions colored by iteration.
    
    3-panel layout:
    - Panel 1: Original series with predictions by iteration
    - Panel 2: Trend segments with local linear fits
    - Panel 3: Residuals
    
    Args:
        sequence: Original time series
        result: LLTResult object from decompose_llt
        figsize: Figure size tuple
    """
    sns.set(style="whitegrid", context="talk", palette="muted")
    
    fig, axes = plt.subplots(3, 1, figsize=figsize, 
                            gridspec_kw={'height_ratios': [3, 2, 1]})
    
    trend_marks = result.trend_marks
    prediction_marks = result.prediction_marks
    num_iterations = result.get_num_iterations()
    
    colors = sns.color_palette("husl", num_iterations)
    
    # Panel 1: Original Series with Predictions by Iteration
    ax1 = axes[0]
    
    ax1.plot(sequence, color='black', linewidth=2, label='Original Series', zorder=1)
    
    for iteration in range(1, num_iterations + 1):
        mask = trend_marks == iteration
        indices = np.where(mask)[0]
        predictions = prediction_marks[mask]
        
        if len(indices) > 0:
            ax1.scatter(indices, predictions, 
                       color=colors[iteration-1], 
                       s=50, alpha=0.7, 
                       label=f'Iteration {iteration}',
                       zorder=3, edgecolors='white', linewidth=0.5)
    
    ax1.set_title('Local Linear Trend Decomposition: Predictions by Iteration', 
                 fontsize=16, pad=15)
    ax1.set_ylabel('Value', fontsize=14)
    ax1.legend(loc='upper left', fontsize=10, ncol=min(4, num_iterations + 1), 
               framealpha=0.9)
    ax1.grid(True, alpha=0.3)
    
    # Panel 2: Trend Segments with Regression Lines
    ax2 = axes[1]
    
    ax2.plot(sequence, color='gray', linewidth=1.5, alpha=0.5, 
            label='Original Series', zorder=1)
    
    segments = result.get_trend_segments()
    
    # Group segments by iteration to avoid duplicate labels
    iteration_plotted = set()
    
    for start, end, iteration in segments:
        color = colors[iteration-1]
        
        segment_indices = np.arange(start, end)
        segment_values = prediction_marks[start:end]
        
        # Only add label once per iteration
        label = f'Iteration {iteration}' if iteration not in iteration_plotted else None
        if iteration not in iteration_plotted:
            iteration_plotted.add(iteration)
        
        ax2.plot(segment_indices, segment_values, 
                color=color, linewidth=2.5, alpha=0.8,
                label=label, zorder=2)
        
        ax2.axvspan(start, end, facecolor=color, alpha=0.1, zorder=0)
    
    ax2.set_title('Trend Segments with Local Linear Fits', fontsize=16, pad=15)
    ax2.set_ylabel('Value', fontsize=14)
    ax2.legend(loc='upper left', fontsize=10, ncol=min(4, num_iterations + 1),
               framealpha=0.9)
    ax2.grid(True, alpha=0.3)
    
    # Panel 3: Residuals
    ax3 = axes[2]
    
    residuals = np.full(len(sequence), np.nan)
    valid_mask = ~np.isnan(prediction_marks)
    residuals[valid_mask] = sequence[valid_mask] - prediction_marks[valid_mask]
    
    # Plot residuals without individual iteration labels
    for iteration in range(1, num_iterations + 1):
        mask = trend_marks == iteration
        indices = np.where(mask)[0]
        iter_residuals = residuals[mask]
        
        if len(indices) > 0:
            ax3.scatter(indices, iter_residuals, 
                       color=colors[iteration-1], 
                       s=30, alpha=0.6,
                       zorder=2)
    
    ax3.axhline(y=0, color='red', linestyle='--', linewidth=1.5, 
               alpha=0.7, label='Zero Line')
    
    ax3.set_title('Residuals (Original - Predicted)', fontsize=16, pad=15)
    ax3.set_xlabel('Time Index', fontsize=14)
    ax3.set_ylabel('Residual', fontsize=14)
    ax3.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    sns.despine()
    return fig