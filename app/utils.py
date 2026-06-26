"""Utility functions: file I/O, image loading, path handling."""

import os
import sys
import json
from pathlib import Path
from PIL import Image

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif", ".avif"}


def is_image(file_path: str | Path) -> bool:
    """Check if the file has a supported image extension."""
    ext = Path(file_path).suffix.lower()
    return ext in SUPPORTED_EXTENSIONS


def list_images(paths: list[str | Path]) -> list[Path]:
    """Filter a list of paths to supported image files."""
    result = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            for child in sorted(p.iterdir()):
                if child.is_file() and is_image(child):
                    result.append(child)
        elif p.is_file() and is_image(p):
            result.append(p)
    return result


def ensure_output_path(input_path: Path, output_path: str | Path | None = None, suffix: str = "_x2") -> Path:
    """
    Resolve the output path.
    If no output path is given, auto-generate one from the input path
    by inserting `suffix` before the extension.
    """
    if output_path:
        return Path(output_path)

    stem = input_path.stem
    ext = input_path.suffix
    return input_path.with_name(f"{stem}{suffix}{ext}")


def ensure_output_dir(path: Path) -> Path:
    """Create the parent directory if it doesn't exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def load_image(path: str | Path) -> Image.Image:
    """Load an image from disk, converting to RGB if needed."""
    img = Image.open(path)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "transparency" in img.info else "RGB")
    return img


def save_image(img: Image.Image, path: str | Path, quality: int = 95) -> None:
    """Save an image, choosing format from the extension."""
    path = Path(path)
    ext = path.suffix.lower()
    fmt = ext.lstrip(".").upper()
    if fmt == "JPG":
        fmt = "JPEG"

    kwargs: dict = {"format": fmt}
    if fmt == "JPEG":
        kwargs["quality"] = quality
        if img.mode == "RGBA":
            img = img.convert("RGB")
    elif fmt == "WEBP":
        kwargs["quality"] = quality
        if img.mode == "RGBA":
            kwargs["format"] = "WEBP"
            img = img.convert("RGBA")
    elif fmt == "PNG":
        if img.mode != "RGBA":
            img = img.convert("RGBA")

    img.save(path, **kwargs)
