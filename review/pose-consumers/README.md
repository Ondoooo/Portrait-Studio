# Who actually consumes a pose estimate?

The [regional-pose exercise](../regional-pose/README.md) asks which regional observations an analyzer could represent. This follow-up asks which consumers should use them, how to introduce them safely, and what evidence would show that a change reached the saved image. You can do this exercise independently. Use only the supplied synthetic mannequin, its jacket badge and its two-tone trousers.

## Confirmed architecture

This map comes from the saved six-node graph and an inspection of the owning workspace callbacks. It identifies code paths and configuration. No original photograph, live execution trace or generated model result is provided.

| Stage | Represented information and actual uses |
| --- | --- |
| 1. Load | The loader sends the imported image to one composite editing node. Pose detection runs inside that node, before optional color processing. Ambiguous or missing subjects can return early with only the original dimensions available for pose-dependent delivery. |
| 2. Produce pose | A Keypoint R-CNN supplies a person box and 17 two-dimensional landmarks and scores. The analysis can try quarter turns, align a working copy, and use geometry and contextual image checks to estimate whole-person posture and view. Its dictionary contains original and aligned dimensions and boxes, original-frame points, resized-crop points, confidence data, crop geometry, working turns and suggested delivery turns. There are no independently evidenced regional facing fields in this representation. A keypoint score does not identify which object occludes a landmark. |
| 2. Consume pose internally | The editor runs selection on an aligned crop, using points and scores together with a separate pixel parser. Whole-person view and posture affect region eligibility, choice of processing coordinates and prompt text. Native retry/acceptance uses image-quality findings. Eligible branches may also cache cropped evidence and masks on the pose dictionary for later refinement. A pose packet therefore mixes observations, working state and optional image data. |
| 3. Optional detail | The node receives the accepted native image, pose packet and native report. The saved graph selects Auto. In the inspected callback both Auto and Off bypass sampling and return the incoming image. An explicitly selected eligible branch may read the cached context, sample, accept a local change, reject it, or skip for insufficient evidence. A pose wire into this node alone establishes none of those runtime outcomes. |
| 4. Deliver | Delivery receives the detail node's image and report. Its pose wire comes directly from stage 2. It checks original dimensions; adaptive framing can use the original box, points, scores, posture, scene flags, suggested turns and a preview of the incoming edited image. Optional crop, leveling, rotation, resizing and finish can change the image after native review. |
| 5–6. Save and preview | One sink takes delivery pixels; another displays the combined text. The broad quality finding concerns the native image upstream of optional detail and delivery. The workspace delivery callback can record its own operations when a diagnostic receipt is requested. A report forwarded into that callback and a delivery completion message do not independently verify an upstream branch or successful file encoding. |

Missing evidence includes which observation and coordinate frame each conditional decision actually read, whether a sampled result survived acceptance, and which exact saved artifact a quality statement describes. Separate these questions when designing instrumentation. Keep source observations distinct from chosen routes and from measurements made on produced pixels.

## Return a proposal and a working adapter

1. Critique this graph. Trace the consequences of a front-facing jacket over a turned pelvis, an obscured badge, a cropped region and a sparse old packet. Name a consumer that should change and one that should keep using the existing geometry. Compare at least two designs for storing or passing regional observations. Address missing cues, score calibration, coordinate transforms, coupling and possible operational cost.
2. Supply a versioned interface example, a producer/consumer table, and a phased migration with rollback. Identify the owner, units, coordinate frame and uncertainty of each new field. Describe a shadow-only comparison, which consumers could opt in first, and how an older saved recipe retains its behavior. Explain the difference between an unavailable field, a reported unknown and a contradictory observation.
3. Return a standalone Python 3 `adapter.py` implementing `run_case(packet, directory) -> dict`. Use the supplied [fixture](example.json) and [checker](check.py). Include one dissimilar synthetic counterexample of your own, its expected behavior and the observed result. Report which intervention changed a route, whether any pixels changed, which stages bypassed and what would falsify your claim. You may critique the public acceptance policy separately.

### Adapter contract

Rows are 8 × 8 palette indices, with x increasing right and y down. The mannequin is fully clothed. Index 3 marks a candidate jacket accent, and index 5 is its requested green replacement. Its intended side must be established by the supplied observations. Independent perturbations of an observation with identical image evidence test consumer behavior; these packets are synthetic interventions.

- With v2 observations present, recolor only visible badge pixels when the upper torso is front-facing, fully in frame and clear. Skip for rear, unknown, outside or hidden. A pelvis-only change must leave this jacket decision unchanged.
- Without v2, reproduce this exercise's older behavior: recolor by the legacy front-view label, otherwise preserve the original. That rule, the jacket task, synthetic labels, and receipt below are proposed **test contracts**, separate from the confirmed historical architecture.
- Auto and Off pass the accepted native pixels through. Apply the supplied half-open crop to those pixels and write `directory / "delivered.ppm"`. Use binary P6 RGB, with ASCII header `P6\nW H\n255\n` and raw RGB triplets. The checker reads this file back. The helper `ppm(case, rows)` documents canonical bytes; your adapter should run independently.
- Return the native rows and a receipt as shown below. Hash canonical PPM bytes at each named stage using SHA-256. The contract exercises native review **binding** only. It makes no claim about visual quality. A detailed alternative design can add observations alongside the tested fields.

```text
native_rows: list[str]              # accepted image in the original frame
trace.selection: {basis: "regional" | "legacy", status: "edited" | "skipped", reason: string}
trace.native_review: {artifact_sha256: string}
trace.detail: {mode: "Auto" | "Off", status: "bypassed", input_sha256: string, output_sha256: string}
trace.saved: {file_sha256: string}
```

Run `python check.py` to check the public fixtures, then `python check.py adapter.py` to check a submission. The checker compares every native index and every reopened output byte and exercises a mismatched saved-artifact receipt in its self-check. The nine cases are public. Passing them demonstrates behavior for these inputs. A self-reported reason alone cannot establish which code actually read a field, general pose accuracy or visual quality.
