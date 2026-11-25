"""Run a deterministic product-card export challenge. Requires NumPy and Pillow."""

import argparse
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image


RAMP = (16, 12, 240, 44)
STRIPE = (16, 52, 240, 76)
PRINT = (16, 92, 116, 120)
WEAVE = (136, 92, 240, 120)
GLYPHS = (
    ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
)


def region(array, box):
    left, top, right, bottom = box
    return array[top:bottom, left:right]


def card():
    a = np.full((132, 256), 170, dtype=np.uint8)
    region(a, RAMP)[:] = np.rint(np.linspace(58, 200, RAMP[2] - RAMP[0]))
    region(a, STRIPE)[:] = 172
    a[52:76, 98:118] = 88
    label = region(a, PRINT)
    label[:] = 192
    for i, glyph in enumerate(GLYPHS * 2):
        bits = np.array([list(row) for row in glyph]) == "1"
        mask = bits.repeat(2, 0).repeat(2, 1)
        start = 4 + 16 * i
        label[6:20, start:start + 10][mask] = 74
    y, x = np.indices(region(a, WEAVE).shape)
    region(a, WEAVE)[:] = np.where((x + y) % 4 < 2, 110, 154)
    return a


def quantize_ramp(a):
    b = a.copy()
    ramp = region(b, RAMP)
    ramp[:] = np.rint(ramp / 16) * 16
    return b


def small_preview(a):
    height, width = a.shape
    return Image.fromarray(a).resize((width // 4, height // 4), Image.Resampling.BOX)


def delivery_size(preview, a):
    return np.array(preview.resize((a.shape[1], a.shape[0]), Image.Resampling.BICUBIC))


def sharpen(a):
    f = a.astype(float)
    pad = np.pad(f, 1, mode="edge")
    mean = sum(pad[y:y + f.shape[0], x:x + f.shape[1]]
               for y in range(3) for x in range(3)) / 9
    return np.rint(np.clip(f + 6 * (f - mean), 0, 255)).astype(np.uint8)


def repeated_steps(patch):
    # Count large jumps separated by plateaus on a horizontal scan line.
    profile = patch.astype(float).mean(axis=0)
    edges = np.flatnonzero(np.abs(np.diff(profile)) >= 7)
    return sum(1 for a, b in zip(edges, edges[1:])
               if b - a >= 4 and np.ptp(profile[a + 1:b + 1]) <= 2)


def metrics(a, ref):
    label = region(a, PRINT).astype(float)
    true_label = region(ref, PRINT).astype(float)
    weave = region(a, WEAVE).astype(float)
    true_weave = region(ref, WEAVE).astype(float)
    ink = true_label < 133
    recovered = label < 133
    # Include the entire black/white transition, including its light side.
    overshoot = np.maximum(74 - label, label - 192).clip(min=0)
    return {
        "ramp_plateaus": repeated_steps(region(a, RAMP)),
        "stripe_plateaus": repeated_steps(region(a, STRIPE)),
        "ink_recall": float(recovered[ink].mean()),
        "false_ink_fraction_of_paper": float(recovered[~ink].mean()),
        "print_overshoot_p99": float(np.percentile(overshoot, 99)),
        "weave_mae": float(np.abs(weave - true_weave).mean()),
        "weave_contrast_sd": float(weave.std()),
    }


def challenge(save_to=None):
    source = card()
    banded = quantize_ramp(source)
    preview = small_preview(banded)
    scaled = delivery_size(preview, source)
    stages = {
        "source": source,
        "tone_export": banded,
        "preview_restored_to_delivery_size": scaled,
        "sharpened_delivery": sharpen(scaled),
    }
    # A second physically different printed pattern has the same 4x4 means.
    alternate = source.copy()
    region(alternate, WEAVE)[:] = np.roll(region(source, WEAVE), 2, axis=1)
    same_preview = np.array_equal(small_preview(source), small_preview(alternate))
    wrong = metrics(alternate, source)
    measurements = {name: metrics(a, source) for name, a in stages.items()}
    first = {}
    for name, m in measurements.items():
        for defect, flagged in {
            "repeated_tone_steps": m["ramp_plateaus"] >= 3,
            "missing_print_strokes": m["ink_recall"] < 0.75,
            "weave_damage": m["weave_mae"] > 10,
            "excess_print_edge_overshoot": m["print_overshoot_p99"] > 20,
        }.items():
            if flagged:
                first.setdefault(defect, name)
    expected = {
        "repeated_tone_steps": "tone_export",
        "missing_print_strokes": "preview_restored_to_delivery_size",
        "weave_damage": "preview_restored_to_delivery_size",
        "excess_print_edge_overshoot": "sharpened_delivery",
    }
    baseline = measurements["source"]
    before_sharpen = measurements["preview_restored_to_delivery_size"]
    after_sharpen = measurements["sharpened_delivery"]
    encoded = io.BytesIO()
    Image.fromarray(source).save(encoded, format="PNG")
    encoded.seek(0)
    with Image.open(encoded) as decoded:
        clean_roundtrip = np.array_equal(np.array(decoded), source)
    checks = {
        "first_flags_match_injected_stages": first == expected,
        "source_and_tone_stage_keep_painted_stripe": np.array_equal(
            region(source, STRIPE), region(banded, STRIPE)
        ) and np.ptp(region(banded, STRIPE)) == 84,
        "painted_stripe_never_called_repeated_banding": all(
            m["stripe_plateaus"] < 3 for m in measurements.values()),
        "reference_has_exact_ink_and_texture": baseline["ink_recall"] == 1
        and baseline["false_ink_fraction_of_paper"] == baseline["weave_mae"] == 0,
        "source_survives_full_size_png_roundtrip": clean_roundtrip,
        "sharpening_recovers_some_ink_but_also_marks_more_paper": (
            after_sharpen["ink_recall"] > before_sharpen["ink_recall"] and
            after_sharpen["false_ink_fraction_of_paper"] >
            before_sharpen["false_ink_fraction_of_paper"]
        ),
        "different_weaves_produce_identical_preview": same_preview and wrong["weave_mae"] == 44,
        "false_recovery_matches_contrast": wrong["weave_contrast_sd"] == baseline["weave_contrast_sd"],
    }
    report = {"first_flags": first, "stages": measurements, "wrong_phase_control": wrong,
              "checks": {name: bool(value) for name, value in checks.items()}}
    if save_to:
        save_to.mkdir(parents=True, exist_ok=True)
        if any(save_to.iterdir()):
            raise SystemExit("Choose an empty output directory.")
        for name, a in {**stages, "wrong_phase_control": alternate}.items():
            Image.fromarray(a).save(save_to / (name + ".png"))
        preview.save(save_to / "actual_low_resolution_preview.png")
        (save_to / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="optional empty directory for PNGs and JSON")
    report = challenge(parser.parse_args().out)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if all(report["checks"].values()) else 1)
