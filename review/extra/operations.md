# Diagnosing and operating the workflow

## 1. Wrong target and foreground

Draw a rotated travel case with two colored latches and a braided cable crossing one latch. Ask for the latch next to the handle to turn yellow while the cable and other latch stay intact. Include a quarter-turned copy, a crop with the handle out of frame, and a control with the cable absent. Specify the target relative to the handle so a screen-coordinate shortcut fails.

Plant three faults independently: select the other latch, transpose the correct mask into the wrong coordinates, and paste over the cable at the end. Return the selected part ID, mask overlay, proposal and delivered native crop for each. Identify the first faulty stage and count changed protected cable pixels. When the crop removes the only disambiguating cue and there is no part ID, record the uncertainty. The check should separate the three faults and pass the clean case. A correct part ID alone earns no pixel-preservation credit.

## 2. Hidden surface ambiguity

Generate two sheets of ruled paper. Under the same opaque piece of tape, one sheet has a continuous line and the other has a gap. The visible image, including the tape, must be byte-identical for both. Save the two clean targets privately for scoring. Add an easier third case where part of the distinguishing mark remains visible.

Prove identical observed pixels and different hidden references. Have a deterministic filler return a proposed repair, then score it on both targets. Report which pixels were observed, which were inferred, and where the test actually has ground truth. Return a decision rule for how a review tool should report a plausible completion when exact recovery cannot be verified. The rule should still distinguish correct and incorrect restoration when the cue is visible.

## 3. Debug receipts

Give a toy exporter a work directory, a user-selected diagnostics directory, and a mock private sibling containing a dummy canary. Use only programmatically created files. With diagnostics off, an export should produce the normal image. With diagnostics on, return a shareable receipt that identifies the requested operation, executed branch, bypasses, stage dimensions, and hashes of the scored and saved artifacts. Offer an explicit way to include only selected synthetic stage crops.

Test two concurrent runs with the same display label and different edits, a preview substituted for a delivered crop, and a write interrupted just before completion. Check that each run stays attributable, the wrong artifact is detected, and an incomplete receipt never masquerades as complete. Audit the bundle for absolute paths, prompt free text, unsolicited image metadata and private canary values. State the privacy boundary of the test and one observation the exported receipt cannot support.

## 4. Resource admission

Use mock host commit headroom of 3 GiB before and 12 GiB after a page-file change, with a separate 4 GiB device budget in both scenarios. Include three requests: 6 GiB host / 2 GiB device, 2 GiB host / 5 GiB device without offload, and 1 GiB host / 1 GiB device with a deterministic output. Run each combination through an admission stub and record the reason for rejection. Add an injected mid-run allocation failure to show the difference between a preflight estimate and actual completion.

Return which historical-style outcomes merit a feasibility rerun and which provide any image-quality evidence. A larger host allowance can admit the first request in this model. It does not increase the device budget; the already successful control should retain its pixels. Distinguish this from the first packet's separate question about temporal sampling of real memory peaks. A recommendation about actual hardware needs a measured run.

## 5. Existing tools

Pick one component with an existing fixture, such as crop-to-source coordinates, image resampling, or color-managed export. Identify a maintained implementation and verify its input ranges, coordinate or color conventions, version, license, and dependencies against primary documentation. Compare it with the simplest existing baseline through the same callable on two fixtures, including one known-good case. Reuse the first packet's coordinate checker if you choose the mapping problem.

Return a keep/replace/defer recommendation, the adapter or pseudocode, one documented incompatibility, a command for reproduction, and measured accuracy and runtime where executable. If the library cannot be run, return a bounded integration experiment and label the recommendation provisional. Avoid an unranked catalogue of packages.
