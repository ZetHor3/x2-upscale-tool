"""Real-ESRGAN upscaler — best quality, GPU-accelerated, с авто-загрузкой модели."""

import os
import sys
import logging
from pathlib import Path
from urllib.request import urlretrieve
from PIL import Image
from .base import BaseUpscaler

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent.parent.parent / "models/realesrgan"
KNOWN_MODELS = {
    "RealESRGAN_x4plus.pth": "4x real-world (photo) — 67 MB",
}

MODEL_URLS = {
    "RealESRGAN_x4plus.pth": (
        "https://github.com/xinntao/Real-ESRGAN/"
        "releases/download/v0.1.0/RealESRGAN_x4plus.pth"
    ),
}

SUPPORTED_SCALES = {2, 3, 4}


class RealEsrganUpscaler(BaseUpscaler):
    """Real-ESRGAN upscaler via the `realesrgan` package (CUDA).

    Модель скачивается автоматически при первом использовании.
    """

    name = "realesrgan"
    display_name = "Real-ESRGAN (GPU)"

    def __init__(self, device: str | None = None):
        self._device = device or "cuda:0"
        self._model_name = "RealESRGAN_x4plus.pth"
        self._model = None
        self._loaded = False
        self._load_error: str | None = None
        self._download_progress_callback = None

    @property
    def device(self) -> str:
        return self._device

    @property
    def available(self) -> bool:
        if not self._loaded:
            self._load_model()
        return self._model is not None

    @property
    def supports_tiling(self) -> bool:
        return True

    def set_download_callback(self, callback):
        """Set a callback(downloaded_mb, total_mb) for download progress."""
        self._download_progress_callback = callback

    def get_options(self) -> dict:
        available_models = list(KNOWN_MODELS.keys())
        return {
            "model": {
                "type": "choice",
                "label": "Model",
                "value": self._model_name,
                "choices": available_models,
            }
        }

    def set_options(self, **kwargs) -> None:
        if "model" in kwargs:
            model_name = kwargs["model"]
            if model_name not in KNOWN_MODELS:
                raise ValueError(f"Unknown model '{model_name}'. Available: {list(KNOWN_MODELS.keys())}")
            self._model_name = model_name
            self._loaded = False
            self._model = None

    def _download_model(self, model_path: Path) -> bool:
        """Download model from GitHub releases with progress bar."""
        if model_path.exists():
            return True

        url = MODEL_URLS.get(self._model_name)
        if not url:
            self._load_error = f"No download URL for {self._model_name}"
            return False

        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Downloading {self._model_name}...")

        tmp_path = model_path.with_suffix(model_path.suffix + ".tmp")

        try:
            # Get file size first
            import urllib.request
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=10) as resp:
                total_size = int(resp.headers.get("Content-Length", 0))
            total_mb = total_size / (1024 * 1024)

            def _report(count, block_size, total_size):
                downloaded = count * block_size
                pct = min(100, downloaded * 100 / total_size) if total_size > 0 else 0
                d_mb = downloaded / (1024 * 1024)
                bar_len = 25
                filled = int(bar_len * pct / 100)
                bar = "█" * filled + "░" * (bar_len - filled)
                sys.stderr.write(f"\r  Загрузка {self._model_name}: {bar} {pct:.0f}% ({d_mb:.1f}/{total_mb:.1f} MB)")
                sys.stderr.flush()
                if self._download_progress_callback:
                    self._download_progress_callback(d_mb, total_mb)

            urlretrieve(url, str(tmp_path), _report)
            os.rename(str(tmp_path), str(model_path))
            sys.stderr.write("\n")
            logger.info(f"Downloaded {self._model_name} to {model_path}")
            return True
        except Exception as e:
            logger.warning(f"Download failed: {e}")
            if tmp_path.exists():
                tmp_path.unlink()
            self._load_error = f"Download failed: {e}"
            return False

    def _load_model(self) -> None:
        """Load the Real-ESRGAN model. Auto-downloads if missing."""
        self._loaded = True
        try:
            import torch
            from realesrgan import RealESRGANer  # type: ignore
            from basicsr.archs.rrdbnet_arch import RRDBNet  # type: ignore
        except ImportError as e:
            missing = str(e).split("'")[1] if "'" in str(e) else str(e)
            self._load_error = (
                f"Не установлен пакет: {missing}. "
                f"Установи: pip install -r requirements-photo.txt"
            )
            return

        model_path = MODELS_DIR / self._model_name
        if not model_path.exists():
            if not self._download_model(model_path):
                return

        try:
            # Определяем scale модели по имени файла
            model_scale = 4 if "x4" in self._model_name.lower() else 2

            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=model_scale)
            upsampler = RealESRGANer(
                scale=model_scale,
                model_path=str(model_path),
                model=model,
                tile=0,
                tile_pad=10,
                pre_pad=0,
                half="fp16" if self._device != "cpu" else None,
                device=self._device,
            )
            self._model = upsampler
        except Exception as e:
            self._load_error = f"Failed to load Real-ESRGAN: {e}"

    def upscale(self, image: Image.Image, scale: float = 2.0) -> Image.Image:
        if not self._loaded:
            self._load_model()
        if self._model is None:
            raise RuntimeError(f"Real-ESRGAN unavailable: {self._load_error}")

        import numpy as np

        img_np = np.array(image.convert("RGB"))
        output, _ = self._model.enhance(img_np, outscale=scale)
        return Image.fromarray(output)
