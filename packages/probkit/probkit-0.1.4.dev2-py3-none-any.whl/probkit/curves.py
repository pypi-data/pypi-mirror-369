"""
Curve and sigmoid functions for probkit.
"""

__all__ = ["ntsig", "nthsig", "biased_curve"]

from .utils import transform_range

def ntsig(k:float, x:float) -> float:
    """Normalized Tunable Sigmoid

    Calculates a point along a sigmoid-like curve that goes through (0,0) and (0.5,0.5) and (1,1).

    Negative k is flat (logit/log-odds curve), bringing all values of y toward 0.5.
    Neutral k is linear between (0,0) and (1,1).
    Positive k is steep/swingy (sigmoid curve), bringing all values of y toward either 0 (for x<0.5) or 1 (for x>0.5).

    https://www.desmos.com/calculator/2hkedvscyv

    Args:
        k (float): Must be in range [-1,1]. The shape (steepness/swinginess) of the curve.
        x (float): Must be in range [0,1]. The function will return the corresponding y value at x.
    Returns:
        float: The y value at x.
    """
    if not -1 <= k <= 1:
        raise ValueError(f"Argument 'k' must be in range [-1,1], got {k}.")
    if not 0 <= x <= 1:
        raise ValueError(f"Argument 'x' must be in range [0,1], got {x}.")

    if x in [0, 0.5, 1] or k == 0: return x
    if k == -1: return 0.5
    if k == 1: return 0 if x < 0.5 else 1

    x_t = transform_range(x, (0, 1), (-1, 1))
    return (_dd_ntsig(-k, x_t) + 1) / 2

def nthsig(k:float, x:float) -> float:
    """Normalized Tunable Half-Sigmoid

    Calculates a point along a half-sigmoid-like curve between (0,0) and (1,1).

    Negative k is convex, bringing all values of y toward 0.
    Neutral k is linear between (0,0) and (1,1).
    Positive k is concave, bringing all values of y toward 1.

    https://www.desmos.com/calculator/2hkedvscyv

    Args:
        k (float): Must be in range [-1,1]. The shape of the curve.
        x (float): Must be in range [0,1]. The function will return the corresponding y value at x.
    Returns:
        float: The y value at x.
    """
    if not -1 <= k <= 1:
        raise ValueError(f"Argument 'k' must be in range [-1,1], got {k}.")
    if not 0 <= x <= 1:
        raise ValueError(f"Argument 'x' must be in range [0,1], got {x}.")

    if x in [0, 1] or k == 0: return x
    if k == -1: return 0
    if k == 1: return 1

    return _dd_ntsig(-k, x)

def biased_curve(k:float, a:float, b:float, x:float) -> float:
    """Calculates a point along a curve between (0,a) and (1,b). The bias parameter (k) bends the curve toward either a or b.

    Negative k favors a, bending the knee of the curve toward (1,a).
    Neutral k is unbiased, linear between (0,a) and (1,b).
    Positive k favors b, bending the knee of the curve toward (0,b).

    https://www.desmos.com/calculator/2hkedvscyv

    Args:
        k (float): Changes the shape of the curve so that all y values move toward either a (when k is negative), b (when k is positive), or neither (when k is 0).
        a (float): The y value at x=0.
        b (float): The y value at x=1.
        x (float): Must be in range [0,1]. The function will return the corresponding y value at x.
    Returns:
        float: The y value at x.
    """
    return a + (b - a) * nthsig(k, x)

def _dd_ntsig(k:float, x:float) -> float:
    """Dino Dini's Normalized Tunable Sigmoid

    Calculates a point along a sigmoid-like curve that goes through (-1,-1) and (0,0) and (1,1).
    Based on Dino Dini's normalized tunable sigmoid function: https://dinodini.wordpress.com/2010/04/05/normalized-tunable-sigmoid-functions/

    Negative k is steep (sigmoid curve), bringing all values of y toward -1 (for x<0) or 1 (for x>0).
    Neutral k is linear between (-1,-1) and (1,1).
    Positive k is flat (logit/log-odds curve), bringing all values of y toward 0.

    https://www.desmos.com/calculator/hvgetz6trt

    Args:
        k (float): Must be in range [-1,1]. The shape (flatness) of the curve.
        x (float): Must be in range [-1,1]. The function will return the corresponding y value at x.
    Returns:
        float: The y value at x.
    """
    if not -1 <= k <= 1:
        raise ValueError(f"Argument k must be in range [-1,1], got {k}.")
    if not -1 <= x <= 1:
        raise ValueError(f"Argument x must be in range [-1,1], got {x}.")

    if x in (-1, 0, 1) or k == 0: return x
    if k == 1: return 0
    if k == -1: return -1 if x < 0 else 1

    return (k - 1) * x / (2 * k * abs(x) - k - 1)
