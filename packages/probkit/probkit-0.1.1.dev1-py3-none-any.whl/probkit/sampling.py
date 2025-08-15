"""
Random sampling functions for probkit curves and probability functions.

These functions provide convenient wrappers around the pure functions in probkit,
automatically generating random x values in [0,1] for sampling from curves.

Uses a module-level RNG for performance. Use seed() to control randomness.
"""

__all__ = ["seed", "sample_ntsig", "sample_nthsig", "sample_biased_curve"]

from random import Random
from . import curves

# Module-level RNG - created once, reused for all calls
_rng = Random()

def seed(seed_value=None):
    """Set the seed for probkit's sampling functions.
    
    Args:
        seed_value: Seed for the random number generator. If None, uses system time.
    """
    _rng.seed(seed_value)

def sample_ntsig(k:float) -> float:
    """Sample ntsig with random x."""
    return curves.ntsig(k, _rng.random())

def sample_nthsig(k:float) -> float:
    """Sample nthsig with random x."""
    return curves.nthsig(k, _rng.random())

def sample_biased_curve(k:float, a:float, b:float) -> float:
    """Sample biased_curve with random x."""
    return curves.biased_curve(k, a, b, _rng.random())
