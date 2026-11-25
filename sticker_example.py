"""A controlled example of a residual outline in a local photo edit."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def make_example():
    # We build the clean paper first so the exact hidden surface is known.
    y, x = np.mgrid[:144, :220]
    grain = np.random.default_rng(218).normal(0, 1.4, x.shape)
    shading = (x - 110) * 0.045 + (y - 72) * 0.04
    lines = np.where(y % 18 == 8, -17, 0)
    paper = np.array([204, 211, 206]) + (grain + shading + lines)[..., None]
    distance = np.sqrt(((x - 111) / 52) ** 2 + ((y - 72) / 37) ** 2)
    mask = distance <= 1
    rim = (distance > 0.83) & mask
    decal = np.empty_like(paper)
    decal[:] = [234, 146, 58]
    decal += (shading + grain)[..., None]
    decal[rim] -= 36
    source = np.where(mask[..., None], decal, paper)

    # Copy the sticker's observed brightness contrast into the neutral fill.
    # This intentionally makes a bad guide. The controlled proposal echoes it.
    luma = source @ np.array([0.2126, 0.7152, 0.0722])
    residual = luma - np.median(luma[distance < 0.7])
    guide = paper + np.where(mask, residual * 0.75, 0)[..., None]

    # In the other path the proposal is exactly correct. The compositor
    # gives the source weight again only near the edge of the edit.
    source_weight = np.where(mask, np.clip((distance - 0.83) / 0.17, 0, 1), 0)
    blend = paper + source_weight[..., None] * (source - paper)
    return paper, source, mask, rim, guide, blend


def rgb(array):
    return np.clip(array.round(), 0, 255).astype(np.uint8)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write a local comparison PNG")
    args = parser.parse_args()
    paper, source, mask, rim, guide, blend = make_example()
    runs = [
        ("A. Structure in guide", (source, guide, guide, guide)),
        ("B. Edge restored by blend", (source, paper, paper, blend)),
    ]
    reference = rgb(paper).astype(float)
    board = Image.new("RGB", (950, 418), "#f7f6f1")
    draw = ImageDraw.Draw(board)
    for col, label in enumerate(("Source", "Guide", "Proposal", "Final composite")):
        draw.text((16 + col * 234, 8), label, fill="#182b36")
    for row, (name, images) in enumerate(runs):
        top = 35 + row * 190
        draw.text((16, top), name, fill="#182b36")
        errors = []
        for col, image in enumerate(images):
            values = rgb(image)
            assert np.array_equal(values[~mask], reference[~mask])
            error = np.abs(values.astype(float) - reference)[rim].mean()
            errors.append(error)
            left = 16 + col * 234
            board.paste(Image.fromarray(values), (left, top + 19))
            draw.text((left, top + 166), f"Rim error {error:.1f}", fill="#182b36")
        print(name, " / ".join(f"{value:.1f}" for value in errors))
    if args.output:
        board.save(args.output)


if __name__ == "__main__":
    main()
