"""lottery: Weighted random allocation library."""

import random
from typing import Dict

def lottery(n: int, weights: Dict[str, int]) -> Dict[str, int]:
    """
    Allocate n draws at random according to the given weights.

    >>> lottery(100, {"a": 14, "b": 86})  # doctest: +SKIP
    {'a': 13, 'b': 87}
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    if not weights or any(w < 0 for w in weights.values()):
        raise ValueError("weights must all be non-negative integers with at least one > 0")

    keys, vals = list(weights.keys()), list(weights.values())
    draws = random.choices(keys, weights=vals, k=n)
    return {k: draws.count(k) for k in keys}

__version__ = "1.0.4"
__all__ = ["lottery"]
