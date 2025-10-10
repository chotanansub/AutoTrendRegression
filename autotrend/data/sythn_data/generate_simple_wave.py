import numpy as np

def generate_simple_wave(
    length=500,
    frequency=1.0,
    amplitude=1.0,
    phase=0.0,
    add_noise=False,
    noise_strength=0.1,
    seed=6969
):
    """
    Generate a stationary sinusoidal wave with constant amplitude.
    
    Args:
        length: Number of points in the sequence.
        frequency: Frequency in cycles per length.
        amplitude: Peak amplitude of the wave.
        phase: Phase shift in radians.
        add_noise: Whether to add Gaussian noise.
        noise_strength: Standard deviation of noise.
        seed: Random seed for reproducibility.
        
    Returns:
        np.ndarray: Stationary sine wave sequence.
    """
    np.random.seed(seed)
    
    # Generate time points
    t = np.linspace(0, 2 * np.pi * frequency, length)
    
    # Generate sine wave
    sequence = amplitude * np.sin(t + phase)
    
    # Add noise if requested
    if add_noise:
        noise = np.random.normal(0, noise_strength, length)
        sequence += noise
    
    return sequence