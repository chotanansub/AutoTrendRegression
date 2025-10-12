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
    verbose: int,
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
        verbose: Verbosity level (0=silent, 1=basic, 2=detailed).
        store_sequence: Whether to store sequence in result for plotting convenience.
        
    Returns:
        LLTResult object containing decomposition results.
    """
    models, process_logs = [], []
    seq_len = len(seq)
    focus_targets = [i + window_size for i in range(seq_len - window_size)]
    
    trend_marks = np.concatenate([np.ones(window_size), np.full(seq_len - window_size, np.nan)])
    prediction_marks = np.full(seq_len, np.nan)

    # Header for verbose output
    if verbose >= 1:
        print(f'\nAutoTrend LLT Decomposition')
        print(f'{"="*60}')
        print(f'Sequence length: {seq_len}')
        print(f'Configuration: window={window_size}, max_iter={max_models}, '
              f'threshold=P{error_percentile}')
        print()

    for iteration in range(max_models):
        if verbose >= 1:
            print(f'Iteration {iteration + 1}/{max_models}', end='')

        #=============== (1) Determine Focus Windows Based on High-Error Ranges

        if not focus_targets:
            if verbose >= 1:
                print(f'\n\n✓ Converged after {iteration} iterations')
                print(f'  Convergence reason: No remaining high-error points')
            break

        focus_ranges = extract_ranges(focus_targets)

        if verbose >= 2:
            print(f'\n  Focus targets: {len(focus_targets)} points')
            print(f'  Focus ranges: {focus_ranges}')

        #=============== (2) Train Linear Model on First Focus Window

        train_end = focus_ranges[0][0]
        train_start = train_end - window_size

        X_train = np.arange(window_size).reshape(-1, 1)
        y_train = seq[train_start:train_end]

        model = LinearRegression()
        model.fit(X_train, y_train)

        if verbose >= 2:
            print(f'  Training window: [{train_start}, {train_end})')
            print(f'  Model: slope={model.coef_[0]:.4f}, intercept={model.intercept_:.4f}')

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

        # Calculate statistics for output
        num_accepted = np.sum(low_error_mask)
        num_remaining = len(focus_targets)
        acceptance_rate = (num_accepted / len(low_error_mask) * 100) if len(low_error_mask) > 0 else 0

        if verbose >= 2:
            print(f'  Error stats: mean={np.mean(errors):.4f}, std={np.std(errors):.4f}, '
                  f'P{error_percentile}={threshold_value:.4f}')
            print(f'  Threshold: {threshold_value:.4f}')
            print(f'  Result: {num_accepted} accepted ({acceptance_rate:.1f}%), '
                  f'{num_remaining} remaining ({100-acceptance_rate:.1f}%)')
        elif verbose >= 1:
            print(f': {len(low_error_mask)} points evaluated → '
                  f'{num_accepted} accepted, {num_remaining} remaining')

        models.append(model)
        process_logs.append((predictions, errors, focus_ranges, high_error_flag, threshold_value))

        # Store predictions for initial training window in first iteration
        if iteration == 0:
            for i in range(window_size):
                prediction_marks[i] = model.predict([[i]])[0]

    # Final summary
    if verbose >= 1:
        if len(focus_targets) == 0:
            print(f'\n✓ Converged after {len(models)} iterations')
        else:
            print(f'\n✓ Stopped after {len(models)} iterations (max reached)')
        
        print(f'  Total points: {seq_len}')
        print(f'  Models trained: {len(models)}')
        coverage = np.sum(~np.isnan(prediction_marks)) / seq_len * 100
        print(f'  Coverage: {coverage:.1f}%')
        
        if verbose >= 2:
            print(f'  Iteration breakdown:')
            for i in range(1, len(models) + 1):
                count = np.sum(trend_marks == i)
                pct = count / seq_len * 100
                print(f'    Iter {i}: {count} pts ({pct:.1f}%)')
        print()
    
    return LLTResult(
        trend_marks=trend_marks,
        prediction_marks=prediction_marks,
        models=models,
        process_logs=process_logs,
        _sequence=seq.copy() if store_sequence else None,
        _window_size=window_size if store_sequence else None
    )