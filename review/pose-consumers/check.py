"""Public synthetic contract checks. Python standard library only."""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile


def packets(example):
    yield "clear front badge", deepcopy(example), True, "regional"
    turn = deepcopy(example)
    turn["observation_v2"]["upper_torso"].update(facing="rear", evidence="reverse jacket panel")
    yield "conflicting global and local views", turn, False, "regional"
    for field, value in (("facing", "unknown"), ("extent", "outside"), ("visibility", "hidden")):
        uncertain = deepcopy(example)
        uncertain["observation_v2"]["upper_torso"].update({field: value, "evidence": "insufficient local cue"})
        yield "uncertain " + field, uncertain, False, "regional"
    legs = deepcopy(example)
    legs["observation_v2"]["pelvis"].update(facing="rear")
    yield "irrelevant regional cue", legs, True, "regional"
    legacy = deepcopy(example)
    del legacy["observation_v2"]
    yield "legacy recipe", deepcopy(legacy), True, "legacy"
    legacy["legacy"]["view"] = "rear"
    yield "legacy reverse view", legacy, False, "legacy"
    off = deepcopy(example)
    off["regional_mode"] = "Off"
    off["delivery_crop_xyxy"] = [0, 0, 8, 8]
    yield "optional stage off; full-frame delivery", off, True, "regional"


def ppm(case, rows):
    """Canonical synthetic output encoding. Rows contain palette-index characters."""
    height, width = len(rows), len(rows[0])
    header = f"P6\n{width} {height}\n255\n".encode("ascii")
    return header + bytes(v for row in rows for char in row for v in case["palette"][int(char)])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def expected(case, edited):
    rows = case["rows"]
    native = [row.replace(str(case["badge_value"]), str(case["recolor_value"])) for row in rows] if edited else rows
    x, y, right, bottom = case["delivery_crop_xyxy"]
    final = [row[x:right] for row in native[y:bottom]]
    return native, ppm(case, final)


def validate(case, edited, basis, receipt, saved):
    native, encoded = expected(case, edited)
    if receipt["native_rows"] != native:
        raise ValueError("native pixels missed the visible badge or damaged protected pixels")
    if saved != encoded:
        raise ValueError("reopened delivered.ppm disagrees with the expected output")
    trace = receipt["trace"]
    if trace["selection"]["basis"] != basis or trace["selection"]["status"] != ("edited" if edited else "skipped"):
        raise ValueError("decision receipt disagrees with exercised route")
    if not isinstance(trace["selection"]["reason"], str) or not trace["selection"]["reason"].strip():
        raise ValueError("supply an evidence-based reason")
    native_hash = sha(ppm(case, native))
    if trace["native_review"]["artifact_sha256"] != native_hash:
        raise ValueError("native review is attached to the wrong pixels")
    if trace["detail"] != {"mode": case["regional_mode"], "status": "bypassed",
                           "input_sha256": native_hash, "output_sha256": native_hash}:
        raise ValueError("identify the skipped detail stage and verify its pixel identity")
    if trace["saved"]["file_sha256"] != sha(saved):
        raise ValueError("saved-output receipt disagrees with reopened bytes")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("adapter", nargs="?", type=Path)
    args = parser.parse_args()
    case = json.loads(Path(__file__).with_name("example.json").read_text(encoding="utf-8"))
    if args.adapter:
        spec = importlib.util.spec_from_file_location("review_adapter", args.adapter)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    for name, packet, edited, basis in packets(case):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder)
            if args.adapter:
                receipt = module.run_case(deepcopy(packet), destination)
                saved = (destination / "delivered.ppm").read_bytes()
            else:
                # Exercise the public oracle/receipt checks with known records, including a bad binding.
                native, saved = expected(packet, edited)
                n = sha(ppm(packet, native))
                receipt = {"native_rows": native, "trace": {
                    "selection": {"basis": basis, "status": "edited" if edited else "skipped", "reason": "oracle"},
                    "native_review": {"artifact_sha256": n},
                    "detail": {"mode": packet["regional_mode"], "status": "bypassed", "input_sha256": n, "output_sha256": n},
                    "saved": {"file_sha256": sha(saved)}}}
                bad = deepcopy(receipt)
                bad["trace"]["saved"]["file_sha256"] = "unbound"
                try:
                    validate(packet, edited, basis, bad, saved)
                except ValueError as exc:
                    if "reopened bytes" not in str(exc):
                        raise
                else:
                    raise ValueError("negative control escaped the validator")
            validate(packet, edited, basis, receipt, saved)
            print("PASS", name)
    print("Adapter checked." if args.adapter else "Public fixture self-check only. Supply adapter.py to test a submission.")


if __name__ == "__main__":
    main()
