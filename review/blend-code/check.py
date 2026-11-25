"""Offline public checks for the object-repair coding exercise."""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from candidate import blend


@dataclass
class Case:
    source: np.ndarray
    proposal: np.ndarray
    alpha: np.ndarray
    truth: np.ndarray
    decal: np.ndarray
    line: np.ndarray


def make_case(kind, seed):
    rng = np.random.default_rng(seed)
    h, w = rng.integers(89, 117), rng.integers(125, 161)
    y, x = np.mgrid[:h, :w]
    cx, cy = w * rng.uniform(.44, .56), h * rng.uniform(.43, .56)
    u, v = (x - cx) / (w * .32), (y - cy) / (h * .35)
    radius = np.sqrt((u + .14 * v) ** 2 + v ** 2)
    alpha = np.clip((1 - radius) / .27, 0, 1).astype(np.float32)
    grain = 3 * np.sin(.69 * y + .075 * x) + rng.normal(0, 1.2, (h, w))
    ground = rng.uniform([131, 148, 102], [185, 182, 158])
    surface = ground + (grain + 8 * x / w - 6 * y / h)[..., None]
    line = np.abs(y - cy - .17 * (x - cx)) < 1.7
    surface[line] -= np.array([75, 52, 36])  # Printed registration stripe.
    truth = (surface / 255).astype(np.float32)
    decal = (radius < .965) & (radius > .42) & (u < .54) & (v > -.63)
    source = truth.copy()
    source[decal] = (.28 * truth[decal] + .72 * np.array([.71, .20, .13]))
    proposal = truth.copy()
    if kind == 'cast':
        # The replacement is aligned but rendered under a different color balance.
        shift = rng.uniform([9, -15, 6], [17, -7, 12])
        drift = ((x - cx) / w + .35 * (y - cy) / h)[..., None] * [4, 3, -3]
        proposal = (truth + (shift + drift) / 255).astype(np.float32)
    elif kind == 'print':
        # Here the original stripe is legitimate. The damage is off the stripe.
        decal &= np.abs(y - cy - .17 * (x - cx)) > 7
        source = truth.copy()
        source[decal] = .45 * truth[decal] + .55 * np.array([.73, .27, .13])
    elif kind != 'decal':
        raise ValueError(kind)
    return Case(source, proposal, alpha, truth, decal, line)


def feather(source, proposal, alpha):
    result = source.copy()
    active = alpha > 0
    result[active] += alpha[active, None] * (proposal[active] - source[active])
    return result


def paste(source, proposal, alpha):
    return np.where(alpha[..., None] > 0, proposal, source)


def checked(fn, c):
    source, proposal, alpha = (a.copy() for a in (c.source, c.proposal, c.alpha))
    result = fn(source, proposal, alpha)
    if not all(np.array_equal(a, b) for a, b in zip(
        (source, proposal, alpha), (c.source, c.proposal, c.alpha)
    )):
        raise ValueError('modified at least one input')
    if not isinstance(result, np.ndarray) or result.shape != source.shape or result.dtype != np.float32:
        raise ValueError('expected an H x W x 3 float32 array')
    if not np.isfinite(result).all() or result.min() < 0 or result.max() > 1:
        raise ValueError('output must be finite and within [0, 1]')
    if not np.array_equal(result[alpha == 0], c.source[alpha == 0]):
        raise ValueError('changed protected pixels')
    return result


def mae(actual, expected, region):
    return float(np.abs(actual[region] - expected[region]).mean() * 255)


def scores(fn, seed):
    values = {}
    for kind in ('decal', 'cast', 'print'):
        c = make_case(kind, seed)
        out = checked(fn, c)
        collar = (c.alpha > 0) & (c.alpha < 1)
        if kind == 'decal':
            values['decal_collar'] = mae(out, c.truth, c.decal & collar)
        elif kind == 'cast':
            values['cast_interior'] = mae(out, c.truth, c.alpha == 1)
            values['cast_collar'] = mae(out, c.truth, collar)
        else:
            # Measure contrast across adjacent pixels straddling the actual printed line.
            edges = (c.line[1:] != c.line[:-1]) & (c.alpha[1:] > 0) & (c.alpha[:-1] > 0)
            values['print_contrast'] = mae(np.diff(out, axis=0), np.diff(c.truth, axis=0), edges)
            values['print_good_pixels'] = mae(out, c.truth, (c.alpha > 0) & ~c.decal)
            c.alpha = np.zeros_like(c.alpha)
            checked(fn, c)
    return values


def ambiguity(fn):
    # Opaque shipping sticker hides whether a printed mark existed underneath.
    h, w = 43, 55
    truth_blank = np.full((h, w, 3), .69, dtype=np.float32)
    truth_ink = truth_blank.copy()
    mark = np.zeros((h, w), bool)
    mark[20:23, 24:34] = True
    truth_ink[mark] = .29
    alpha = np.zeros((h, w), np.float32)
    alpha[14:29, 16:41] = 1
    source = truth_blank.copy()
    source[alpha > 0] = [.25, .36, .53]
    c = Case(source, truth_blank.copy(), alpha, truth_blank, mark, mark)
    out = checked(fn, c)
    return {'blank_world': mae(out, truth_blank, mark), 'ink_world': mae(out, truth_ink, mark),
            'best_possible_mean_lower_bound': mae(truth_ink, truth_blank, mark) / 2}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=731, help='first of three consecutive seeds')
    args = parser.parse_args()
    report = {}
    individual = {}
    for name, method in [('feather', feather), ('paste', paste), ('candidate', blend)]:
        rows = [scores(method, seed) for seed in range(args.seed, args.seed + 3)]
        individual[name] = rows
        report[name] = {metric: float(np.mean([row[metric] for row in rows])) for metric in rows[0]}
    treatment = ('decal_collar', 'cast_interior', 'cast_collar')
    def composite(row):
        return sum(row[m] for m in treatment) / len(treatment)

    # Compare each seed separately, so a strong fixture cannot hide a failing one.
    failures = []
    for index, candidate in enumerate(individual['candidate']):
        f, p = individual['feather'][index], individual['paste'][index]
        limits = {'decal_collar': .45 * f['decal_collar'],
                  'cast_interior': .55 * p['cast_interior'],
                  'cast_collar': .65 * min(f['cast_collar'], p['cast_collar']),
                  'print_contrast': 2.0, 'print_good_pixels': 1.0,
                  'composite': .65 * min(composite(f), composite(p))}
        for metric, limit in limits.items():
            score = composite(candidate) if metric == 'composite' else candidate[metric]
            if score > limit:
                failures.append({'seed': args.seed + index, 'metric': metric,
                                 'score': round(score, 3), 'maximum': round(limit, 3)})
    for row in report.values():
        row['composite'] = composite(row)
    report['unobservable_pair'] = ambiguity(blend)
    report['failures'] = failures
    print(json.dumps(report, indent=2))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
