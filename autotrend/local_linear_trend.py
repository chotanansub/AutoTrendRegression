import numpy as np
from sklearn.linear_model import LinearRegression
from typing import List, Tuple
from .utility import extract_ranges


def decompose_llt(
    seq: np.ndarray,
    max_models: int = 10,
    window_size: int = 5,
    error_percentile: int = 40,
    percentile_step: int = 0,
    update_threshold: bool = False
) -> List[Tuple[List[float], List[float], List[Tuple[int, int]]]]:
    """
    Fit linear Regression on high-error segments identified via sliding windows.

    Args:
        seq: 1D input sequence.
        max_models: Maximum number of refinement rounds.
        window_size: Length of each training window.
        error_percentile: Initial percentile threshold for high errors.
        percentile_step: Step size to increase error threshold per round.

    Returns:
        List of (predictions, filtered_errors, focus_ranges) per iteration.
    """

    models, process_logs = [], []
    seq_len = len(seq)
    focus_targets = [i + window_size for i in range(seq_len - window_size)]

    trend_marks = np.full(seq_len, np.nan)

    for iteration in range(max_models):
        print(f'\n[Iteration {iteration + 1}/{max_models}]')

        #=============== (1) Determine Focus Windows Based on High-Error Ranges

        if not focus_targets:
            print('- No focused error regions found.')
            print('- All segments are sufficiently accurate. Stopping early.')
            break

        focus_ranges = extract_ranges(focus_targets)

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
        trend_marks[np.array(focus_targets)[low_error_mask]] = iteration + 1
        focus_targets = list(np.array(focus_targets)[~low_error_mask])
        high_error_flag = [int(e > threshold_value) for e in errors]

        print(f' - errors: {len(errors)} : {errors}')
        print(f' - error threshold (P{error_percentile}): {threshold_value:.4f}')

        models.append(model)
        process_logs.append((predictions, errors, focus_ranges, high_error_flag, threshold_value))


    print('\n[Done]')
    return (trend_marks, models, process_logs)