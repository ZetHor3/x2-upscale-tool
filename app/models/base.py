"""Base class for all upscaler backends."""

from abc import ABC, abstractmethod
from PIL import Image


class BaseUpscaler(ABC):
    """Abstract upscaler backend."""

    name: str = "base"
    display_name: str = "Base"

    @property
    @abstractmethod
    def device(self) -> str:
        """Device string: 'cpu', 'cuda:0', etc."""
        ...

    @property
    @abstractmethod
    def available(self) -> bool:
        """Whether this backend is usable (deps installed, model loaded)."""
        ...

    @property
    def supports_tiling(self) -> bool:
        """Whether the backend can tile large images to avoid OOM."""
        return False

    def get_options(self) -> dict:
        """Return a schema of tuneable options for the UI."""
        return {}

    def set_options(self, **kwargs) -> None:
        """Apply user-provided options."""
        pass

    @abstractmethod
    def upscale(self, image: Image.Image, scale: float = 2.0) -> Image.Image:
        """Upscale a single image."""
        ...

    def upscale_tiled(
        self,
        image: Image.Image,
        scale: float = 2.0,
        tile_size: int = 512,
        overlap: int = 32,
    ) -> Image.Image:
        """Fallback: upscale by tiling (overridden by backends that support it natively)."""
        from .tile_processor import process_tiled

        return process_tiled(self, image, scale, tile_size, overlap)
