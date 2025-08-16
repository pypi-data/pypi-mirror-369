# probkit

Toolkit for modifying probabilities and shaping curves.

## Features
- **Tunable sigmoid curves** - Transform distributions with controllable steepness/flatness
- **Probability modification** - Scale probabilities using ratios with proper mathematical behavior
- **Pure functional design** - Deterministic functions for precise control
- **Random sampling** - Convenient random versions for generating samples from curves
- **Zero dependencies** - Only uses Python standard library
- **Robust validation** - Input validation and comprehensive error handling
- **Well tested** - Thoroughly unit tested with edge case coverage

## Quick Start

### Deterministic Functions
```python
from probkit import ntsig, biased_curve, modified_probability

# Sigmoid-like curve through (0,0), (0.5,0.5), (1,1)
y = ntsig(k=0.5, x=0.3)  # k controls steepness

# Custom curve between any two points
y = biased_curve(k=0.2, a=10, b=100, x=0.7)  # From (0,10) to (1,100)

# Modify probability with a ratio
new_prob = modified_probability(0.3, 1.5)  # Scale 30% by 1.5x
new_prob = modified_probability(0.3, 3, 2)  # Scale 30% by ratio 3/2
```

### Random Sampling
```python
import probkit.sampling

# Optionally set seed for reproducible results
sampling.seed(42)

# Sample from curves with random x values
sample = sampling.sample_ntsig(k=0.5)
sample = sampling.sample_biased_curve(k=0.2, a=10, b=100)

# Generate multiple samples
samples = [sampling.sample_ntsig(0.3) for _ in range(1000)]
```

## API Reference

### Curve Functions
- **`ntsig(k, x)`** - Normalized tunable sigmoid. Negative k is flat (logit-like), positive k is steep (sigmoid-like)
- **`nthsig(k, x)`** - Normalized tunable half-sigmoid. Negative k is convex, positive k is concave
- **`biased_curve(k, a, b, x)`** - Custom curve between points (0,a) and (1,b) with bias k

### Probability Functions  
- **`modified_probability(k, a, b=None)`** - Scale probability by ratio `a` (or `a/b` if b provided) with proper saturation

### Random Sampling
- **`probkit.sampling.seed(value)`** - Set seed for reproducible random sampling
- **`probkit.sampling.sample_ntsig(k)`** - Sample from ntsig with random x
- **`probkit.sampling.sample_nthsig(k)`** - Sample from nthsig with random x  
- **`probkit.sampling.sample_biased_curve(k, a, b)`** - Sample from biased_curve with random x

### Utilities
- **`clamp(val, min_val, max_val)`** - Constrain value to range
- **`transform_range(x, old_range, new_range)`** - Linear transformation between ranges
- **`effective_ratio(a, b)`** - Safe division with edge case handling

## Use Cases
- **Game development** - Procedural generation, difficulty curves, loot tables
- **Simulations** - Monte Carlo methods, statistical modeling  
- **Data science** - Distribution transformation, probability weighting
- **Machine learning** - Custom activation functions, data preprocessing

## Install
Clone this repo or copy the `probkit` folder into your project. No external dependencies required.

```bash
# Example: install with pip from local folder
pip install .
```

## Testing
Run all tests with:
```bash
python -m unittest discover tests -v
```

## Deployment (notes for Taylor)
PyPI is set up to receive releases from the `main` branch or when tagged with `v*`. This is accomplished using PyPI OIDC and GitHub Actions.
Pushing to main will create a new dev release with automatic version bump.
Creating a `v*` tag will create a production release using that version number.
```bash
git tag v0.1.0 && git push --tags
```

## Contributing
Pull requests and suggestions welcome! Open an issue or PR on GitHub.

## License
MIT License. See LICENSE file for details.
