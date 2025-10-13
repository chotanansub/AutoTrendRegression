"""
Error Threshold Evolution Animation - Shows how errors decrease across iterations.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
from ..core.utility import split_by_gap


def animate_error_threshold(result, sequence=None, window_size=None, fps=2, 
                            duration_per_iter=1.0, figsize=(14, 10), 
                            output_path='error_threshold.gif', dpi=100,
                            sliding_mode=False, slides_per_iter=10):
    """
    Create an animation showing error threshold evolution across iterations.
    
    Args:
        result: LLTResult object from decompose_llt
        sequence: Original time series (optional if stored in result)
        window_size: Window size used in decomposition (optional if stored in result)
        fps: Frames per second for the animation
        duration_per_iter: Duration in seconds to display each iteration
        figsize: Figure size tuple
        output_path: Output file path (.gif or .mp4)
        dpi: Resolution for output file
        sliding_mode: If True, animate sliding frame revealing predictions progressively
        slides_per_iter: Number of sliding steps per iteration (only used if sliding_mode=True)
        
    Returns:
        matplotlib.animation.FuncAnimation object
    """
    seq = sequence if sequence is not None else result._sequence
    ws = window_size if window_size is not None else result._window_size
    
    if seq is None:
        raise ValueError("Sequence must be provided or stored in result")
    if ws is None:
        raise ValueError("Window size must be provided or stored in result")
    
    sns.set(style="whitegrid", context="talk", palette="muted")
    
    num_iterations = result.get_num_iterations()
    colors = sns.color_palette("husl", num_iterations)
    
    if sliding_mode:
        # Calculate frames for sliding mode
        frames_per_iter = slides_per_iter
        init_frames = 1  # Short initialization
        total_frames = init_frames + num_iterations * frames_per_iter
    else:
        # Normal mode
        frames_per_iter = int(fps * duration_per_iter)
        init_frames = max(3, frames_per_iter // 2)  # Shorter initialization
        total_frames = init_frames + num_iterations * frames_per_iter
    
    fig, (ax_main, ax_error) = plt.subplots(2, 1, figsize=figsize,
                                            gridspec_kw={'height_ratios': [2, 1]})
    
    # Main plot: time series with predictions
    line_full, = ax_main.plot(seq, color='black', linewidth=1.5, alpha=1, 
                              label='Observed Time Series', zorder=2)
    
    # Training window line (will be updated)
    line_window, = ax_main.plot([], [], color='royalblue', linewidth=2.5, 
                                label='Reference Window', zorder=3)
    
    # Sliding frame rectangle (only used in sliding mode)
    from matplotlib.patches import Rectangle
    sliding_frame = Rectangle((0, 0), 0, 0, linewidth=2, 
                             edgecolor='orange', facecolor='yellow',
                             alpha=0.2, zorder=1, visible=False)
    ax_main.add_patch(sliding_frame)
    
    pred_scatters = []
    for i in range(num_iterations):
        scatter = ax_main.scatter([], [], color=colors[i], s=50, alpha=0.7,
                                 label=f'Iter {i+1}', zorder=3,
                                 edgecolors='white', linewidth=0.5)
        pred_scatters.append(scatter)
    
    ax_main.set_ylabel('Value', fontsize=14)
    ax_main.legend(loc='upper right', fontsize=9, ncol=min(4, num_iterations + 2))
    ax_main.grid(True, alpha=0.3)
    ax_main.set_title('Predictions by Iteration', fontsize=16, pad=10)
    
    # Error plot: bars showing errors
    ax_error.set_xlabel('Time Index', fontsize=14)
    ax_error.set_ylabel('Error', fontsize=14)
    ax_error.grid(True, alpha=0.3)
    ax_error.set_title('Prediction Errors', fontsize=16, pad=10)
    
    # Text annotations
    iter_text = ax_main.text(0.02, 0.98, '', transform=ax_main.transAxes,
                            fontsize=12, ha='left', va='top',
                            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    stats_text = ax_error.text(0.98, 0.98, '', transform=ax_error.transAxes,
                              fontsize=11, ha='right', va='top',
                              bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    # Store fill objects and prediction lines to remove later
    main_fills = []
    pred_lines = []
    
    def init():
        line_window.set_data([], [])
        sliding_frame.set_visible(False)
        iter_text.set_text('')
        stats_text.set_text('')
        for scatter in pred_scatters:
            scatter.set_offsets(np.empty((0, 2)))
        return [line_window, sliding_frame] + pred_scatters + [iter_text, stats_text]
    
    def animate_sliding(frame):
        """Animation function for sliding mode"""
        nonlocal main_fills, pred_lines
        
        # Handle initialization frames
        if frame < init_frames:
            iter_text.set_text('Starting...')
            line_window.set_data([], [])
            sliding_frame.set_visible(False)
            
            for fill in main_fills:
                fill.remove()
            main_fills = []
            
            for line in pred_lines:
                line.remove()
            pred_lines = []
            
            ax_error.clear()
            ax_error.set_xlabel('Time Index', fontsize=14)
            ax_error.set_ylabel('Error', fontsize=14)
            ax_error.grid(True, alpha=0.3)
            ax_error.set_title('Prediction Errors', fontsize=16, pad=10)
            return [line_window, sliding_frame] + pred_scatters + [iter_text, stats_text]
        
        # Adjust frame for actual iterations
        adjusted_frame = frame - init_frames
        current_iter = (adjusted_frame // frames_per_iter) + 1
        slide_progress = (adjusted_frame % frames_per_iter) / frames_per_iter
        
        if current_iter > num_iterations:
            return [line_window, sliding_frame] + pred_scatters + [iter_text, stats_text]
        
        # Remove previous fills and prediction lines
        for fill in main_fills:
            fill.remove()
        main_fills = []
        
        for line in pred_lines:
            line.remove()
        pred_lines = []
        
        # Get error data for current iteration
        predictions, errors, focus_ranges, high_error_flag, threshold_value = \
            result.process_logs[current_iter - 1]
        
        prediction_indices = [idx for r in focus_ranges for idx in range(r[0], r[1])]
        
        if len(prediction_indices) == 0:
            return [line_window, sliding_frame] + pred_scatters + [iter_text, stats_text]
        
        # Update training window
        if len(focus_ranges) > 0:
            train_end = focus_ranges[0][0]
            train_start = max(0, train_end - ws)
            window_indices = np.arange(train_start, train_end)
            window_values = seq[train_start:train_end]
            line_window.set_data(window_indices, window_values)
            
            fill = ax_main.axvspan(train_start, train_end, facecolor='cyan', 
                                  alpha=0.2, zorder=0)
            main_fills.append(fill)
        
        # Calculate sliding frame position
        first_pred_idx = prediction_indices[0]
        last_pred_idx = prediction_indices[-1]
        
        slide_start = train_end
        slide_end = last_pred_idx + 1
        slide_width = ws
        
        current_slide_pos = slide_start + (slide_end - slide_start - slide_width) * slide_progress
        current_slide_pos = max(slide_start, min(current_slide_pos, slide_end - slide_width))
        
        # Update sliding frame
        y_min_data = np.min(seq)
        y_max_data = np.max(seq)
        y_range_data = y_max_data - y_min_data
        
        sliding_frame.set_x(current_slide_pos)
        sliding_frame.set_y(y_min_data - 0.1 * y_range_data)
        sliding_frame.set_width(slide_width)
        sliding_frame.set_height(y_range_data * 1.2)
        sliding_frame.set_visible(True)
        
        # Show predictions up to sliding frame position
        revealed_indices = []
        revealed_predictions = []
        for i, idx in enumerate(prediction_indices):
            if idx <= current_slide_pos + slide_width:
                revealed_indices.append(idx)
                revealed_predictions.append(predictions[i])
        
        # Update cumulative predictions from previous iterations
        for iteration in range(1, current_iter):
            mask = result.trend_marks == iteration
            indices = np.where(mask)[0]
            preds = result.prediction_marks[mask]
            
            if len(indices) > 0:
                points = np.column_stack([indices, preds])
                pred_scatters[iteration - 1].set_offsets(points)
        
        # Update current iteration predictions (only revealed ones)
        if len(revealed_indices) > 0:
            points = np.column_stack([revealed_indices, revealed_predictions])
            pred_scatters[current_iter - 1].set_offsets(points)
            
            # Plot prediction segments
            prediction_segments = split_by_gap(revealed_indices, revealed_predictions)
            for xs, ys in prediction_segments:
                line, = ax_main.plot(xs, ys, color='purple', linewidth=1.5,
                                    linestyle='--', alpha=0.7, zorder=2)
                pred_lines.append(line)
        
        # Add fill_between for revealed regions
        for r in focus_ranges:
            range_indices = list(range(r[0], min(r[1], int(current_slide_pos + slide_width) + 1)))
            i = 0
            while i < len(range_indices):
                idx = range_indices[i]
                if idx in prediction_indices:
                    pred_idx = prediction_indices.index(idx)
                    error_flag = high_error_flag[pred_idx]
                    
                    j = i
                    while j < len(range_indices) - 1:
                        next_idx = range_indices[j + 1]
                        if next_idx in prediction_indices:
                            next_pred_idx = prediction_indices.index(next_idx)
                            if high_error_flag[next_pred_idx] == error_flag:
                                j += 1
                            else:
                                break
                        else:
                            break
                    
                    start_seg = range_indices[i]
                    end_seg = range_indices[j]
                    
                    if error_flag == 1:
                        fill = ax_main.axvspan(start_seg, end_seg + 1, 
                                              facecolor='tomato', alpha=0.15, zorder=-1)
                    else:
                        fill = ax_main.axvspan(start_seg, end_seg + 1,
                                              facecolor='lightgreen', alpha=0.15, zorder=-1)
                    main_fills.append(fill)
                    
                    i = j + 1
                else:
                    i += 1
        
        # Update error plot
        all_errors_high = np.zeros(len(seq))
        all_errors_low = np.zeros(len(seq))
        
        for i, idx in enumerate(revealed_indices):
            pred_idx = prediction_indices.index(idx)
            if high_error_flag[pred_idx] == 1:
                all_errors_high[idx] = errors[pred_idx]
            else:
                all_errors_low[idx] = errors[pred_idx]
        
        ax_error.clear()
        
        x_indices = np.arange(len(seq))
        high_mask = all_errors_high > 0
        low_mask = all_errors_low > 0
        
        if len(prediction_indices) > 1:
            min_gap = min(prediction_indices[i+1] - prediction_indices[i] 
                        for i in range(len(prediction_indices)-1))
            bar_width = min(0.8, min_gap * 0.7)
        else:
            bar_width = 0.8
        
        ax_error.bar(x_indices[high_mask], all_errors_high[high_mask],
                    color='tomato', alpha=0.8, edgecolor='darkred',
                    width=bar_width, label='High Error')
        ax_error.bar(x_indices[low_mask], all_errors_low[low_mask],
                    color='green', alpha=0.8, edgecolor='darkgreen',
                    width=bar_width, label='Low Error')
        ax_error.axhline(y=threshold_value, color='red', linestyle='--',
                       linewidth=2, alpha=0.7, label='Threshold')
        
        ax_error.set_xlabel('Time Index', fontsize=14)
        ax_error.set_ylabel('Error', fontsize=14)
        ax_error.legend(loc='upper right', fontsize=10)
        ax_error.grid(True, alpha=0.3)
        ax_error.set_title('Prediction Errors', fontsize=16, pad=10)
        
        # Statistics
        num_high = np.sum(high_error_flag)
        num_low = len(high_error_flag) - num_high
        
        iter_text.set_text(f'Iteration: {current_iter}/{num_iterations} (Sliding...)')
        stats_text.set_text(
            f'Threshold: {threshold_value:.4f}\n'
            f'Revealed: {len(revealed_indices)}/{len(prediction_indices)}\n'
            f'Accepted: {num_low}\n'
            f'Remaining: {num_high}'
        )
        
        return [line_window, sliding_frame] + pred_scatters + [iter_text, stats_text]
    
    def animate_normal(frame):
        """Animation function for normal mode"""
        nonlocal main_fills, pred_lines
        
        # Handle initialization frames
        if frame < init_frames:
            iter_text.set_text('Starting...')
            line_window.set_data([], [])
            sliding_frame.set_visible(False)
            
            for fill in main_fills:
                fill.remove()
            main_fills = []
            
            for line in pred_lines:
                line.remove()
            pred_lines = []
            
            ax_error.clear()
            ax_error.set_xlabel('Time Index', fontsize=14)
            ax_error.set_ylabel('Error', fontsize=14)
            ax_error.grid(True, alpha=0.3)
            ax_error.set_title('Prediction Errors', fontsize=16, pad=10)
            return [line_window, sliding_frame] + pred_scatters + [iter_text, stats_text]
        
        # Adjust frame for actual iterations
        adjusted_frame = frame - init_frames
        current_iter = min((adjusted_frame // frames_per_iter) + 1, num_iterations)
        
        # Remove previous fills and prediction lines
        for fill in main_fills:
            fill.remove()
        main_fills = []
        
        for line in pred_lines:
            line.remove()
        pred_lines = []
        
        # Update predictions on main plot (cumulative)
        for iteration in range(1, current_iter + 1):
            mask = result.trend_marks == iteration
            indices = np.where(mask)[0]
            predictions = result.prediction_marks[mask]
            
            if len(indices) > 0:
                points = np.column_stack([indices, predictions])
                pred_scatters[iteration - 1].set_offsets(points)
        
        # Get error data for current iteration
        if current_iter <= len(result.process_logs):
            predictions, errors, focus_ranges, high_error_flag, threshold_value = \
                result.process_logs[current_iter - 1]
            
            prediction_indices = [idx for r in focus_ranges for idx in range(r[0], r[1])]
            
            # Update training window on main plot
            if len(focus_ranges) > 0:
                train_end = focus_ranges[0][0]
                train_start = max(0, train_end - ws)
                window_indices = np.arange(train_start, train_end)
                window_values = seq[train_start:train_end]
                line_window.set_data(window_indices, window_values)
                
                fill = ax_main.axvspan(train_start, train_end, facecolor='cyan', 
                                      alpha=0.2, zorder=0)
                main_fills.append(fill)
            
            # Plot prediction segments separately
            if len(prediction_indices) > 0:
                prediction_segments = split_by_gap(prediction_indices, predictions)
                for xs, ys in prediction_segments:
                    line, = ax_main.plot(xs, ys, color='purple', linewidth=1.5,
                                        linestyle='--', alpha=0.7, zorder=2)
                    pred_lines.append(line)
            
            # Add fill_between for low/high error regions on main plot
            for r in focus_ranges:
                range_indices = list(range(r[0], r[1]))
                i = 0
                while i < len(range_indices):
                    idx = range_indices[i]
                    if idx in prediction_indices:
                        pred_idx = prediction_indices.index(idx)
                        error_flag = high_error_flag[pred_idx]
                        
                        j = i
                        while j < len(range_indices) - 1:
                            next_idx = range_indices[j + 1]
                            if next_idx in prediction_indices:
                                next_pred_idx = prediction_indices.index(next_idx)
                                if high_error_flag[next_pred_idx] == error_flag:
                                    j += 1
                                else:
                                    break
                            else:
                                break
                        
                        start_seg = range_indices[i]
                        end_seg = range_indices[j]
                        
                        if error_flag == 1:
                            fill = ax_main.axvspan(start_seg, end_seg + 1, 
                                                  facecolor='tomato', alpha=0.15, zorder=-1)
                        else:
                            fill = ax_main.axvspan(start_seg, end_seg + 1,
                                                  facecolor='lightgreen', alpha=0.15, zorder=-1)
                        main_fills.append(fill)
                        
                        i = j + 1
                    else:
                        i += 1
            
            # Prepare error bars data
            all_errors_high = np.zeros(len(seq))
            all_errors_low = np.zeros(len(seq))
            
            for i, idx in enumerate(prediction_indices):
                if high_error_flag[i] == 1:
                    all_errors_high[idx] = errors[i]
                else:
                    all_errors_low[idx] = errors[i]
            
            # Clear and redraw error plot
            ax_error.clear()
            
            x_indices = np.arange(len(seq))
            high_mask = all_errors_high > 0
            low_mask = all_errors_low > 0
            
            if len(prediction_indices) > 1:
                min_gap = min(prediction_indices[i+1] - prediction_indices[i] 
                            for i in range(len(prediction_indices)-1))
                bar_width = min(0.8, min_gap * 0.7)
            else:
                bar_width = 0.8
            
            ax_error.bar(x_indices[high_mask], all_errors_high[high_mask],
                        color='tomato', alpha=0.8, edgecolor='darkred',
                        width=bar_width, label='High Error')
            ax_error.bar(x_indices[low_mask], all_errors_low[low_mask],
                        color='green', alpha=0.8, edgecolor='darkgreen',
                        width=bar_width, label='Low Error')
            ax_error.axhline(y=threshold_value, color='red', linestyle='--',
                           linewidth=2, alpha=0.7, label='Threshold')
            
            # Add fill_between for error regions on error plot
            for r in focus_ranges:
                range_indices = list(range(r[0], r[1]))
                i = 0
                while i < len(range_indices):
                    idx = range_indices[i]
                    if idx in prediction_indices:
                        pred_idx = prediction_indices.index(idx)
                        error_flag = high_error_flag[pred_idx]
                        
                        j = i
                        while j < len(range_indices) - 1:
                            next_idx = range_indices[j + 1]
                            if next_idx in prediction_indices:
                                next_pred_idx = prediction_indices.index(next_idx)
                                if high_error_flag[next_pred_idx] == error_flag:
                                    j += 1
                                else:
                                    break
                            else:
                                break
                        
                        start_seg = range_indices[i]
                        end_seg = range_indices[j]
                        
                        if error_flag == 1:
                            ax_error.axvspan(start_seg, end_seg + 1,
                                           facecolor='tomato', alpha=0.15, zorder=-1)
                        else:
                            ax_error.axvspan(start_seg, end_seg + 1,
                                           facecolor='lightgreen', alpha=0.15, zorder=-1)
                        
                        i = j + 1
                    else:
                        i += 1
            
            ax_error.set_xlabel('Time Index', fontsize=14)
            ax_error.set_ylabel('Error', fontsize=14)
            ax_error.legend(loc='upper right', fontsize=10)
            ax_error.grid(True, alpha=0.3)
            ax_error.set_title('Prediction Errors', fontsize=16, pad=10)
            
            # Statistics
            num_high = np.sum(high_error_flag)
            num_low = len(high_error_flag) - num_high
            mean_error = np.mean(errors)
            
            iter_text.set_text(f'Iteration: {current_iter}/{num_iterations}')
            stats_text.set_text(
                f'Threshold: {threshold_value:.4f}\n'
                f'Mean Error: {mean_error:.4f}\n'
                f'Accepted: {num_low}\n'
                f'Remaining: {num_high}'
            )
        
        return [line_window, sliding_frame] + pred_scatters + [iter_text, stats_text]
    
    # Choose animation function based on mode
    anim_func = animate_sliding if sliding_mode else animate_normal
    
    anim = animation.FuncAnimation(fig, anim_func, init_func=init,
                                  frames=total_frames, interval=1000/fps,
                                  blit=False, repeat=True)
    
    # Save animation
    if output_path.endswith('.gif'):
        anim.save(output_path, writer='pillow', fps=fps, dpi=dpi)
    elif output_path.endswith('.mp4'):
        anim.save(output_path, writer='ffmpeg', fps=fps, dpi=dpi)
    else:
        raise ValueError("Output path must end with .gif or .mp4")
    
    plt.close(fig)
    print(f"Animation saved to: {output_path}")
    
    return anim