"""Starter for a masked repair of a photographed object. Requires NumPy."""

import numpy as np


def blend(source: np.ndarray, proposal: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """Return a fresh float32 RGB image. See README.md for the input contract."""
    result = source.copy()
    editable = alpha > 0
    weight = alpha[editable, None]
    result[editable] = source[editable] + weight * (proposal[editable] - source[editable])
    return result
