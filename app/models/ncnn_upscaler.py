"""Real-ESRGAN ncnn Vulkan backend — использует realesrgan-ncnn-vulkan.exe.

Берёт уже установленный бинарник из D:/2026/realesrgan-full/
(или из paths.json / %APPDATA%/x2-upscale/config.json).
"""

import os
import sys
import subprocess
import tempfile
import json
import logging
from pathlib import Path
from PIL import Image

from .base import BaseUpscaler

logger = logging.getLogger(__name__)

# ── Пути ────────────────────────────────────────────────────────


def _app_root() -> Path:
    """Вернуть корень проекта (работает и в .exe через PyInstaller)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent.parent


# Встроенный бинарник (идёт вместе с проектом)
BUNDLED_BINARY = _app_root() / "bin" / "ncnn" / "realesrgan-ncnn-vulkan.exe"
BUNDLED_MODELS = _app_root() / "bin" / "ncnn" / "models"

# Запасные пути (установленные пользователем ранее)
FALLBACK_PATHS = [
    Path("D:/2026/realesrgan-full/realesrgan-ncnn-vulkan.exe"),
    Path("D:/2026/realesrgan/realesrgan-ncnn-vulkan.exe"),
]

NCNN_MODEL_NAMES = {
    "realesr-animevideov3": "AnimeVideoV3 (best for animation/claymation)",
    "realesrgan-x4plus": "Real-ESRGAN x4plus (general photos)",
    "realesrgan-x4plus-anime": "Real-ESRGAN x4plus-anime",
}

SUPPORTED_SCALES = {2, 3, 4}


def _find_binary() -> Path | None:
    """Find the realesrgan-ncnn-vulkan.exe — bundled first, then fallback paths."""
    # Сначала встроенный бинарник
    if BUNDLED_BINARY.exists():
        return BUNDLED_BINARY
    # Потом системные пути (D:/2026 и т.д.)
    for p in FALLBACK_PATHS:
        if p.exists():
            return p
    # Попробовать в PATH
    for dir_ in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(dir_) / "realesrgan-ncnn-vulkan.exe"
        if candidate.exists():
            return candidate
    return None


def _models_dir(binary_path: Path) -> Path:
    """Models ищем: bundled, рядом с бинарником, на уровень выше."""
    # Сначала встроенная папка models/
    if BUNDLED_MODELS.is_dir():
        return BUNDLED_MODELS
    # Потом рядом с бинарником
    parent = binary_path.parent
    candidate = parent / "models"
    if candidate.is_dir():
        return candidate
    # Потом на уровень выше
    candidate = parent.parent / "models"
    if candidate.is_dir():
        return candidate
    return parent / "models"


class NcnnUpscaler(BaseUpscaler):
    """Real-ESRGAN ncnn Vulkan backend.

    Использует realesrgan-ncnn-vulkan.exe через subprocess.
    Поддерживает модели animevideov3 (x2/x3/x4) и x4plus.
    """

    name = "ncnn"
    display_name = "Real-ESRGAN ncnn (Vulkan)"

    def __init__(self, device: str | None = None):
        self._binary_path: Path | None = _find_binary()
        self._model_name = "realesr-animevideov3"
        self._tile_size = 256
        self._tta = False  # TTA mode (slower but better)
        self._device_str = device or "vulkan"
        self._loaded = False

        # Найдём models/ папку
        if self._binary_path:
            self._models_path = _models_dir(self._binary_path)
        else:
            self._models_path = Path("models")

    @property
    def device(self) -> str:
        return self._device_str

    @property
    def available(self) -> bool:
        return self._binary_path is not None and self._binary_path.exists()

    @property
    def supports_tiling(self) -> bool:
        return True  # бинарник сам поддерживает tiling через -t

    def get_options(self) -> dict:
        return {
            "tile_size": {
                "type": "int",
                "label": "Tile size",
                "value": self._tile_size,
                "min": 128,
                "max": 1024,
                "step": 64,
            },
            "tta": {
                "type": "bool",
                "label": "TTA (higher quality, slower)",
                "value": self._tta,
            },
        }

    def set_options(self, **kwargs) -> None:
        if "model" in kwargs:
            m = kwargs["model"]
            if m in NCNN_MODEL_NAMES:
                self._model_name = m
        if "tile_size" in kwargs:
            self._tile_size = int(kwargs["tile_size"])
        if "tta" in kwargs:
            self._tta = bool(kwargs["tta"])

    def upscale(self, image: Image.Image, scale: float = 2.0) -> Image.Image:
        if not self.available:
            raise RuntimeError(
                "realesrgan-ncnn-vulkan.exe not found. "
                "Download from https://github.com/xinntao/Real-ESRGAN/releases"
            )

        # Округляем scale до 2, 3, 4
        scale_int = min(SUPPORTED_SCALES, key=lambda x: abs(x - scale))

        with tempfile.TemporaryDirectory(prefix="ncnn_upscale_") as tmpdir:
            input_path = Path(tmpdir) / "input.png"
            output_path = Path(tmpdir) / "output.png"

            # Сохраняем входное изображение
            image.save(str(input_path), format="PNG")

            # Собираем команду
            cmd = [
                str(self._binary_path),
                "-i", str(input_path),
                "-o", str(output_path),
                "-s", str(scale_int),
                "-n", self._model_name,
                "-t", str(self._tile_size),
            ]

            # Флаг -x для максимального качества (только animevideov3)
            if self._model_name == "realesr-animevideov3":
                cmd.append("-x")

            # TTA mode (test-time augmentation)
            if self._tta:
                cmd.append("-x")  # TTA включается тем же -x для realesrgan-x4plus

            logger.info(f"Running: {' '.join(cmd)}")
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if proc.returncode != 0:
                error_msg = (proc.stderr or proc.stdout or "Unknown error")[:500]
                raise RuntimeError(
                    f"realesrgan-ncnn-vulkan failed (exit {proc.returncode}): {error_msg}"
                )

            if not output_path.exists():
                raise RuntimeError("Output file was not created by realesrgan-ncnn-vulkan")

            # Загружаем результат
            result = Image.open(str(output_path)).convert("RGBA" if image.mode == "RGBA" else "RGB")
            return result

    def upscale_directory(
        self,
        input_dir: str | Path,
        output_dir: str | Path,
        scale: int = 2,
    ) -> int:
        """Пакетная обработка всей папки сразу (быстрее, чем по одному).

        Returns: количество обработанных файлов.
        """
        if not self.available:
            raise RuntimeError("realesrgan-ncnn-vulkan.exe not found")

        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            str(self._binary_path),
            "-i", str(input_dir),
            "-o", str(output_dir),
            "-s", str(scale),
            "-n", self._model_name,
            "-t", str(self._tile_size),
        ]

        if self._model_name == "realesr-animevideov3":
            cmd.append("-x")
        if self._tta:
            cmd.append("-x")

        logger.info(f"Batch upscale: {' '.join(cmd)}")
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if proc.returncode != 0:
            raise RuntimeError(f"Batch upscale failed: {proc.stderr[:500]}")

        files = [f for f in output_dir.iterdir()
                 if f.suffix.lower() in (".png", ".jpg", ".jpeg")]
        return len(files)
