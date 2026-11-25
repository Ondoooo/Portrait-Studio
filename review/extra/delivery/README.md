# Which export stage damaged the product label?

The fixture draws a 256 × 132 grayscale product card with a smooth gradient, a painted stripe, six printed glyphs and a repeating weave. The delivery target is a faithful, full-size copy. The program holds the original pixel layout as ground truth. It runs on CPU and reads no images from disk.

Run from this directory with Python 3, NumPy and Pillow installed.

```console
python check_delivery.py --out card-results
```

Choose a new or empty output directory. The command writes the source, intermediates, delivery and alternate weave as six PNGs, plus a JSON report. Omit `--out` to check in memory. A failed check returns exit code 1.

## Attribute the first visible damage

| Saved stage | Change | Evidence on the fixture |
|---|---|---|
| Source | The single painted stripe belongs on the card. A full-size lossless PNG round trip is the export control. | No repeated steps on the ramp. The stripe has two hard edges enclosing one plateau. Its pixels survive tone export exactly. |
| Tone export | Round the gradient to the nearest multiple of 16 gray levels. | Seven plateaus qualify between large jumps on the ramp. The print and weave still match their source. |
| Small preview | Reduce to 64 × 33 by averaging 4 × 4 blocks. Return to delivery dimensions with bicubic interpolation for a registered comparison. Both sizes are saved. | Ink recall falls to 30%. The weave differs from the source by 22 gray levels per pixel on average. The repeated-step detector now misses the earlier tone damage because interpolation softened its edges. |
| Sharpened delivery | Add six times the residual from a 3 × 3 mean filter and clip to 8 bits. | Ink recall rises to 62%, while the share of paper falsely classified as ink rises from 3.3% to 8.7%. The 99th percentile excursion beyond the known ink and paper range rises from 8 to about 31 gray levels. |

Inspect each delivery-size PNG at one image pixel per display pixel. Compare identical coordinates in the fixed regions defined at the top of the script. On the glyphs, check whether counters stay open, vertical strokes remain separated and bright or dark rims appear. On the weave, follow the dark diagonal through the same starting pixel. On the ramp, trace the new boundaries backward through the saved stages. For a blind visual review, randomize candidate filenames, supply the source as the reference and keep the stage key and report hidden until the reviewer records a verdict.

## Test a claim of recovered detail

Return a stage-attribution checker on a second card that you design. Move the printed label, rotate the ramp and include several legitimate painted stripes. Compare your checker with reusing the original fixed coordinates and thresholds. Show one error that the original checker makes on the new design, the first saved stage that establishes it, and whether the new checker preserves the clean control. Include runnable code and count false alarms and misses. If there is too little evidence to name the cause from the final card alone, record that uncertainty.

For a candidate in the same pixel coordinates, pass its grayscale array and `card()` to `metrics`. Compare its results with both the resized preview and the original. Ink recall counts true ink locations below 133. The false-ink fraction counts original paper locations below that threshold, with paper as the denominator. Inspect both numbers alongside the edge excursions. Exact recovery on this card would place every stroke and the weave at their source positions. High contrast alone cannot establish that result.

The alternate control shifts the dark weave by two pixels. It preserves the original contrast standard deviation of 22, but every weave pixel is wrong by 44 levels. The original and alternate print produce **byte-identical low-resolution pixel arrays** after 4 × 4 averaging. No method seeing that preview alone can tell which weave was present. A sharper plausible weave is an unverified reconstruction without the original or an independent higher-resolution capture.

The detectors know the coordinates, orientation, tones and intent of this card. Their thresholds are fixture assertions. Repeated painted stripes could trip the ramp detector, while gradual contours or steps at another orientation could escape it. For a product-photo trial, register a separately retained full-resolution reference, mask known art separately from smooth shading, and include clean packaging with repeated intentional stripes and genuine fine print. Record false alarms per clean region alongside misses per damaged region and compare results on unseen products. Without aligned ground truth, report observed halos, stroke ambiguity and reviewer preference separately from any claim of fidelity.
