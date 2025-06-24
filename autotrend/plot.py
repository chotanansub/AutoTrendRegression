import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from itertools import groupby

def split_by_gap(x, y):
    counter = iter(range(len(x)))
    segments = []
    for _, group in groupby(zip(x, y), key=lambda t: t[0] - next(counter)):
        g = list(group)
        xs, ys = zip(*g)
        segments.append((list(xs), list(ys)))
    return segments

def new_plot_multiple_lr(models, n=100):
    sns.set(style="whitegrid", context="talk", palette="muted")

    X = np.arange(n).reshape(-1, 1)
    x_vals = np.arange(n)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_title("Multiple Linear Regression Model Predictions", fontsize=18)

    palette = sns.color_palette("muted", len(models))

    for i, (model, color) in enumerate(zip(models, palette)):
        y_pred = model.predict(X)

        # Plot the prediction line up to the 2nd last point
        ax.plot(x_vals[:-1], y_pred[:-1], label=f'Model {i+1}', linewidth=2.5, color=color, zorder=2)

        # Add arrow at the end
        ax.annotate(
            '', 
            xy=(x_vals[-1], y_pred[-1]), 
            xytext=(x_vals[-2], y_pred[-2]),
            arrowprops=dict(arrowstyle="->", color=color, lw=2),
            zorder=3
        )

    ax.set_xlabel("Time Step", fontsize=14)
    ax.set_ylabel("Prediction", fontsize=14)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)
    ax.legend(fontsize=12)
    sns.despine()
    plt.tight_layout()
    plt.show()


def plot_error(sequence, sliding_lr_output, window_size):
    sns.set(style="whitegrid", context="talk", palette="muted")

    num_iterations = len(sliding_lr_output)
    fig, axes = plt.subplots(
        nrows=num_iterations,
        ncols=1,
        figsize=(14, 5 * num_iterations),
        sharex=True
    )
    if num_iterations == 1:
        axes = [axes]

    fig.suptitle("Sliding Linear Regression Error", fontsize=22, y=0.99)

    for iteration, (package, ax) in enumerate(zip(sliding_lr_output, axes)):
        predictions, absolute_errors, focused_ranges = package
        prediction_indices = [idx for r in focused_ranges for idx in range(r[0], r[1])]

        if not prediction_indices:
            continue  # skip empty plot

        end_window = prediction_indices[0]
        start_window = max(0, end_window - window_size)

        sns.lineplot(
            x=np.arange(start_window, end_window),
            y=sequence[start_window:end_window],
            ax=ax,
            color='royalblue',
            linewidth=2.5,
            zorder=3
        )

        ax.axvspan(
            xmin=start_window,
            xmax=end_window,
            ymin=0,
            ymax=1,
            facecolor='cyan',
            alpha=0.2,
            zorder=0
        )

        sns.lineplot(
            x=np.arange(len(sequence)),
            y=sequence,
            ax=ax,
            color='green',
            linewidth=2,
            alpha=1,
            zorder=2
        )

        prediction_segments = split_by_gap(prediction_indices, predictions)
        for xs, ys in prediction_segments:
            sns.lineplot(
                x=xs,
                y=ys,
                ax=ax,
                color='yellow',
                linewidth=4,
                alpha=0.7,
                zorder=2
            )

        ax.errorbar(
            prediction_indices,
            [sequence[idx] for idx in prediction_indices],
            yerr=absolute_errors,
            ecolor='tomato',
            linestyle='None',
            alpha=0.6,
            zorder=1
        )

        for r in focused_ranges:
            ax.axvspan(
                xmin=r[0],
                xmax=r[1],
                ymin=0,
                ymax=1,
                facecolor='gray',
                alpha=0.2,
                zorder=-1
            )

        ax.set_title(f"Iteration: {iteration}", fontsize=16)
        ax.set_xlabel("Time Index", fontsize=14)
        ax.set_ylabel("Value", fontsize=14)
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.6)

    # Define single global legend
    legend_elements = [
        mlines.Line2D([], [], color='royalblue', linewidth=2.5, label='Initial Training Window'),
        mlines.Line2D([], [], color='yellow', linewidth=4, label='Predict'),
        mlines.Line2D([], [], color='green', linewidth=2, label='Observed Time Series'),
        mpatches.Patch(color='gray', alpha=0.2, label='Eval Area'),
        mlines.Line2D([], [], color='tomato', linewidth=2, linestyle='-', label='Prediction Error'),
    ]
    fig.legend(
        handles=legend_elements,
        loc='lower center',
        ncol=5,
        bbox_to_anchor=(0.5, -0.01),
        fontsize=12
    )

    plt.tight_layout(rect=[0, 0.04, 1, 0.96])
    sns.despine()
    plt.show()

