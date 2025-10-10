import numpy as np
from scipy.signal import find_peaks
from scipy.interpolate import interp1d


def generate_nonstationary_wave(add_noise=False, noise_strength=2, seed=6969):
    """
    Generate a non-stationary sinusoidal wave with variable amplitude envelope and linear trend.
    
    Args:
        add_noise: Whether to add random noise.
        noise_strength: Magnitude of noise to add.
        seed: Random seed for reproducibility.
        
    Returns:
        np.ndarray: Non-stationary wave sequence of length 500.
    """
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