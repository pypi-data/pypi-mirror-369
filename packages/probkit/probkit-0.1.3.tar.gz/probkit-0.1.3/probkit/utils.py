"""
General utility functions for probkit.
"""

__all__ = ["clamp", "transform_range", "effective_ratio"]

def clamp(val:float, min_val:float, max_val:float) -> float:
    """Clamp a value between min_val and max_val.

    Args:
        val (float): The value to clamp.
        min_val (float): The minimum allowed value.
        max_val (float): The maximum allowed value.
    Returns:
        float: The clamped value.
    """
    return min(max(val, min_val), max_val)

def transform_range(x:float, oldrange:tuple[float,float], newrange:tuple[float,float]=(0,1)) -> float:
    """Translate and/or scale a variable from one range to another.

    If newrange is not provided, normalize x on (0,1).

    Args:
        x (float): The value of x relative to oldrange.
        oldrange (tuple): The (min,max) values of the old range. Note: min does not necessarily have to be <max.
        newrange (tuple): The (min,max) values of the new range. Note: min does not necessarily have to be <max.
    Returns:
        float: The transformed value of x relative to newrange.
    """
    return (x - oldrange[0]) * (newrange[1] - newrange[0]) / (oldrange[1] - oldrange[0]) + newrange[0]

def effective_ratio(a:float, b:float) -> float:
    """Calculate the effective ratio a/b, handling edge cases.

    Args:
        a (float): The numerator.
        b (float): The denominator.
    Returns:
        float: The ratio a/b, or 0 if a=0, or inf/-inf if b=0.
    """
    if a == 0:
        return 0
    if b == 0:
        return float('inf') if a > 0 else float('-inf')
    return a / b
