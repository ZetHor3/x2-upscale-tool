"""Tile-based processing for memory-efficient upscaling of large images."""

from PIL import Image
import math


def process_tiled(upscaler, image: Image.Image, scale: float, tile_size: int = 512, overlap: int = 32) -> Image.Image:
    """
    Split a large image into tiles, upscale each tile independently,
    then stitch back together.

    Args:
        upscaler: An upscaler backend with .upscale(img, scale) -> img
        image: PIL Image
        scale: upscaling factor
        tile_size: tile size in original-image pixels (before scaling)
        overlap: overlap in original-image pixels to avoid seam artifacts

    Returns:
        Combined upscaled PIL Image
    """
    w, h = image.size

    if w <= tile_size and h <= tile_size:
        return upscaler.upscale(image, scale)

    stride = tile_size - overlap
    if stride <= 0:
        stride = tile_size // 2

    cols = max(1, math.ceil((w - tile_size) / stride) + 1)
    rows = max(1, math.ceil((h - tile_size) / stride) + 1)

    scaled_w = round(w * scale)
    scaled_h = round(h * scale)

    result = Image.new("RGBA" if image.mode == "RGBA" else "RGB", (scaled_w, scaled_h))
    weight_sum = Image.new("L", (scaled_w, scaled_h))

    for row in range(rows):
        for col in range(cols):
            x = min(col * stride, w - tile_size)
            y = min(row * stride, h - tile_size)

            tile = image.crop((x, y, x + tile_size, y + tile_size))
            upscaled = upscaler.upscale(tile, scale)

            dst_x = round(x * scale)
            dst_y = round(y * scale)
            dst_w = upscaled.width
            dst_h = upscaled.height

            # Feather mask for smooth blending
            mask = _make_feather_mask(dst_w, dst_h, round(overlap * scale))
            result.paste(upscaled, (dst_x, dst_y), mask)
            weight_sum.paste(
                Image.new("L", (dst_w, dst_h), 255),
                (dst_x, dst_y),
                mask,
            )

    # Normalize by weight
    weight_sum = weight_sum.point(lambda v: 255 if v < 1 else 255 * 255 // v)
    result = Image.composite(
        result,
        Image.new(result.mode, result.size),
        weight_sum,
    )
    return result


def _make_feather_mask(w: int, h: int, feather: int) -> Image.Image:
    """Create a linear gradient mask for blending tile edges."""
    from PIL import ImageDraw

    mask = Image.new("L", (w, h), 255)
    if feather <= 0:
        return mask

    draw = ImageDraw.Draw(mask)
    for i in range(min(feather, w // 2)):
        alpha = round(255 * i / feather)
        draw.rectangle([i, 0, i, h], fill=alpha)
        draw.rectangle([w - 1 - i, 0, w - 1 - i, h], fill=alpha)
    for i in range(min(feather, h // 2)):
        alpha = round(255 * i / feather)
        draw.rectangle([0, i, w, i], fill=alpha)
        draw.rectangle([0, h - 1 - i, w, h - 1 - i], fill=alpha)
    return mask
