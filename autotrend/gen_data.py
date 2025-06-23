import numpy as np

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
