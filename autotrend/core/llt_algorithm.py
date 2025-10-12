"""
Core LLT algorithm implementation.
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from .llt_result import LLTResult
from .utility import extract_ranges


def decompose_llt_internal(
    seq: np.ndarray,
    max_models: int,
    window_size: int,
    error_percentile: int,
    percentile_step: int,
    update_threshold: bool,
    is_quiet: bool,
    store_sequence: bool
) -> LLTResult:
    """
    Internal implementation of LLT decomposition.
    
    This is the core algorithm called by both the functional and object-based APIs.
    
    Args:
        seq: 1D input sequence.
        max_models: Maximum number of refinement rounds.
        window_size: Length of each training window.
        error_percentile: Initial percentile threshold for high errors.
        percentile_step: Step size to increase error threshold per round.
        update_threshold: Whether to update threshold each iteration.
        is_quiet: Whether to suppress printed output.
        store_sequence: Whether to store sequence in result for plotting convenience.
        
    Returns:
        LLTResult object containing decomposition results.
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
        process_logs=process_logs,
        _sequence=seq.copy() if store_sequence else None,
        _window_size=window_size if store_sequence else None
    )