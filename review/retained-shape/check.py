"""Synthetic woven-pouch benchmark. See README.md for inputs and pass criteria."""

import argparse
import importlib.util
from pathlib import Path

import numpy as np


def load_candidate(path):
    spec = importlib.util.spec_from_file_location("pouch_candidate", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.repair


def ridge(distance, width):
    return np.exp(-0.5 * (distance / width) ** 2)


def fixture(seed):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[:96, :144]
    cx, cy = rng.integers(65, 79), rng.integers(43, 52)
    dx, dy = x - cx, y - cy
    editable = (abs(dx) <= 25) & (abs(dy) <= 21)
    # Distance to a logo made of two raised loops. The actual relief occupies
    # a small subset of the editable rectangle and crosses genuine textile detail.
    skew = rng.uniform(-0.18, 0.18)
    d1 = np.hypot((dx+7)/13, (dy-skew*dx)/11) - 1
    d2 = np.hypot((dx-7)/11, (dy+2)/10) - 1
    height = np.maximum(ridge(d1, .11), ridge(d2, .12))
    relief = 24 * (0.8*np.gradient(height, axis=0) + np.gradient(height, axis=1))
    relief *= editable
    seam_y = cy + 2 + rng.uniform(-.035, .035)*dx + .7*np.sin(x/19)
    fold_y = cy - 10 + rng.uniform(-.05, .05)*dx + .8*np.cos(x/27)
    seam = y-seam_y
    fold = y-fold_y
    seam_light = 11*ridge(seam+.8, .85) - 15*ridge(seam-1, .8)
    thread = (1 + np.cos(2*np.pi*x/6))/2
    seam_light += 4*thread*ridge(seam, 1)
    fold_light = 16*ridge(fold+2, 2.8) - 15*ridge(fold-2, 2.6)
    phase = rng.uniform(0, 2*np.pi, 2)
    weave = (3.7*np.cos(2*np.pi*x/4+phase[0]) +
             3.1*np.cos(2*np.pi*y/3+phase[1]) +
             1.8*np.cos(np.pi*(x+y)))
    # Legitimate embossed belt fitting, outside every editable mask.
    buckle_dist = np.hypot((x-120)/9, (y-23)/7)-1
    buckle = 18*np.gradient(ridge(buckle_dist, .18), axis=0)
    surface = (seam_light + fold_light + weave + buckle + .045*x - .04*y +
               rng.normal(0, .3, x.shape))
    fabric = np.array([136, 124, 99]) + surface[..., None]

    def render(strength):
        return np.rint(fabric + strength*relief[..., None]).clip(0, 255).astype(np.uint8)

    clean, proposal = render(0), render(1)
    # A separately rendered, physically shallower emboss calibrates the scorer.
    # This is a simulated acquisition control, not a repair algorithm.
    shallow = render(.16)
    flat = proposal.copy()
    flat[editable] = np.median(proposal[editable], axis=0).astype(np.uint8)
    return proposal, editable, clean, shallow, flat, relief, seam, fold


def metrics(image, proposal, mask, clean, relief, seam, fold):
    if not isinstance(image, np.ndarray) or image.dtype != np.uint8 or image.shape != clean.shape:
        raise ValueError("repair() must return an RGB uint8 array with the input shape")
    actual = image.astype(float).mean(axis=2)
    truth = clean.astype(float).mean(axis=2)
    error = actual - truth
    color_error = image.astype(float) - clean.astype(float) - error[..., None]
    grad_error = np.abs(np.gradient(error, axis=0))
    logo = mask & (np.abs(relief) > 1)
    # Matched relief detects the specific paired highlights and shadows. MAE
    # on their support also penalizes inversion or substitution with a new edge.
    abs_relief = abs(np.dot(error[logo], relief[logo])/np.dot(relief[logo], relief[logo]))
    # A 3x3 box high-pass measures local cloth variation away from structural edges.
    smooth_error = sum(np.roll(error, (i, j), axis=(0, 1))
                       for i in (-1, 0, 1) for j in (-1, 0, 1))/9
    plain = mask & (abs(seam) > 4) & (abs(fold) > 6)
    return np.array([
        abs_relief, np.abs(error[logo]).mean(), grad_error[mask & (abs(seam) <= 2.5)].mean(),
        grad_error[mask & (abs(fold) <= 4)].mean(), np.abs((error-smooth_error)[plain]).mean(),
        np.abs(color_error[mask]).mean(), np.any(image[~mask] != proposal[~mask], axis=1).sum(),
    ])


NAMES = ("relief", "logo_mae", "seam_grad", "fold_grad", "weave_hp", "chroma", "outside_px")
LIMITS = np.array([.35, 2.5, 1.5, 1.4, 0.9, 0.5, 0])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=Path(__file__).with_name("candidate.py"))
    parser.add_argument("--seeds", type=int, nargs="+", default=[3, 19, 41])
    parser.add_argument("--board", type=Path, help="write a new binary PPM for the first seed")
    args = parser.parse_args()
    candidate = load_candidate(args.candidate.resolve())
    print("seed  output       " + "  ".join(NAMES))
    passed = True
    for index, seed in enumerate(args.seeds):
        proposal, mask, clean, shallow, flat, relief, seam, fold = fixture(seed)
        result = candidate(proposal.copy(), mask.copy())
        for name, image in [("recolor", proposal), ("shallow", shallow), ("flat", flat), ("candidate", result)]:
            scores = metrics(image, proposal, mask, clean, relief, seam, fold)
            ok = bool((scores <= LIMITS).all())
            print(f"{seed:>4}  {name:<9} " + "  ".join(f"{s:8.3f}" for s in scores) + ("  PASS" if ok else "  FAIL"))
            if name == "candidate":
                passed &= ok
        if index == 0 and args.board:
            board = np.concatenate([proposal, result, clean], axis=1)
            board = board.repeat(3, axis=0).repeat(3, axis=1)
            with args.board.open("xb") as stream:
                stream.write(f"P6\n{board.shape[1]} {board.shape[0]}\n255\n".encode())
                stream.write(board.tobytes())
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
