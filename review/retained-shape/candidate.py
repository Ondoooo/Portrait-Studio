"""Replace repair() with a proposal-stage repair. Requires only NumPy."""

import numpy as np


def repair(proposal, editable):
    """Return an RGB uint8 image, same shape as proposal. editable is a 2D bool mask."""
    # The proposal already has the target fabric color. This baseline keeps the
    # proposal's shading, including any shading inherited from the embossed logo.
    return np.array(proposal, copy=True)
