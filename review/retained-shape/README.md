# Remove the raised logo from a woven tool pouch

A tool pouch manufacturer wants a flat, unbranded canvas panel. The draft has already changed a raised logo to the surrounding fabric color. Two linked loops still read as an emblem because their highlights and shadows survived **in the proposal itself**. Your input is that proposal. There is no paste or later composite in this exercise.

Repair the 144 × 96 fabric detail without erasing the stitching, the fold crossing the emblem, or the weave. Keep the legitimate embossed fitting near the upper right intact. The editable rectangle contains both damaged and healthy cloth.

## Run and return

Use Python 3 and NumPy. From this directory, run the starter. Exit code 1 means at least one candidate row missed a limit.

```console
python -B check.py
```

Copy [candidate.py](candidate.py) to your own module and implement `repair(proposal, editable)`. Its only inputs are the recolored RGB uint8 proposal and a boolean mask. Return a same-size RGB uint8 image. Use the surrounding cloth as evidence. Keep the fixture generator, seed, scoring reference, and evaluation masks out of the repair. The evaluator can render the clean panel because this is a synthetic test.

```console
python -B check.py --candidate my_repair.py --board pouch-review.ppm
```

The optional new PPM shows the proposal, your returned repair and the clean scoring reference, left to right at 3×. Choose a new filename for each board. Inspect whether the loop, seam and fold remain legible and whether the intact outer fitting changed. Freeze the method, then have a reviewer choose two additional nonnegative integer seeds and run `python -B check.py --candidate my_repair.py --seeds N M` with their values.

Return your candidate module, command, scores by seed and one visual observation at the crossing seam. Point to the earliest supplied frame with the unwanted shape. If it fails, identify which adjacent fabric feature your method damaged or which part of the emblem survived.

## Pass criteria

Every candidate row must meet every limit on the three published seeds and the two reviewer-chosen seeds. Luminance here is the mean RGB channel value on a 0–255 scale. The clean target, true logo support and structural bands are available only to the scorer.

| Score | What it catches | Maximum |
| --- | --- | ---: |
| relief | Absolute fraction of original logo-shaped shading retained, including inverted shading | 0.35 |
| logo_mae | Mean absolute luminance error across the original relief | 2.5 |
| seam_grad | Mean vertical gradient error along the horizontal seam | 1.5 |
| fold_grad | Mean vertical gradient error along the fold | 1.4 |
| weave_hp | Mean error in local high-frequency variation away from the seam and fold | 0.9 |
| chroma | Mean absolute per-channel error after removing luminance error, over the editable area | 0.5 |
| outside_px | Changed pixels anywhere outside the editable area | 0 |

On the three published seeds the unmodified recolor retained roughly 100% of the relief. The flat fill retained only 16–21% yet failed the seam, fold and weave checks. A separately simulated shallow emboss retained about 16% and passed every check. A trial repair using only the allowed inputs also cleared the limits on those three seeds and four additional seeds. Its implementation is left out so reviewers can propose their own methods. These are synthetic canvas measurements. More seeds vary the placement, fold, weave phase and noise within the same family.
