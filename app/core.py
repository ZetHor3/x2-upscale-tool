"""Core upscaling orchestrator — ties together backends, batch ops, progress."""

import os
import sys
import time
from pathlib import Path
from PIL import Image
from . import models
from . import utils


class UpscaleJob:
    """Represents a single image upscaling job."""

    def __init__(self, input_path: Path, output_path: Path | None = None, scale: float = 2.0):
        self.input_path = input_path
        self.output_path = output_path or utils.ensure_output_path(input_path)
        self.scale = scale
        self.duration: float = 0.0
        self.error: str | None = None
        self.input_size: tuple[int, int] | None = None
        self.output_size: tuple[int, int] | None = None

    @property
    def status(self) -> str:
        if self.error:
            return "ERROR"
        if self.duration > 0 and self.output_size:
            return "OK"
        return "PENDING"


class UpscaleEngine:
    """Orchestrates upscaling with progress reporting."""

    def __init__(self, backend_name: str = "ai", device: str | None = None):
        self.backend = models.get_backend(backend_name, device=device)
        self.backend_name = backend_name
        self._tiling = False
        self._tile_size = 512
        self._tile_overlap = 32
        self._on_progress = None  # callback(completed, total, job)

    @property
    def display_name(self) -> str:
        return self.backend.display_name

    @property
    def device(self) -> str:
        return self.backend.device

    def set_options(self, **kwargs) -> None:
        self.backend.set_options(**kwargs)
        if "tiling" in kwargs:
            self._tiling = bool(kwargs["tiling"])
        if "tile_size" in kwargs:
            self._tile_size = int(kwargs["tile_size"])
        if "tile_overlap" in kwargs:
            self._tile_overlap = int(kwargs["tile_overlap"])

    def get_backend_options(self) -> dict:
        return self.backend.get_options()

    def set_progress_callback(self, callback) -> None:
        self._on_progress = callback

    def upscale_one(self, job: UpscaleJob) -> UpscaleJob:
        """Process a single job."""
        try:
            img = utils.load_image(job.input_path)
            job.input_size = img.size

            t0 = time.time()

            if self._tiling and self.backend.supports_tiling:
                result = self.backend.upscale_tiled(
                    img, scale=job.scale,
                    tile_size=self._tile_size,
                    overlap=self._tile_overlap,
                )
            else:
                result = self.backend.upscale(img, scale=job.scale)

            job.duration = time.time() - t0
            job.output_size = result.size

            utils.ensure_output_dir(job.output_path)
            utils.save_image(result, job.output_path)
        except Exception as e:
            job.error = f"{type(e).__name__}: {e}"
            import traceback
            traceback.print_exc()

        return job

    def upscale_many(self, jobs: list[UpscaleJob]) -> list[UpscaleJob]:
        """Process multiple jobs sequentially with progress callbacks."""
        completed = 0
        total = len(jobs)
        results = []

        for job in jobs:
            self.upscale_one(job)
            results.append(job)
            if job.error:
                completed += 1
            else:
                completed += 1
            if self._on_progress:
                self._on_progress(completed, total, job)

        return results

    def upscale_paths(
        self,
        input_paths: list[str | Path],
        output_dir: str | Path | None = None,
        scale: float = 2.0,
    ) -> list[UpscaleJob]:
        """Convenience: process a list of input paths."""
        images = utils.list_images(input_paths)
        if not images:
            return []

        jobs = []
        for img_path in images:
            if output_dir:
                out = Path(output_dir) / img_path.name
            else:
                out = None
            jobs.append(UpscaleJob(img_path, out, scale=scale))

        return self.upscale_many(jobs)
