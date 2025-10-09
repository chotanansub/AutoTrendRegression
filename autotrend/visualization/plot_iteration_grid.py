import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


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