# Second read of the shirt

Compare your original vote with the construction. A preserves much of the soft fold structure but shifts it slightly and lightens the center. B weakens and broadens the folds. C retains broad shading but adds a narrow, hard line across one fold. These are competing errors. No preference is prescribed.

The following scores came from the 800 × 324 board rendered in Microsoft Edge. Lower means closer to the reference on that particular measurement.

| Candidate | Mean absolute channel error | Mean absolute luminance-gradient error |
|---|---:|---:|
| A | 2.69 | 0.70 |
| B | 2.55 | 0.82 |
| C | 1.73 | 0.77 |

To compare pixel fidelity on the same region, rasterize the complete SVG at 800 × 324 with a browser renderer, without zoom, page margins or browser chrome. Then run:

```console
python review/score_shirt.py path/to/board.png
```

The script compares each detail crop with the original, measuring mean absolute channel error across the entire crop and mean absolute error in horizontal and vertical luminance differences. Both measures include protected pixels. A narrow conspicuous line can occupy few pixels. A broad brightness shift can accumulate a large error where the shape still reads correctly.

Record the scores separately from the initial vote. If you revise your decision, name the visible feature that changed your mind. A consistent result on one diagram establishes performance on this diagram only.
