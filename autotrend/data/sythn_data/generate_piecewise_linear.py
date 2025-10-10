import numpy as np


def generate_piecewise_linear(trends, total_length, min_seg_len, max_seg_len, seed=None):
    """
    Generate a time series composed of multiple linear segments with different slopes.
    
    Args:
        trends: List of trend types for each segment. Options: 'increase', 'decrease', 'steady'
        total_length: Total length of the output sequence.
        min_seg_len: Minimum length for each segment.
        max_seg_len: Maximum length for each segment.
        seed: Random seed for reproducibility.
    
    Returns:
        np.ndarray: Piecewise linear time series.
    """
    if seed is not None:
        np.random.seed(seed)
    
    def generate_segment(start_value, length, trend):
        """Generate a single linear segment."""
        x = np.arange(length)
        if trend == 'increase':
            return start_value + 0.5 * x
        elif trend == 'decrease':
            return start_value - 0.8 * x
        elif trend == 'steady':
            return np.full(length, start_value)
        else:
            raise ValueError(f"Unknown trend type: {trend}. Use 'increase', 'decrease', or 'steady'")

    # Generate random segment lengths
    segment_lengths = np.random.randint(min_seg_len, max_seg_len + 1, size=len(trends))
    
    # Scale to match total_length
    scale_factor = total_length / np.sum(segment_lengths)
    segment_lengths = np.round(segment_lengths * scale_factor).astype(int)

    sequence = []
    current_value = 0

    for trend, length in zip(trends, segment_lengths):
        segment = generate_segment(current_value, length, trend)
        sequence.extend(segment)
        current_value = segment[-1]

    # Pad if needed
    if len(sequence) < total_length:
        sequence.extend([current_value] * (total_length - len(sequence)))

    return np.array(sequence[:total_length])