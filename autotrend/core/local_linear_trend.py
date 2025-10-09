import numpy as np
from sklearn.linear_model import LinearRegression
from typing import List, Tuple
from dataclasses import dataclass
from .utility import extract_ranges


@dataclass
class LLTResult:
    """
    Results from Local Linear Trend (LLT) decomposition.
    
    Attributes:
        trend_marks: Array indicating which iteration labeled each point.
                     Values represent the iteration number (1, 2, 3, ...) or NaN if unlabeled.
        prediction_marks: Array of predicted values for each point.
                         NaN for points without predictions.
        models: List of LinearRegression models from each iteration.
        process_logs: Detailed logs from each iteration for visualization.
                     Each log is a tuple of (predictions, errors, focus_ranges, high_error_flag, threshold_value).
    """
    trend_marks: np.ndarray
    prediction_marks: np.ndarray
    models: List[LinearRegression]
    process_logs: List[Tuple]
    
    def get_num_iterations(self) -> int:
        """Get the number of iterations performed."""
        return len(self.models)
    
    def get_trend_segments(self) -> List[Tuple[int, int, int]]:
        """
        Extract contiguous trend segments.
        
        Returns:
            List of tuples (start_idx, end_idx, iteration_number)
        """
        segments = []
        current_trend = None
        start_idx = None
        
        for i, trend in enumerate(self.trend_marks):
            if not np.isnan(trend):
                if trend != current_trend:
                    if current_trend is not None:
                        segments.append((start_idx, i, int(current_trend)))
                    current_trend = trend
                    start_idx = i
            else:
                if current_trend is not None:
                    segments.append((start_idx, i, int(current_trend)))
                    current_trend = None
                    start_idx = None
        
        if current_trend is not None:
            segments.append((start_idx, len(self.trend_marks), int(current_trend)))
        
        return segments
    
    def get_predictions_by_iteration(self, iteration: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get indices and predictions for a specific iteration.
        
        Args:
            iteration: Iteration number (1-indexed)
            
        Returns:
            Tuple of (indices, predictions) for points labeled in that iteration
        """
        mask = self.trend_marks == iteration
        indices = np.where(mask)[0]
        predictions = self.prediction_marks[mask]
        return indices, predictions


def decompose_llt(
    seq: np.ndarray,
    max_models: int = 10,
    window_size: int = 5,
    error_percentile: int = 40,
    percentile_step: int = 0,
    update_threshold: bool = False,
    is_quiet: bool = False
) -> LLTResult:
    """
    Fit linear regression on high-error segments identified via sliding windows.

    Args:
        seq: 1D input sequence.
        max_models: Maximum number of refinement rounds.
        window_size: Length of each training window.
        error_percentile: Initial percentile threshold for high errors.
        percentile_step: Step size to increase error threshold per round.
        update_threshold: Whether to update threshold each iteration.
        is_quiet: Whether to suppress printed output.

    Returns:
        LLTResult: Dataclass containing trend_marks, prediction_marks, models, and process_logs.
        
    Example:
        >>> result = decompose_llt(seq, max_models=5, window_size=10)
        >>> print(f"Completed {result.get_num_iterations()} iterations")
        >>> plot_error(sequence, result.process_logs, window_size)
        
        # Access individual components
        >>> trends = result.trend_marks
        >>> predictions = result.prediction_marks
        >>> models = result.models
        
        # Or unpack if needed (backward compatible)
        >>> trend_marks, prediction_marks, models, logs = result
    """

    models, process_logs = [], []
    seq_len = len(seq)
    focus_targets = [i + window_size for i in range(seq_len - window_size)]
    
    trend_marks = np.concatenate([np.ones(window_size), np.full(seq_len - window_size, np.nan)])
    prediction_marks = np.full(seq_len, np.nan)

    for iteration in range(max_models):
        if not is_quiet:
            print(f'\n[Iteration {iteration + 1}/{max_models}]')

        #=============== (1) Determine Focus Windows Based on High-Error Ranges

        if not focus_targets:
            if not is_quiet:
                print('- No focused error regions found.')
                print('- All segments are sufficiently accurate. Stopping early.')
            break

        focus_ranges = extract_ranges(focus_targets)

        if not is_quiet:
            print(f' - focus_targets: {len(focus_targets)} : {focus_targets}')
            print(f' - focus_ranges (plot): {focus_ranges}')

        #=============== (2) Train Linear Model on First Focus Window

        train_end = focus_ranges[0][0]
        train_start = train_end - window_size

        X_train = np.arange(window_size).reshape(-1, 1)
        y_train = seq[train_start:train_end]

        model = LinearRegression()
        model.fit(X_train, y_train)

        #=============== (3) Apply Inference and Compute Errors in Focus Regions

        y0 = seq[train_start]
        yhat_m = model.predict([[window_size]])[0]
        basis_trend = yhat_m - y0

        predictions = []
        errors = []

        for t in focus_targets:
            yt_minus_m = seq[t - window_size]
            yt = seq[t]
            yt_hat = yt_minus_m + basis_trend
            error = abs(yt_hat - yt)

            predictions.append(yt_hat)
            errors.append(error)

        #=============== (4) Identify High-Error Indices for Next Iteration

        if iteration == 0 or update_threshold:
            error_percentile += percentile_step * update_threshold
            threshold_value = np.percentile(errors, error_percentile)

        low_error_mask = np.array(errors) <= threshold_value

        # Update trend_marks for points with low error (assign iteration round)
        trend_marks[np.array(focus_targets)[low_error_mask]] = iteration + 1

        # Update prediction_marks for points with low error (store prediction values)
        low_error_targets = np.array(focus_targets)[low_error_mask]
        low_error_predictions = np.array(predictions)[low_error_mask]
        prediction_marks[low_error_targets] = low_error_predictions

        focus_targets = list(np.array(focus_targets)[~low_error_mask])
        high_error_flag = [int(e > threshold_value) for e in errors]

        if not is_quiet:
            print(f' - errors: {len(errors)} : {errors}')
            print(f' - error threshold (P{error_percentile}): {threshold_value:.4f}')

        models.append(model)
        process_logs.append((predictions, errors, focus_ranges, high_error_flag, threshold_value))

        # Store predictions for initial training window in first iteration
        if iteration == 0:
            for i in range(window_size):
                prediction_marks[i] = model.predict([[i]])[0]

    if not is_quiet:
        print('\n[Done]')
    
    return LLTResult(
        trend_marks=trend_marks,
        prediction_marks=prediction_marks,
        models=models,
        process_logs=process_logs
    )