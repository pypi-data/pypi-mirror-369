"""Utility functions for computing statistics."""

from __future__ import annotations

from typing import Dict, Iterable

import numpy as np


def calculate_stats(values: Iterable[float]) -> Dict[str, float]:
    """Calculate basic statistics for *values* using NumPy.

    The input iterable is converted to a NumPy array once, and then fast
    vectorized aggregations compute the summary statistics.
    """
    arr = np.asarray(values, dtype=float)
    return {
        "sum": float(arr.sum()),
        "min": float(arr.min()),
        "max": float(arr.max()),
        "mean": float(arr.mean()),
    }
