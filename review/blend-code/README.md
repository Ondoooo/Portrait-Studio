# Coding challenge: blend a repaired object into its original photograph

A sticker or decal has been removed from a photographed object. You have the original photo, an aligned proposed repair and a soft edit mask. Conventional feathering can bring the old decal back. A direct paste can leave a color shift when the repair was rendered under different lighting. Return working code that improves both outcomes while keeping original printed details sharp.

## Send this to a coding reviewer

Use the three files in this folder. Replace the body of `candidate.blend` with a general, deterministic, CPU-only NumPy implementation. Keep the public checker intact. Return your complete `candidate.py`, one additional reproducible object-scene test of your own and a short report with the command, per-metric results, baseline comparison, one failure mode, and what observation would falsify your explanation. Include runtime and image dimensions for any timing claim. Do not tune to particular seeds, shapes, colors or coordinates, inspect the caller, import the checker from the candidate, or use external assets or pretrained models.

## Contract

| Item | Meaning |
| --- | --- |
| `source` | Original H × W × 3 RGB array. |
| `proposal` | Full-frame aligned repaired RGB image. Context around the editable region is available for comparison. |
| `alpha` | H × W geometric edit guide. Zero protects a pixel exactly. Any positive value permits replacement; the fractional value suggests proximity to the boundary. |
| Return | H × W × 3 RGB array. All inputs and the result use finite float32 values in [0, 1], in display-referred RGB. Leave inputs untouched. Handle an empty mask. |

The candidate receives only these three arrays. Ground truth, edit causes, seeds and damage regions belong to the evaluator. The suite includes a decal on grained packaging, a tone mismatch on an aligned replacement, a correct repair around a genuine printed registration line, and a sticker that hides the presence or absence of ink.

## Run and interpret

With Python 3 and NumPy installed, run the following inside this folder.

```sh
python check.py
python check.py --seed 907
```

The checker prints JSON and exits with 0 on a pass or 1 on a failed check. Each invocation runs three consecutive seeds. All tests and alternate seeds in this package are public. Additional seeds vary colors, dimensions, placement, grain and lighting within the same construction. A claim of transfer to new objects requires a separately constructed scene.

Error units are RGB levels on a 0–255 scale. The decal metric measures remaining damage in the soft collar. The two cast metrics measure absolute color errors inside the edit and in its collar. Print contrast measures error in the color difference across the real stripe. The good-pixel metric covers all undamaged editable pixels in the print control. Every case checks the entire protected exterior for exact equality.

Measured means for the packaged starter, seeds 731–733:

| Method | Decal collar | Cast interior | Cast collar | Print contrast | Good pixels | Treatment mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Starter / ordinary feather | 24.599 | 10.236 | 14.443 | 0.000 | 0.000 | 16.426 |
| Hard paste inside mask | 0.000 | 10.236 | 10.235 | 0.000 | 0.000 | 6.824 |

For **each seed**, reduce decal-collar error to at most 45% of feather, cast-interior error to 55% of paste, and cast-collar error to 65% of the better control. The mean of those three treatment metrics must be at most 65% of the better control's mean. Print-contrast error must stay at or below 2 levels and good-pixel error at or below 1 level. These are engineering targets for these rendered scenes. The starter fails all four treatment checks on all three default seeds and passes the preservation checks.

The ambiguous sticker has identical inputs for two equally weighted possible originals. The checker reports errors in the hidden region under each original without a pass/fail gate. The two truths differ by 102 levels, giving a lower bound of 51 on their average absolute error. The starter scores 0 and 102. Explain what extra observation or user instruction would settle the ambiguity.
