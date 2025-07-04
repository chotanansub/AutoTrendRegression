import numpy as np
from sklearn.linear_model import LinearRegression
from typing import List, Tuple


def extract_ranges(indices: List[int]) -> List[Tuple[int, int]]:
    """
    Convert a list of sorted indices into a list of continuous index ranges.
    Example: [1, 2, 3, 7, 8] -> [(1, 4), (7, 9)]
    """
    if len(indices) == 0:
        return []

    ranges = []
    start = prev = indices[0]

    for idx in indices[1:]:
        if idx == prev + 1:
            prev = idx
        else:
            ranges.append((start, prev + 1))
            start = prev = idx

    ranges.append((start, prev + 1))
    return [(int(s), int(e)) for s, e in ranges]


def train_sliding_lr_ensemble(
    seq: np.ndarray,
    max_models: int = 2,
    window_size: int = 5,
    error_percentile: int = 40,
    percentile_step: int = 5,
) -> List[Tuple[List[float], List[float], List[Tuple[int, int]]]]:
    """
    Trains an ensemble of linear models on high-error segments identified via sliding windows.

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
    seq_len = len(seq) - 1
    all_errors = np.where(np.zeros(seq_len) == 0, np.inf, np.zeros(seq_len))
    focus_windows = [(i, i + window_size) for i in range(seq_len - window_size)]


    for iteration in range(max_models):
        print(f'\n[Iteration {iteration + 1}/{max_models}]')

        #=============== (1) Determine Focus Windows Based on High-Error Ranges

        if iteration > 0:
            error_percentile = min(90, error_percentile + percentile_step)
            high_error_ranges = extract_ranges(high_error_indices)

            focus_windows = [
                (i, i + window_size)
                for start, end in high_error_ranges
                if end - start > window_size*4
                for i in range(start + window_size, end - 2 * window_size)
            ]

            if not focus_windows:
                print('- No focused error regions found.')
                print('- All segments are sufficiently accurate. Stopping early.')
                break

        focus_targets = [end for _, end in focus_windows]
        focus_ranges = extract_ranges(focus_targets)
        print(f' - Focused error ranges: {focus_ranges}')

        #=============== (2) Train Linear Model on First Focus Window

        train_start = focus_windows[0][0]
        X_train = np.arange(window_size).reshape(-1, 1)
        y_train = seq[train_start:train_start + window_size]

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

        threshold_value = np.percentile(errors, error_percentile)
        high_error_indices = [t for t, e in zip(focus_targets, errors) if e > threshold_value]

        print(f' - Error threshold (P{error_percentile}): {threshold_value:.4f}')

        filtered_errors = [err if err > threshold_value else 0 for err in errors]

        models.append(model)
        process_logs.append( (predictions, filtered_errors, focus_ranges) )


    print('\n[Done] Ensemble training complete.')
    return (models, process_logs)