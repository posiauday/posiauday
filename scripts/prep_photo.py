"""Prep a photo for ASCII conversion.

    python scripts/prep_photo.py source-photo.png

Writes source-prepped.png (grayscale) and source-mask.png (subject mask).
- Transparent PNGs (like a GitHub avatar cut-out) use their alpha channel as the mask.
- Otherwise rembg is used to cut out the subject if it is installed.
- Local contrast: OpenCV CLAHE if installed, else a numpy/PIL fallback.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent


def cut_out(img: Image.Image) -> Image.Image:
    if img.mode in ("RGBA", "LA") and img.getchannel("A").getextrema()[0] < 250:
        return img.convert("RGBA")
    try:
        from rembg import remove  # type: ignore
        print("removing background with rembg...")
        return remove(img.convert("RGB")).convert("RGBA")
    except ImportError:
        print("rembg not installed and photo has no transparency; keeping background")
        return img.convert("RGBA")


def local_contrast(gray: np.ndarray) -> np.ndarray:
    try:
        import cv2  # type: ignore
        return cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)
    except ImportError:
        img = Image.fromarray(gray)
        img = ImageOps.autocontrast(img, cutoff=1)
        img = img.filter(ImageFilter.UnsharpMask(radius=6, percent=220, threshold=2))
        return np.asarray(img)


def main() -> None:
    src = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "source-photo.png")
    rgba = cut_out(Image.open(src))
    alpha = np.asarray(rgba.getchannel("A"))
    gray = np.asarray(rgba.convert("L"))
    gray = local_contrast(gray)
    # composite onto pure white so the background maps to the blank end of the ramp
    a = alpha.astype(np.float32) / 255.0
    out = (gray * a + 255 * (1 - a)).astype(np.uint8)
    Image.fromarray(out).save(ROOT / "source-prepped.png")
    Image.fromarray(alpha).save(ROOT / "source-mask.png")
    print("wrote source-prepped.png + source-mask.png")


if __name__ == "__main__":
    main()
