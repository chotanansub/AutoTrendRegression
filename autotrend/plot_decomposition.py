import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
    ax1.legend(loc='best', fontsize=10, ncol=min(4, num_iterations))
    ax1.grid(True, alpha=0.3)
    
    # Panel 2: Trend Segments with Regression Lines
    ax2 = axes[1]
    
    ax2.plot(sequence, color='gray', linewidth=1.5, alpha=0.5, 
            label='Original Series', zorder=1)
    
    segments = result.get_trend_segments()
    for start, end, iteration in segments:
        color = colors[iteration-1]
        
        segment_indices = np.arange(start, end)
        segment_values = prediction_marks[start:end]
        
        ax2.plot(segment_indices, segment_values, 
                color=color, linewidth=2.5, alpha=0.8,
                label=f'Trend Segment {iteration}', zorder=2)
        
        ax2.axvspan(start, end, facecolor=color, alpha=0.1, zorder=0)
    
    ax2.set_title('Trend Segments with Local Linear Fits', fontsize=16, pad=15)
    ax2.set_ylabel('Value', fontsize=14)
    ax2.legend(loc='best', fontsize=10, ncol=min(4, num_iterations))
    ax2.grid(True, alpha=0.3)
    
    # Panel 3: Residuals
    ax3 = axes[2]
    
    residuals = np.full(len(sequence), np.nan)
    valid_mask = ~np.isnan(prediction_marks)
    residuals[valid_mask] = sequence[valid_mask] - prediction_marks[valid_mask]
    
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
    ax3.legend(loc='best', fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    sns.despine()
    return fig


def plot_iteration_grid(sequence, result, figsize=(16, 12)):
    """
    Plot each iteration's contribution separately in a grid layout.
    
    Shows individual subplots for each iteration with:
    - Original series
    - Predictions for that iteration
    - Trend line
    - Model parameters (slope, intercept)
    
    Args:
        sequence: Original time series
        result: LLTResult object from decompose_llt
        figsize: Figure size tuple
    """
    sns.set(style="whitegrid", context="talk", palette="muted")
    
    num_iterations = result.get_num_iterations()
    
    ncols = min(3, num_iterations)
    nrows = (num_iterations + ncols - 1) // ncols
    
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, squeeze=False)
    fig.suptitle('Iteration-by-Iteration Grid', fontsize=18, y=0.995)
    
    colors = sns.color_palette("husl", num_iterations)
    
    for iteration in range(1, num_iterations + 1):
        row = (iteration - 1) // ncols
        col = (iteration - 1) % ncols
        ax = axes[row, col]
        
        ax.plot(sequence, color='lightgray', linewidth=1.5, alpha=0.6, 
               label='Original', zorder=1)
        
        mask = result.trend_marks == iteration
        indices = np.where(mask)[0]
        predictions = result.prediction_marks[mask]
        
        if len(indices) > 0:
            ax.scatter(indices, predictions, 
                      color=colors[iteration-1], 
                      s=60, alpha=0.8, 
                      label=f'Predictions',
                      zorder=3, edgecolors='white', linewidth=0.5)
            
            ax.plot(indices, predictions, 
                   color=colors[iteration-1], 
                   linewidth=2, alpha=0.6, zorder=2)
            
            ax.axvspan(indices[0], indices[-1], 
                      facecolor=colors[iteration-1], alpha=0.1, zorder=0)
            
            model = result.models[iteration-1]
            slope = model.coef_[0]
            intercept = model.intercept_
            ax.text(0.05, 0.95, 
                   f'Slope: {slope:.4f}\nIntercept: {intercept:.2f}',
                   transform=ax.transAxes, 
                   fontsize=10, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_title(f'Iteration {iteration}', fontsize=14, pad=10)
        ax.set_xlabel('Time Index', fontsize=11)
        ax.set_ylabel('Value', fontsize=11)
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for iteration in range(num_iterations + 1, nrows * ncols + 1):
        row = (iteration - 1) // ncols
        col = (iteration - 1) % ncols
        axes[row, col].axis('off')
    
    plt.tight_layout()
    sns.despine()
    return fig


def plot_model_statistics(result, figsize=(14, 8)):
    """
    Plot summary statistics and model characteristics.
    
    4-panel layout:
    - Panel 1: Segment lengths bar chart
    - Panel 2: Model slopes bar chart
    - Panel 3: Points covered per iteration
    - Panel 4: Model parameters table
    
    Args:
        result: LLTResult object from decompose_llt
        figsize: Figure size tuple
    """
    sns.set(style="whitegrid", context="talk", palette="muted")
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Model Statistics Summary', fontsize=18, y=0.995)
    
    num_iterations = result.get_num_iterations()
    colors = sns.color_palette("husl", num_iterations)
    
    # Panel 1: Segment Lengths
    ax1 = axes[0, 0]
    segments = result.get_trend_segments()
    segment_lengths = [end - start for start, end, _ in segments]
    iterations = [iteration for _, _, iteration in segments]
    
    bars = ax1.bar(range(len(segment_lengths)), segment_lengths, 
                   color=[colors[it-1] for it in iterations], alpha=0.7)
    ax1.set_title('Trend Segment Lengths', fontsize=14, pad=10)
    ax1.set_xlabel('Segment Index', fontsize=12)
    ax1.set_ylabel('Length', fontsize=12)
    ax1.grid(True, alpha=0.3, axis='y')
    
    for i, (bar, length) in enumerate(zip(bars, segment_lengths)):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
                f'{length}', ha='center', va='bottom', fontsize=9)
    
    # Panel 2: Model Slopes
    ax2 = axes[0, 1]
    slopes = [model.coef_[0] for model in result.models]
    
    bars = ax2.bar(range(1, num_iterations + 1), slopes, 
                   color=colors, alpha=0.7)
    ax2.set_title('Model Slopes by Iteration', fontsize=14, pad=10)
    ax2.set_xlabel('Iteration', fontsize=12)
    ax2.set_ylabel('Slope', fontsize=12)
    ax2.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
    ax2.grid(True, alpha=0.3, axis='y')
    
    for bar, slope in zip(bars, slopes):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
                f'{slope:.4f}', ha='center', 
                va='bottom' if slope >= 0 else 'top', fontsize=9)
    
    # Panel 3: Coverage per Iteration
    ax3 = axes[1, 0]
    coverage = []
    for iteration in range(1, num_iterations + 1):
        count = np.sum(result.trend_marks == iteration)
        coverage.append(count)
    
    bars = ax3.bar(range(1, num_iterations + 1), coverage, 
                   color=colors, alpha=0.7)
    ax3.set_title('Points Covered by Each Iteration', fontsize=14, pad=10)
    ax3.set_xlabel('Iteration', fontsize=12)
    ax3.set_ylabel('Number of Points', fontsize=12)
    ax3.grid(True, alpha=0.3, axis='y')
    
    for bar, count in zip(bars, coverage):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height(), 
                f'{count}', ha='center', va='bottom', fontsize=9)
    
    # Panel 4: Model Parameters Table
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    table_data = [['Iteration', 'Slope', 'Intercept', 'Points']]
    for iteration in range(1, num_iterations + 1):
        model = result.models[iteration-1]
        slope = model.coef_[0]
        intercept = model.intercept_
        count = coverage[iteration-1]
        table_data.append([f'{iteration}', f'{slope:.4f}', 
                          f'{intercept:.2f}', f'{count}'])
    
    table = ax4.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.2, 0.3, 0.3, 0.2])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    for i in range(4):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    for i in range(1, len(table_data)):
        for j in range(4):
            table[(i, j)].set_facecolor(colors[i-1])
            table[(i, j)].set_alpha(0.3)
    
    ax4.set_title('Model Parameters', fontsize=14, pad=20)
    
    plt.tight_layout()
    sns.despine()
    return fig