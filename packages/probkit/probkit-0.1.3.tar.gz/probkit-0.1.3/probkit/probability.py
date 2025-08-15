"""
Probability modification functions for probkit.
"""

__all__ = ["modified_probability"]

from .utils import effective_ratio

def modified_probability(k:float, a:float, b:float|None=None) -> float:
    """Modifies a base probability using a ratio.

    The ratio can be provided directly as `a`, or calculated as `a/b` when both parameters are given.

    0 <= k <= 1
    0 <= ratio <= INF

    At ratio=0, modprob=0
    At ratio=1, modprob=k
    At ratio=INF, modprob=1

    https://www.desmos.com/calculator/buzh0oqrxs

    Args:
        k (float): Base probability in [0,1].
        a (float): Ratio (if b is None) or numerator (if b is provided).
        b (float, optional): Denominator of the ratio.

    Returns:
        float: Modified probability in [0,1].
    """
    x = a if b is None else effective_ratio(a, b)

    if not 0 <= k <= 1:
        raise ValueError(f"Base probability 'k' must be in range [0,1], got {k}.")
    if x < 0:
        raise ValueError(f"Ratio may not be negative, got {x}.")

    if x == 0: return 0
    if x == 1: return k
    if x == float('inf'): return 1
    if k in (0, 1): return k

    kx = k * x
    return kx / (kx - k + 1)
