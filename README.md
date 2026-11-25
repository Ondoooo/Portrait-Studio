# Portrait Studio

For the current independent review, start with the [assignments and reviewer prompt](review/NEXT.md). The [original visual tests](review/README.md) include the white-shirt comparison.

Portrait Studio is a local ComfyUI photo-editing workflow. The operator supplies one photograph and an edit request. The workflow selects an area, generates candidate edits, blends a selected candidate into the original, and prepares a finished image. The aim is a believable local edit that preserves the lighting, texture, composition and foreground objects that belong in the photograph.

This repository describes the workflow and contains two standalone finishing filters and a reproducible editing example. The full application, model weights, personal photos and run records stay local.

## How an edit reaches the saved image

| Stage | What happens | Why the distinction matters |
|---|---|---|
| Input and selection | The workflow assesses framing, orientation and visible regions, then selects an edit mask. | The subject can be turned, partly outside the frame, or blocked by a foreground object. A plausible overall pose can still yield a wrong local selection. |
| Guide and generation | A guide provides context for a masked edit. The active model receives the inputs and settings supported by its route and produces candidate pixels. | The mask says where an edit is allowed. The guide can still describe the old object's shading inside that mask. |
| Selection and return to the original | The workflow chooses a proposal, places it back on the original pixel grid and blends its edges. | A clean proposal can acquire a source edge during this step. A small halo can be almost invisible on a full-frame preview. |
| Native review and optional refinement | A quality report describes the native result. A later regional step may change pixels or pass the image through. In the saved Complete workflow, the Auto regional setting passes it through. | The selected setting, the operation that actually ran and the image that was scored are separate facts. |
| Delivery | The workflow applies the selected framing, resolution and photographic finish, then saves the result. | A native crop and the delivered image can show different amounts of grain or edge contrast. Release review uses the saved image. |

## A worked example: removing a sticker from ruled paper

Imagine asking an editor to remove an orange oval sticker. The paper's faint horizontal rules should continue across the old sticker location. The surrounding paper should keep its original color and grain. If the orange disappears but you can still point to the oval, the edit has missed part of the request.

The example builds the clean sheet first, then adds a sticker with a dark rim. This gives us the exact appearance of the paper behind it. Two controlled runs create similar-looking final defects at different stages.

| Run | Guide | Proposal | Final composite | What the intermediate images establish |
|---|---|---|---|---|
| A | Gray oval on paper | Same gray oval | Same gray oval | The fill adopted the paper's color while retaining the sticker's brightness pattern. The outline was already present before compositing. |
| B | Clean paper | Clean paper | Orange fringe | The clean proposal matched the known original. The blend gave the source image weight around the edit boundary and restored part of the rim. |

On an 8-bit scale, the **mean absolute RGB error on the sticker rim** goes from **27.0 → 27.0 → 27.0** in A and **0.0 → 0.0 → 49.3** in B across guide, proposal and composite. Pixels outside the oval match the original exactly in both runs. An exterior-preservation check alone would therefore pass both failures.

The script uses deterministic image arithmetic and a controlled stand-in for the proposal. It runs with NumPy and Pillow on CPU. From the repository root:

```console
python sticker_example.py --output sticker-example.png
```

The generated board shows the source, guide, proposal and composite side by side. Each row has the same target and the same known reference. The example can be inspected or rerun without access to any project photographs or model checkpoints.

## What the project evidence supports

In one local comparison, changing source hue at fixed brightness had almost no effect on the reconstructed guide. Removing the guide's source-shading contribution weakened two measured edges, while another contour survived. The same change brought no meaningful improvement on a second scene with a known original. A separate comparison found that an edge became visible again when a proposal was blended back into the source. Another scene used a different guide and its remaining outline is still unexplained. The sticker example isolates two mechanisms seen across those comparisons. It cannot identify which mechanism caused a new photograph's artifact.

The practical diagnostic question is **where the old outline first becomes visible**. Compare the source, the exact guide used, the selected proposal, the image immediately after blending, and the saved delivery at the same coordinates. Record what must change and what should be preserved. Judge the whole image and a native-size crop separately. A final screenshot with a faint oval is evidence that the edit failed. On its own, it gives little evidence for choosing between a guide, a model or a compositor change.

## Finishing utilities

`photo_finish.py` exposes `gentle_contrast(image)` and `fine_detail(image)` for floating-point PyTorch RGB tensors shaped `[N, H, W, 3]` in the range 0–1. The first applies a mild luminance curve. The second brings out existing edges with a bounded luminance adjustment. Both operate at the delivery stage. Their source is included so readers can see exactly what the finishing step contributes.
