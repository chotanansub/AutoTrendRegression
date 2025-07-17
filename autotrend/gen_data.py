import numpy as np
from scipy.signal import find_peaks
from scipy.interpolate import interp1d

def generate_simeple_wave(add_noise=False, noise_strength=2, seed=6969):
    np.random.seed(seed)

    a = np.linspace(0, 50, 500)
    base_wave = np.sin(a)

    # Find peaks and create amplitude envelope
    peaks, _ = find_peaks(base_wave)
    peak_amplitudes = np.random.uniform(1, 5, size=len(peaks))
    interpolator = interp1d(peaks, peak_amplitudes, kind='linear', fill_value="extrapolate")
    amp_envelope = interpolator(np.arange(len(a)))

    # Base sequence with linear trend
    linear_trend = np.linspace(0, 5, len(a))
    sequence = amp_envelope * base_wave + linear_trend

    if add_noise:
        sequence += np.random.rand(len(a)) * noise_strength
        sequence += 2  # Offset for noisy version

    return sequence


def generate_behavioral_sequence(behaviors, total_length, min_seg_len, max_seg_len):
    def generate_segment(start_value, length, behavior):
        x = np.arange(length)
        if behavior == 'increase':
            return start_value + 0.5 * x
        elif behavior == 'decrease':
            return start_value - 0.8 * x
        elif behavior == 'steady':
            return np.full(length, start_value)

    segment_lengths = np.random.randint(min_seg_len, max_seg_len + 1, size=len(behaviors))
    scale_factor = total_length / np.sum(segment_lengths)
    segment_lengths = np.round(segment_lengths * scale_factor).astype(int)

    sequence = []
    current_value = 0

    for behavior, length in zip(behaviors, segment_lengths):
        segment = generate_segment(current_value, length, behavior)
        sequence.extend(segment)
        current_value = segment[-1]

    if len(sequence) < total_length:
        sequence.extend([current_value] * (total_length - len(sequence)))

    return np.array(sequence[:total_length])
