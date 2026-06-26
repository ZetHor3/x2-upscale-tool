"""Upscaling model backends.

Only backends that can be safely imported (no hard torch dependency at module level)
are registered here. Real-ESRGAN / PyTorch backends are tried lazily.
"""

from .._compat import patch_basicsr

patch_basicsr()

from .pil_upscaler import PilUpscaler
from .ncnn_upscaler import NcnnUpscaler

BACKENDS: dict[str, type] = {
    "pil": PilUpscaler,
    "ncnn": NcnnUpscaler,
}

# Real-ESRGAN Python backend (needs torch + realesrgan — optional)
try:
    from .realesrgan_upscaler import RealEsrganUpscaler
    BACKENDS["realesrgan"] = RealEsrganUpscaler
except ImportError:
    pass


def list_backends() -> list[str]:
    """Return available backend names."""
    return list(BACKENDS.keys())


def get_backend(name: str, device: str | None = None):
    """Instantiate a backend by name."""
    if name not in BACKENDS:
        names = ", ".join(BACKENDS)
        raise ValueError(f"Unknown backend '{name}'. Available: {names}")
    return BACKENDS[name](device=device)
