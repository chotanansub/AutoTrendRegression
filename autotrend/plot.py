import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from .utility import split_by_gap

def plot_error(sequence, sliding_lr_output, window_size):
    sns.set(style="whitegrid", context="talk", palette="muted")

    num_iterations = len(sliding_lr_output)
    fig, axes = plt.subplots(
        nrows=num_iterations * 2,  # Double the rows for main plot + error plot
        ncols=1,
        figsize=(14, 7 * num_iterations),  # Increased height multiplier from 6 to 7
        sharex=True,
        gridspec_kw={'height_ratios': [3, 1] * num_iterations}  # Main plot taller than error plot
    )
    if num_iterations == 1:
        axes = [axes] if len(axes.shape) == 1 else axes.flatten()
    else:
        axes = axes.flatten()

    # Move the title positioning and reduce font size slightly
    fig.suptitle("Sliding Linear Regression Error", fontsize=18, y=0.99)

    for iteration, package in enumerate(sliding_lr_output):
        predictions, absolute_errors, focused_ranges, high_error_flag, threshold_value = package
        prediction_indices = [idx for r in focused_ranges for idx in range(r[0], r[1])]

        high_errors = [err if flag == 1 else 0 for err, flag in zip(absolute_errors, high_error_flag)]
        low_errors = [err if flag == 0 else 0 for err, flag in zip(absolute_errors, high_error_flag)]

        if not prediction_indices:
            continue  # skip empty plot

        # Main plot (signal)
        ax_main = axes[iteration * 2]
        # Error plot
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

        # Highlight evaluation areas with color based on error type - subdivided
        for r in focused_ranges:
            range_indices = list(range(r[0], r[1]))

            # Get error flags for this range
            range_error_flags = []
            for idx in range_indices:
                if idx in prediction_indices:
                    pred_idx = prediction_indices.index(idx)
                    range_error_flags.append(high_error_flag[pred_idx])
                else:
                    range_error_flags.append(None)  # No prediction for this index

            # Group consecutive indices with same error type
            current_start = r[0]
            i = 0
            while i < len(range_error_flags):
                if range_error_flags[i] is not None:  # Only process indices with predictions
                    current_error_type = range_error_flags[i]
                    current_end = range_indices[i]

                    # Find consecutive indices with same error type
                    j = i + 1
                    while j < len(range_error_flags) and range_error_flags[j] == current_error_type:
                        current_end = range_indices[j]
                        j += 1

                    # Color based on error type
                    if current_error_type == 1:  # High error
                        facecolor = 'tomato'
                        alpha = 0.15
                    else:  # Low error
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
            bar_width = min(0.8, min_gap * 0.7)  # Adaptive width based on data density
        else:
            bar_width = 0.8

        # Error subplot - vertical bar plot
        # Create arrays for all indices with zero padding
        all_errors_high = np.zeros(len(sequence))
        all_errors_low = np.zeros(len(sequence))

        # Fill in the actual errors at prediction indices
        for i, idx in enumerate(prediction_indices):
            all_errors_high[idx] = high_errors[i]
            all_errors_low[idx] = low_errors[i]

        # Plot error bars with fill colors
        x_indices = np.arange(len(sequence))

        # High errors (red) - with fill
        high_mask = all_errors_high > 0
        ax_error.bar(x_indices[high_mask], all_errors_high[high_mask],
                    color='tomato', alpha=0.8, edgecolor='darkred', width=bar_width, label='High Error')

        # Low errors (green) - with fill
        low_mask = all_errors_low > 0
        ax_error.bar(x_indices[low_mask], all_errors_low[low_mask],
                    color='green', alpha=0.8, width=bar_width, edgecolor='darkgreen', label='Low Error')

        # Add horizontal threshold line to error plot
        ax_error.axhline(y=threshold_value, color='red', linestyle='--', 
                        linewidth=1, alpha=0.7, zorder=5, label='Threshold')

        # Highlight evaluation areas on error plot with same subdivision logic
        for r in focused_ranges:
            range_indices = list(range(r[0], r[1]))

            # Get error flags for this range
            range_error_flags = []
            for idx in range_indices:
                if idx in prediction_indices:
                    pred_idx = prediction_indices.index(idx)
                    range_error_flags.append(high_error_flag[pred_idx])
                else:
                    range_error_flags.append(None)  # No prediction for this index

            # Group consecutive indices with same error type
            current_start = r[0]
            i = 0
            while i < len(range_error_flags):
                if range_error_flags[i] is not None:  # Only process indices with predictions
                    current_error_type = range_error_flags[i]
                    current_end = range_indices[i]

                    # Find consecutive indices with same error type
                    j = i + 1
                    while j < len(range_error_flags) and range_error_flags[j] == current_error_type:
                        current_end = range_indices[j]
                        j += 1

                    # Color based on error type
                    if current_error_type == 1:  # High error
                        facecolor = 'tomato'
                        alpha = 0.15
                    else:  # Low error
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

        # Only show x-axis label on the last error subplot
        if iteration == num_iterations - 1:
            ax_error.set_xlabel("Time Index", fontsize=14)

    # Define single global legend
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
        ncol=4,  # Reduce columns from 7 to 4 for better spacing
        bbox_to_anchor=(0.5, 0.97),  # Position legend right below title
        fontsize=10
    )

    # Adjust the layout with minimal top margin
    plt.tight_layout(rect=[0, 0.02, 1, 0.94])  # Bring plots very close to legend
    plt.subplots_adjust(top=0.94)  # Additional adjustment to reduce top space
    sns.despine()
    plt.show()

def plot_slope_comparison(models, x_range=(-5, 5), figsize=(14, 10)):
    sns.set(style="whitegrid", context="talk", palette="muted")
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle("Slope Comparison Across Multiple Models", fontsize=18, y=1.03)
    plt.subplots_adjust(top=0.90, hspace=0.4, wspace=0.3)


    palette = sns.color_palette("muted", len(models))
    title_pad = 12
    fontsize_title = 14
    fontsize_axis = 12

    def add_arrow(ax, x_data, y_data, color):
        """Draw arrowhead on last segment of line."""
        ax.plot(x_data, y_data, color=color, linewidth=2)
        ax.annotate(
            '', xy=(x_data[-1], y_data[-1]), xytext=(x_data[-2], y_data[-2]),
            arrowprops=dict(arrowstyle="->", color=color, lw=2)
        )

    # Regression Lines (Zoomed)
    def plot_zoomed_lines(ax):
        x = np.linspace(x_range[0], x_range[1], 100)
        for i, (model, color) in enumerate(zip(models, palette)):
            slope = model.coef_[0]
            intercept = model.intercept_
            y = slope * x + intercept
            add_arrow(ax, x, y, color)
        ax.set_title("Regression Lines", fontsize=fontsize_title, pad=title_pad)
        ax.set_xlabel("X", fontsize=fontsize_axis)
        ax.set_ylabel("Y", fontsize=fontsize_axis)
        ax.tick_params(axis='both', labelsize=10)
        ax.legend([f'Model {i+1} (m={model.coef_[0]:.4f})' for i, model in enumerate(models)], fontsize=10, loc="best")
        ax.grid(True, alpha=0.3)

    # Bar Chart of Slopes
    def plot_slope_bars(ax):
        slopes = [model.coef_[0] for model in models]
        bars = ax.bar(range(len(models)), slopes, color=palette, alpha=0.8)
        ax.set_title("Slope Magnitudes", fontsize=fontsize_title, pad=title_pad)
        ax.set_xlabel("Model", fontsize=fontsize_axis)
        ax.set_ylabel("Slope Value", fontsize=fontsize_axis)
        ax.set_xticks(range(len(models)))
        ax.set_xticklabels([f'M{i+1}' for i in range(len(models))])
        ax.tick_params(axis='both', labelsize=10)
        for bar, slope in zip(bars, slopes):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{slope:.4f}',
                     ha='center', va='bottom', fontsize=10)
        ax.grid(True, alpha=0.3)

    # Extended Range Plot
    def plot_extended_lines(ax):
        x_ext = np.linspace(0, 100, 100)
        for i, (model, color) in enumerate(zip(models, palette)):
            slope = model.coef_[0]
            y_ext = slope * x_ext
            add_arrow(ax, x_ext, y_ext, color)
        ax.set_title("Extended Range (Amplifies Differences)", fontsize=fontsize_title, pad=title_pad)
        ax.set_xlabel("X (Extended Range)", fontsize=fontsize_axis)
        ax.set_ylabel("Y Change", fontsize=fontsize_axis)
        ax.tick_params(axis='both', labelsize=10)
        ax.legend([f'Model {i+1} (m={model.coef_[0]:.4f})' for i, model in enumerate(models)], fontsize=10, loc="upper left")
        ax.grid(True, alpha=0.3)

    # Fixed Half-Circle Angle Visualization - Right Half (Quadrants 1 & 4)
    def plot_half_circle(ax):
        ax.set_title("Slope Angles (Linear Trend)", fontsize=fontsize_title, pad=12)
        ax.set_xlim(-0.1, 1.8)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
        
        arc = np.linspace(-np.pi/2, np.pi/2, 300)
        ax.plot(np.cos(arc), np.sin(arc), color='lightgray', lw=2)
        
        degree_marks = [-90, -60, -45, -30, -15, 0, 15, 30, 45, 60, 90]
        for deg in degree_marks:
            rad = np.radians(deg)
            x = np.cos(rad)
            y = np.sin(rad)
            ax.plot([0, x], [0, y], ls='--', color='lightgray', lw=0.5, alpha=0.7)
            if deg in [-90, -45, 0, 45, 90]:
                ax.text(x * 1.15, y * 1.15, f"{deg}°", ha='center', va='center', 
                        fontsize=9, color='gray', weight='bold')
        
        legend_info = []
        for i, (model, color) in enumerate(zip(models, palette)):
            slope = model.coef_[0]
            angle = np.arctan(slope)
            x = np.cos(angle)
            y = np.sin(angle)
            ax.arrow(0, 0, x * 0.85, y * 0.85, 
                     head_width=0.04, head_length=0.05, 
                     fc=color, ec=color, linewidth=1.5, alpha=0.8)
            angle_deg = np.degrees(angle)
            legend_info.append((f'Model {i+1}', angle_deg, color))
        
        ax.plot(0, 0, 'ko', markersize=4)
        legend_x = 1.5
        legend_y_start = 0.8
        legend_y_spacing = 0.2

        ax.text(legend_x, legend_y_start + 0.15, 'Models:', ha='left', va='center', 
               fontsize=11, weight='bold', color='black')
        for i, (model_name, angle_deg, color) in enumerate(legend_info):
            y_pos = legend_y_start - i * legend_y_spacing
            ax.arrow(legend_x, y_pos, 0.08, 0, head_width=0.02, head_length=0.02, 
                     fc=color, ec=color, linewidth=2)
            ax.text(legend_x + 0.12, y_pos, f'{model_name}: {angle_deg:.1f}°', 
                    ha='left', va='center', fontsize=10, color=color, weight='bold')
        
        ax.text(0.6, -1.15, 'Linear Trend Angle', ha='center', va='top', 
               fontsize=10, style='italic', color='darkgray')
        ax.grid(True, alpha=0.3)
  

    plot_zoomed_lines(axes[0, 0])
    plot_slope_bars(axes[0, 1])
    plot_extended_lines(axes[1, 0])
    plot_half_circle(axes[1, 1])

    plt.show()




