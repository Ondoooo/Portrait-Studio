# Fix a rotated crop's return coordinates

An annotation tool crops an image, changes its orientation, then resizes it for display. A click on a labeled pixel must map back to that pixel's original center. The starter loses alignment in one of six views. Fix `map_to_source` in `candidate.py` and explain which operation first introduced the error.

## Run

From this directory use Python 3.8 or newer. Both commands run offline using the standard library.

```text
python -B check.py
python -B check.py --json
```

The first command prints the per-view results. The second prints the input, expected and returned centers, per-axis error and outcomes of all checker controls. The starter exits with code 1. A passing solution exits with code 0.

## Contract

- `points` maps arbitrary labels to continuous target-view coordinates `(x, y)`. Return a new mapping with each original label and its recovered source center. Valid crops may have any integer size and offset. Image-edge coordinates start at zero and the center of source pixel at index `(i, j)` is `(i + 0.5, j + 0.5)`.
- The forward pipeline takes a half-open source crop `(left, top, right, bottom)`, orients that cropped rectangle using `identity`, `flip_x` (horizontal reflection) or `cw90` (clockwise quarter turn), then resizes its full extent to positive integer `target_size = (width, height)`. Each axis scales independently. Preserve continuous coordinates until the caller selects a raster pixel.
- The checker uses a 37 × 23 coordinate grid and an offset 28 × 18 crop. It builds reference views by rearranging the grid cells and finding the four labels. It checks each orientation at native size and at 19 × 13. The checker separately plants horizontal, vertical and diagonal one-pixel shifts, exchanged labels and switched scale factors. Switching identical scale factors is an unchanged control.

## Acceptance and handoff

All six views must return every label, with at most 0.01 source pixel error on each axis. All 36 checker controls must match their expected outcomes. Apply the coordinate rule generally across crop positions, sizes and labeled points. Keep the supplied fixtures, tolerance and checker fixed.

Return the revised `candidate.py`, the output from both commands, and a short explanation that names the failed original view and explains why another view concealed the error.
