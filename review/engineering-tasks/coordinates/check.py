"""Independent labeled-raster oracle and fault checks. Python standard library."""

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from candidate import map_to_source


SOURCE_SIZE = (37, 23)
CROP = (4, 3, 32, 21)
WITNESSES = {"red": (5, 4), "amber": (11, 15), "mint": (25, 7), "blue": (30, 19)}
EXPECTED = {label: (x + 0.5, y + 0.5) for label, (x, y) in WITNESSES.items()}
TOLERANCE = 0.01


def oriented_raster(orientation):
    """Store the original pixel address in each cell and rearrange the cells."""
    width, height = SOURCE_SIZE
    grid = [[(x, y) for x in range(width)] for y in range(height)]
    left, top, right, bottom = CROP
    grid = [row[left:right] for row in grid[top:bottom]]
    if orientation == "flip_x":
        return [row[::-1] for row in grid]
    if orientation == "cw90":
        return list(zip(*grid[::-1]))
    return grid


def rendered_points(grid, target):
    """Find labeled source cells in the transformed array, then resize centers."""
    labels = {point: label for label, point in WITNESSES.items()}
    width, height = len(grid[0]), len(grid)
    return {
        labels[point]: ((col + 0.5) * target[0] / width, (row + 0.5) * target[1] / height)
        for row, cells in enumerate(grid)
        for col, point in enumerate(cells)
        if point in labels
    }


def assess(returned):
    rows = {}
    for label, expected in EXPECTED.items():
        got = returned.get(label)
        valid = (
            isinstance(got, (list, tuple)) and len(got) == 2
            and all(isinstance(v, (int, float)) and math.isfinite(v) for v in got)
        )
        error = [abs(a - b) for a, b in zip(got, expected)] if valid else None
        rows[label] = {"expected": expected, "returned": got if valid else None,
                       "axis_error": error, "pass": valid and max(error) <= TOLERANCE}
    return {"pass": set(returned) == set(EXPECTED) and all(r["pass"] for r in rows.values()),
            "witnesses": rows}


def scale_swap_return(grid, target, points):
    # Read the oriented basis from adjacent source addresses in the raster.
    # Use the height ratio on raster x and the width ratio on raster y.
    origin = grid[0][0]
    right = tuple(a - b for a, b in zip(grid[0][1], origin))
    down = tuple(a - b for a, b in zip(grid[1][0], origin))
    wrong_x = len(grid) / target[1]
    wrong_y = len(grid[0]) / target[0]
    return {
        label: tuple(start + 0.5 + (x * wrong_x - 0.5) * dx + (y * wrong_y - 0.5) * dy
                     for start, dx, dy in zip(origin, right, down))
        for label, (x, y) in points.items()
    }


def check_view(orientation, grid, target):
    points = rendered_points(grid, target)
    candidate = assess(map_to_source(points, CROP, orientation, target))
    # Feed the checker known answers and planted faults independently of the starter.
    probes = {"unchanged": (EXPECTED, True)}
    for name, dx, dy in [("shift_x", 1, 0), ("shift_y", 0, 1), ("shift_xy", 1, 1)]:
        probes[name] = ({k: (x + dx, y + dy) for k, (x, y) in EXPECTED.items()}, False)
    switched = EXPECTED.copy()
    switched["amber"], switched["blue"] = switched["blue"], switched["amber"]
    probes["exchange_labels"] = (switched, False)
    equal_scale = len(grid[0]) * target[1] == len(grid) * target[0]
    probes["swap_scale_factors"] = (scale_swap_return(grid, target, points), equal_scale)
    controls = {}
    for name, (output, should_pass) in probes.items():
        result = assess(output)
        controls[name] = {
            "expected_accept": should_pass, "actual_accept": result["pass"],
            "failing_labels": [k for k, v in result["witnesses"].items() if not v["pass"]],
            "pass": result["pass"] == should_pass,
        }
    return {"orientation": orientation, "target": target, "view_centers": points,
            "candidate": candidate, "controls": controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print every witness and control.")
    args = parser.parse_args()
    results = []
    for orientation in ("identity", "flip_x", "cw90"):
        grid = oriented_raster(orientation)
        for target in ((len(grid[0]), len(grid)), (19, 13)):
            results.append(check_view(orientation, grid, target))
    passing = sum(row["candidate"]["pass"] for row in results)
    controls = [c["pass"] for row in results for c in row["controls"].values()]
    if args.json:
        print(json.dumps({"tolerance_source_px": TOLERANCE, "cases": results}, indent=2))
    else:
        for row in results:
            failed = [k for k, v in row["candidate"]["witnesses"].items() if not v["pass"]]
            status = "PASS" if row["candidate"]["pass"] else "FAIL"
            print(f'{status:4} {row["orientation"]:8} {row["target"]}  {", ".join(failed)}')
        print(f"Mapper {passing}/{len(results)} views. Checker {sum(controls)}/{len(controls)} controls.")
    return 0 if passing == len(results) and all(controls) else 1


if __name__ == "__main__":
    sys.exit(main())
