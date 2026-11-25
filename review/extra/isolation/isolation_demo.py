"""A tiny two-mode renderer with intentionally weak cache keys and a reference key."""

import argparse
import hashlib
import tempfile
from dataclasses import dataclass
from pathlib import Path


HEADER = b"P6\n2 2\n255\n"
CHARTS = {
    "a": bytes([10, 20, 30, 250, 1, 249, 0, 100, 0, 255, 255, 255]),
    "b": bytes([3, 7, 11, 240, 4, 250, 128, 80, 0, 255, 254, 253]),
}

# Fixed hand-calculated RGB triples in raster order, independent of render().
EXPECTED = {
    ("a", "stable", 4): bytes([14, 20, 30, 254, 1, 249, 4, 100, 0, 255, 255, 255]),
    ("a", "experimental", 4): bytes([10, 20, 34, 250, 1, 253, 0, 100, 4, 255, 255, 255]),
    ("a", "experimental", 9): bytes([10, 20, 39, 250, 1, 255, 0, 100, 9, 255, 255, 255]),
    ("a", "stable", 0): CHARTS["a"],
    ("a", "experimental", 0): CHARTS["a"],
    ("a", "stable", 9): bytes([19, 20, 30, 255, 1, 249, 9, 100, 0, 255, 255, 255]),
    ("b", "stable", 4): bytes([7, 7, 11, 244, 4, 250, 132, 80, 0, 255, 254, 253]),
}


@dataclass(frozen=True)
class Job:
    # graph is the workflow's saved filename. A legacy job omits mode.
    graph: str = "portrait.json"
    source: str = "chart.ppm"
    chart: str = "a"
    mode: str | None = "stable"
    strength: int | None = 4
    stable_default: int = 4

    def payload(self):
        fields = {}
        if self.mode is not None:
            fields["mode"] = self.mode
        if self.strength is not None:
            fields["strength"] = self.strength
        return fields


@dataclass(frozen=True)
class Case:
    name: str
    left: Job
    right: Job
    left_expected: tuple
    right_expected: tuple
    should_reuse: bool = False


A4 = ("a", "stable", 4)
E4 = ("a", "experimental", 4)
CASES = [
    Case("same paths and explicit strength", Job(), Job(mode="experimental"), A4, E4),
    Case("different graph filenames", Job(), Job(graph="lab.json", mode="experimental"), A4, E4),
    Case("mode-specific defaults", Job(strength=None), Job(mode="experimental", strength=None),
         A4, ("a", "experimental", 9)),
    Case("legacy fields absent", Job(mode=None, strength=None), Job(mode="experimental"),
         A4, E4),
    Case("legacy equals explicit stable", Job(mode=None, strength=None), Job(), A4, A4, True),
    Case("different bytes at same source path", Job(), Job(chart="b"), A4, ("b", "stable", 4)),
    Case("same bytes at different source paths", Job(), Job(source="copy.ppm"), A4, A4, True),
    Case("changed stable default", Job(strength=None), Job(strength=None, stable_default=9),
         A4, ("a", "stable", 9)),
    Case("explicit zero survives defaults", Job(strength=0), Job(strength=None),
         ("a", "stable", 0), A4),
    Case("equal pixels still exercise both modes", Job(strength=0), Job(mode="experimental", strength=0),
         ("a", "stable", 0), ("a", "experimental", 0)),
]


def render(pixels, mode, strength):
    result = bytearray(pixels)
    channel = {"stable": 0, "experimental": 2}[mode]
    for offset in range(channel, len(result), 3):
        result[offset] = min(255, result[offset] + strength)
    return bytes(result)


def read_chart(path):
    data = path.read_bytes()
    if not data.startswith(HEADER) or len(data) != len(HEADER) + 12:
        raise ValueError(f"Unexpected chart dimensions, format or payload in {path.name}")
    return data[len(HEADER):]


def submit(job, directory, cache, policy, output):
    path = directory / job.source
    path.write_bytes(HEADER + CHARTS[job.chart])
    pixels = read_chart(path)
    fields = job.payload()
    mode = fields.get("mode", "stable")
    strength = fields.get("strength", {"stable": job.stable_default, "experimental": 9}[mode])
    digest = hashlib.sha256(pixels).digest()
    if policy == "path":
        key = (job.graph, job.source)
    elif policy == "implicit":
        # Omission is keyed as None, even when the resolved default has changed.
        key = (digest, fields.get("strength"))
    elif policy == "scoped":
        key = ("chart-render-v1", mode, digest, strength)
    else:
        raise ValueError(policy)
    hit = key in cache
    if not hit:
        cache[key] = render(pixels, mode, strength)
    output.write_bytes(HEADER + cache[key])
    return hit


def run_case(case, policy, directory, reverse):
    steps = [(case.left, case.left_expected), (case.right, case.right_expected)]
    if reverse:
        steps.reverse()
    # A/B/A checks restoration after the other request and repeat-hit behavior.
    steps.append(steps[0])
    cache = {}
    issues = []
    saved = []
    for index, (job, oracle) in enumerate(steps):
        path = directory / f"delivered-{index}.ppm"
        hit = submit(job, directory, cache, policy, path)
        if hit != (False, case.should_reuse, True)[index]:
            issues.append(f"step {index + 1}: unexpected {'hit' if hit else 'miss'}")
        saved.append((path, EXPECTED[oracle]))
    for index, (path, expected) in enumerate(saved):
        if read_chart(path) != expected:
            issues.append(f"step {index + 1}: delivered pixels differ")
    return issues


def check(policy, directory, verbose):
    pixel_failures = set()
    reuse_failures = set()
    for case in CASES:
        for reverse in (False, True):
            issues = run_case(case, policy, directory, reverse)
            order = "B/A/B" if reverse else "A/B/A"
            for issue in issues:
                if "pixels" in issue:
                    pixel_failures.add((case.name, order))
                else:
                    reuse_failures.add((case.name, order))
            if verbose:
                print(f"  {order} {case.name}: {', '.join(issues) or 'OK'}")
    print(f"{policy:8} {len(CASES) * 2} sequences, {len(pixel_failures)} with pixel failures, "
          f"{len(reuse_failures)} with reuse failures")
    return pixel_failures, reuse_failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", choices=("path", "implicit", "scoped"), help="strict single-policy test")
    parser.add_argument("--verbose", action="store_true", help="print findings by case and order")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="chart-cache-") as local:
        directory = Path(local)
        if args.policy:
            pixels, reuse = check(args.policy, directory, args.verbose)
            return int(bool(pixels or reuse))
        results = {name: check(name, directory, args.verbose) for name in ("path", "implicit", "scoped")}
    # Require the planted pixel and execution failures in both orders.
    required_pixel_failures = {
        "path": ("same paths and explicit strength", "legacy fields absent",
                 "changed stable default", "different bytes at same source path"),
        "implicit": ("same paths and explicit strength", "different graph filenames",
                     "mode-specific defaults", "changed stable default"),
    }
    for name, required_cases in required_pixel_failures.items():
        pixels, reuse = results[name]
        for order in ("A/B/A", "B/A/B"):
            for case in required_cases:
                if (case, order) not in pixels:
                    return 1
            if ("equal pixels still exercise both modes", order) not in reuse:
                return 1
    return int(any(results["scoped"]))


if __name__ == "__main__":
    raise SystemExit(main())
