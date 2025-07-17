from typing import List, Tuple
from itertools import groupby

def extract_ranges(indices: List[int]) -> List[Tuple[int, int]]:
    """
    Convert a list of sorted indices into a list of continuous index ranges.

    Each range is represented as a tuple (start, end), where `start` is inclusive 
    and `end` is exclusive. For example, the input [1, 2, 3, 7, 8] will be 
    converted to [(1, 4), (7, 9)].

    Args:
        indices (List[int]): A sorted list of integer indices.

    Returns:
        List[Tuple[int, int]]: A list of (start, end) tuples representing contiguous ranges.
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


def split_by_gap(x: List[int], y: List[float]) -> List[Tuple[List[int], List[float]]]:
    """
    Split x and y values into continuous segments based on gaps in x.

    This function groups together pairs (x, y) where the x values are consecutive 
    (i.e., the difference between adjacent x values is 1). When a gap is detected, 
    a new segment is started.

    Args:
        x (List[int]): List of x-values (assumed sorted).
        y (List[float]): Corresponding list of y-values.

    Returns:
        List[Tuple[List[int], List[float]]]: List of segments, each a tuple of (x_segment, y_segment).
    """
    counter = iter(range(len(x)))
    segments = []
    for _, group in groupby(zip(x, y), key=lambda t: t[0] - next(counter)):
        g = list(group)
        xs, ys = zip(*g)
        segments.append((list(xs), list(ys)))
    return segments
