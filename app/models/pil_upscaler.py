"""PIL-based upscaler — fast CPU resize with multiple filters."""

from PIL import Image, ImageFilter
from .base import BaseUpscaler


INTERPOLATION_MAP = {
    "nearest": Image.NEAREST,
    "bilinear": Image.BILINEAR,
    "bicubic": Image.BICUBIC,
    "lanczos": Image.LANCZOS,
    "box": Image.BOX,
    "hamming": Image.HAMMING,
}

DEFAULT_FILTER = "lanczos"


class PilUpscaler(BaseUpscaler):
    name = "pil"
    display_name = "PIL (CPU)"

    def __init__(self, device: str | None = None):
        self._filter_name = DEFAULT_FILTER
        self._filter = INTERPOLATION_MAP[DEFAULT_FILTER]

    @property
    def device(self) -> str:
        return "cpu"

    @property
    def available(self) -> bool:
        return True

    @property
    def supports_tiling(self) -> bool:
        return False

    def set_filter(self, filter_name: str) -> None:
        if filter_name not in INTERPOLATION_MAP:
            raise ValueError(
                f"Unknown filter '{filter_name}'. "
                f"Available: {', '.join(INTERPOLATION_MAP)}"
            )
        self._filter_name = filter_name
        self._filter = INTERPOLATION_MAP[filter_name]

    def get_filter(self) -> str:
        return self._filter_name

    def get_options(self) -> dict:
        return {
            "filter": {
                "type": "choice",
                "label": "Interpolation filter",
                "value": self._filter_name,
                "choices": list(INTERPOLATION_MAP.keys()),
            }
        }

    def set_options(self, **kwargs) -> None:
        if "filter" in kwargs:
            self.set_filter(kwargs["filter"])

    def upscale(self, image: Image.Image, scale: float = 2.0) -> Image.Image:
        w, h = image.size
        new_w = max(1, round(w * scale))
        new_h = max(1, round(h * scale))
        return image.resize((new_w, new_h), self._filter)
