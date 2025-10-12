import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from ..core.utility import split_by_gap


def plot_error(sequence, sliding_lr_output, window_size):
    """
    Plot sliding linear regression with error analysis.
    
    Shows the iterative process of LLT with:
    - Training window and predictions
    - Error bars colored by threshold
    - Evaluation regions highlighted
    
    Args:
        sequence: Original time series
        sliding_lr_output: Process logs from decompose_llt
        window_size: Size of reference window
        
    Returns:
        matplotlib Figure object
    """
    sns.set(style="whitegrid", context="talk", palette="muted")

    num_iterations = len(sliding_lr_output)
    fig, axes = plt.subplots(
        nrows=num_iterations * 2,
        ncols=1,
        figsize=(14, 7 * num_iterations),
        sharex=True,
        gridspec_kw={'height_ratios': [3, 1] * num_iterations}
    )
    if num_iterations == 1:
        axes = [axes] if len(axes.shape) == 1 else axes.flatten()
    else:
        axes = axes.flatten()

    fig.suptitle("Sliding Linear Regression Error", fontsize=18, y=0.99)

    for iteration, package in enumerate(sliding_lr_output):
        predictions, absolute_errors, focused_ranges, high_error_flag, threshold_value = package
        prediction_indices = [idx for r in focused_ranges for idx in range(r[0], r[1])]

        high_errors = [err if flag == 1 else 0 for err, flag in zip(absolute_errors, high_error_flag)]
        low_errors = [err if flag == 0 else 0 for err, flag in zip(absolute_errors, high_error_flag)]

        if not prediction_indices:
            continue

        ax_main = axes[iteration * 2]
        ax_error = axes[iteration * 2 + 1]

        end_window = prediction_indices[0]
        start_window = max(0, end_window - window_size)

        # Plot training window
        sns.lineplot(
            x=np.arange(start_window, end_window),
            y=sequence[start_window:end_window],
            ax=ax_main,
            color='royalblue',
            linewidth=2.5,
            zorder=3
        )

        # Highlight training window
        ax_main.axvspan(
            xmin=start_window,
            xmax=end_window,
            ymin=0,
            ymax=1,
            facecolor='cyan',
            alpha=0.2,
            zorder=0
        )

        # Plot full sequence
        sns.lineplot(
            x=np.arange(len(sequence)),
            y=sequence,
            ax=ax_main,
            color='black',
            linewidth=1.5,
            alpha=1,
            zorder=2
        )

        # Plot predictions
        prediction_segments = split_by_gap(prediction_indices, predictions)
        for xs, ys in prediction_segments:
            sns.lineplot(
                x=xs,
                y=ys,
                ax=ax_main,
                color='purple',
                linestyle='--',
                linewidth=1.5,
                alpha=0.7,
                zorder=2
            )

        # Highlight evaluation areas
        for r in focused_ranges:
            range_indices = list(range(r[0], r[1]))
            range_error_flags = []
            for idx in range_indices:
                if idx in prediction_indices:
                    pred_idx = prediction_indices.index(idx)
                    range_error_flags.append(high_error_flag[pred_idx])
                else:
                    range_error_flags.append(None)

            current_start = r[0]
            i = 0
            while i < len(range_error_flags):
                if range_error_flags[i] is not None:
                    current_error_type = range_error_flags[i]
                    current_end = range_indices[i]

                    j = i + 1
                    while j < len(range_error_flags) and range_error_flags[j] == current_error_type:
                        current_end = range_indices[j]
                        j += 1

                    if current_error_type == 1:
                        facecolor = 'tomato'
                        alpha = 0.15
                    else:
                        facecolor = 'lightgreen'
                        alpha = 0.15

                    ax_main.axvspan(
                        xmin=range_indices[i],
                        xmax=current_end + 1,
                        ymin=0,
                        ymax=1,
                        facecolor=facecolor,
                        alpha=alpha,
                        zorder=-1
                    )

                    i = j
                else:
                    i += 1

        ax_main.set_title(f"Iteration: {iteration+1}", fontsize=16)
        ax_main.set_ylabel("Value", fontsize=14)
        ax_main.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)

        if len(prediction_indices) > 1:
            min_gap = min(prediction_indices[i+1] - prediction_indices[i] for i in range(len(prediction_indices)-1))
            bar_width = min(0.8, min_gap * 0.7)
        else:
            bar_width = 0.8

        # Error subplot
        all_errors_high = np.zeros(len(sequence))
        all_errors_low = np.zeros(len(sequence))

        for i, idx in enumerate(prediction_indices):
            all_errors_high[idx] = high_errors[i]
            all_errors_low[idx] = low_errors[i]

        x_indices = np.arange(len(sequence))

        high_mask = all_errors_high > 0
        ax_error.bar(x_indices[high_mask], all_errors_high[high_mask],
                    color='tomato', alpha=0.8, edgecolor='darkred', width=bar_width, label='High Error')

        low_mask = all_errors_low > 0
        ax_error.bar(x_indices[low_mask], all_errors_low[low_mask],
                    color='green', alpha=0.8, width=bar_width, edgecolor='darkgreen', label='Low Error')

        ax_error.axhline(y=threshold_value, color='red', linestyle='--', 
                        linewidth=1, alpha=0.7, zorder=5, label='Threshold')

        # Highlight evaluation areas on error plot
        for r in focused_ranges:
            range_indices = list(range(r[0], r[1]))
            range_error_flags = []
            for idx in range_indices:
                if idx in prediction_indices:
                    pred_idx = prediction_indices.index(idx)
                    range_error_flags.append(high_error_flag[pred_idx])
                else:
                    range_error_flags.append(None)

            i = 0
            while i < len(range_error_flags):
                if range_error_flags[i] is not None:
                    current_error_type = range_error_flags[i]
                    current_end = range_indices[i]

                    j = i + 1
                    while j < len(range_error_flags) and range_error_flags[j] == current_error_type:
                        current_end = range_indices[j]
                        j += 1

                    if current_error_type == 1:
                        facecolor = 'tomato'
                        alpha = 0.15
                    else:
                        facecolor = 'lightgreen'
                        alpha = 0.15

                    ax_error.axvspan(
                        xmin=range_indices[i],
                        xmax=current_end + 1,
                        ymin=0,
                        ymax=1,
                        facecolor=facecolor,
                        alpha=alpha,
                        zorder=-1
                    )

                    i = j
                else:
                    i += 1

        ax_error.set_ylabel("Error", fontsize=12)
        ax_error.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)

        if iteration == num_iterations - 1:
            ax_error.set_xlabel("Time Index", fontsize=14)

    # Global legend
    legend_elements = [
        mlines.Line2D([], [], color='royalblue', linewidth=2.5, label='Reference Window'),
        mlines.Line2D([], [], color='purple', linewidth=2,linestyle='--', label='Reference Trend'),
        mlines.Line2D([], [], color='black', linewidth=2, label='Observed Time Series'),
        mpatches.Patch(color='lightgreen', alpha=0.15, label='Below Error Threshold Area'),
        mpatches.Patch(color='tomato', alpha=0.15, label='Above Error Threshold Area'),
        mpatches.Patch(color='tomato', alpha=0.8, label='Above Error Threshold Bars'),
        mpatches.Patch(color='green', alpha=0.8, label='Below Error Threshold Bars'),
        mlines.Line2D([], [], color='red', linewidth=2, linestyle='--', label='Threshold'),
    ]
    fig.legend(
        handles=legend_elements,
        loc='upper center',
        ncol=4,
        bbox_to_anchor=(0.5, 0.97),
        fontsize=10
    )

    plt.tight_layout(rect=[0, 0.02, 1, 0.94])
    plt.subplots_adjust(top=0.94)
    sns.despine()
    
    # Don't call plt.show() - let the caller decide
    return fig