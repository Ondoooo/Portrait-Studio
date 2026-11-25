# Does Experimental change what Stable delivers?

A user renders a chart in Stable, tries Experimental, then returns to Stable. Each request should save the pixels its own settings specify. A cache collision can make the second request deliver the first request's pixels, even when both report success. Which inputs must participate in cache identity, and where should an older request acquire its missing defaults?

## Run the experiment

From this folder, run the following commands with Python 3.10 or later. The script generates two 2×2 RGB charts and all delivered PPM files in a temporary directory. It uses only the standard library and removes the directory on exit.

```sh
python isolation_demo.py
python isolation_demo.py --policy path --verbose
python isolation_demo.py --policy implicit --verbose
python isolation_demo.py --policy scoped --verbose
```

The first command exits 0 when both planted defects are detected and the reference policy passes. The single-policy commands are strict checks. A detected regression exits 1.

| Policy | Cache key | Sequences with wrong pixels | Sequences with wrong hit/miss behavior |
| --- | --- | ---: | ---: |
| `path` | Workflow filename and source filename | 12/20 | 16/20 |
| `implicit` | Chart content digest and raw strength field | 8/20 | 12/20 |
| `scoped` | Renderer version, effective mode, content digest and effective strength | 0/20 | 0/20 |

## Read the controls

Stable adds the effective strength to red. Experimental adds it to blue. Channel values saturate at 255. The initial strengths are 4 and 9 respectively. A missing mode selects Stable, a missing strength selects that mode's current default, and an explicit zero preserves every pixel. The `changed stable default` case supplies 9 for one Stable request to simulate a change while a cache survives.

Each of ten request pairs runs in both A/B/A and B/A/B order. Every sequence starts with an empty cache, and all three requests share it. The filename cases exercise two ways paths can mislead. A copied workflow can preserve every processing input, while replacing a chart in place can preserve its filename and change every pixel. The graph filename here is a label, and the operation is defined by the renderer version and effective settings.

The script reads back each saved PPM, checks the header and dimensions, and compares all twelve RGB channel values with a handwritten oracle. It checks reuse separately. For example, the two modes produce the same chart at strength zero. Both must still execute once to demonstrate mode isolation, then the repeated request should hit. An explicit Stable request may reuse the result of an equivalent legacy request. Changing an input filename alone may reuse identical chart bytes.

## Reviewer assignment

Return a minimal cache or routing fix with regression tests and exact commands to reproduce a failure before the patch and a pass afterward. The `scoped` policy is an executable reference for the toy renderer. For a proposed integration, identify the real dispatch point, default resolver, cache owner, and delivery writer. Trace a failing sequence through those components and state which effective inputs can change its output. If the real system uses models, masks, seeds, or persisted cache entries, account for the relevant identities and earlier cache versions in the patch.

Acceptance requires all of the following.

- Both weak controls must still fail in both run orders where the first request poisons the second. Name a pair and report the expected and delivered channel values.
- The corrected implementation must pass all 20 sequences, including every delivered pixel, the expected second-request hit or miss, and the third-request hit. Disabling caching fails this criterion.
- A request with both legacy fields missing must deliver the Stable default before and after Experimental runs. A deliberate zero must survive normalization. Changing an effective default or replacing chart bytes under the same path must produce fresh pixels.
- Add at least one test beyond the supplied matrix and explain which defect it would catch. For an integration claim, exercise the public submission path and its actual delivered file. Report any layer the test cannot observe.
