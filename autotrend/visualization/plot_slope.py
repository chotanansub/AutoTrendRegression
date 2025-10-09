import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def plot_slope_comparison(models, x_range=(-5, 5), figsize=(14, 10)):
    """
    Compare slopes across multiple linear regression models.
    
    4-panel visualization showing:
    - Regression lines (zoomed)
    - Slope bar chart
    - Extended range comparison
    - Angle visualization (half-circle)
    
    Args:
        models: List of LinearRegression models
        x_range: Tuple of (min, max) for zoomed plot
        figsize: Figure size tuple
    """
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

    # Panel 1: Regression Lines (Zoomed)
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
        ax.legend([f'Model {i+1} (m={model.coef_[0]:.4f})' for i, model in enumerate(models)], 
                 fontsize=10, loc="best")
        ax.grid(True, alpha=0.3)

    # Panel 2: Bar Chart of Slopes
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

    # Panel 3: Extended Range Plot
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
        ax.legend([f'Model {i+1} (m={model.coef_[0]:.4f})' for i, model in enumerate(models)], 
                 fontsize=10, loc="upper left")
        ax.grid(True, alpha=0.3)

    # Panel 4: Half-Circle Angle Visualization
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