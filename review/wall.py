"""Create synthetic wall comparisons locally. Requires NumPy and Pillow."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="New directory for local review boards")
    args = parser.parse_args()
    y, x = np.mgrid[:180, :260]
    illumination = 17 * x / 259 + 6 * np.sin(y / 138 + x / 170)
    paint = np.array([167, 182, 177])
    clean = paint + illumination[..., None]
    stepped = paint + (np.round(illumination / 4) * 4)[..., None]
    offset = np.clip((x - (104 + 6 * np.sin(y / 76))) / 10, 0, 1)
    seam = clean + 5 * offset[..., None]
    ambiguous = paint + (4 * np.floor(illumination / 4))[..., None]
    # Another construction reaches the same pixels by applying a spatial
    # exposure correction to a smooth input. Finals alone cannot discriminate.
    correction = 4 * np.floor(illumination / 4) - illumination
    as_rgb = lambda a: np.uint8(np.clip(np.rint(a), 0, 255))
    assert np.array_equal(as_rgb(ambiguous), as_rgb(clean + correction[..., None]))
    images = (clean, seam, stepped, ambiguous, clean + correction[..., None])
    directory = args.directory
    directory.mkdir(parents=True, exist_ok=False)
    for name, values in zip(("Control", "A", "B", "C", "D"), images):
        frame = Image.fromarray(as_rgb(values))
        frame.save(directory / f"{name}.png")
        frame.save(directory / f"{name}.jpg", quality=78, subsampling=2)
    for extension in ("png", "jpg"):
        board = Image.new("RGB", (794, 408), "#25292a")
        draw = ImageDraw.Draw(board)
        for i, label in enumerate(("Control", "A", "B", "C", "D")):
            left, top = (i % 3) * 264, (i // 3) * 204
            draw.text((left + 3, top + 3), label, fill="white")
            with Image.open(directory / f"{label}.{extension}") as image:
                board.paste(image, (left, top + 22))
        board.save(directory / f"board-{extension}.png")
    print("Start with board-png.png, then compare board-jpg.png.")


if __name__ == "__main__":
    main()
