"""Score a canonical browser rendering of shirt.svg after a blind verdict."""
import argparse

import numpy as np
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board")
    args = parser.parse_args()
    with Image.open(args.board) as image:
        if image.size != (800, 324):
            parser.error("Expected an 800 × 324 board without margins.")
        board = np.asarray(image.convert("RGB"), dtype=float)
    if not np.all(board[310, 8] == (37, 41, 42)) or not np.all(board[309, 8] == (115, 123, 120)):
        parser.error("The detail strip is not at the expected coordinates.")
    patches = [board[202:310, x:x+184] for x in (8, 208, 408, 608)]
    ref = patches[0]
    weights = np.array([0.2126, 0.7152, 0.0722])
    for label, patch in zip("ABC", patches[1:]):
        diff = patch - ref
        luma_diff = diff @ weights
        gradients = [np.abs(np.diff(luma_diff, axis=axis)).mean() for axis in (0, 1)]
        print(f"{label}: mean channel error {np.abs(diff).mean():.2f}; mean gradient error {np.mean(gradients):.2f}")


if __name__ == "__main__":
    main()
