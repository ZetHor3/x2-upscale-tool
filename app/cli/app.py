"""CLI application — argparse-based interface."""

import sys
import argparse
from pathlib import Path
from ..core import UpscaleEngine
from .. import models


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="x2-upscale",
        description="Image upscaling tool — CLI mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  x2-upscale input.jpg output.jpg
  x2-upscale input.png --scale 3 --method torch --sharpness 0.5
  x2-upscale folder/ --out results/ --method pil --filter lanczos
  x2-upscale *.png --method realesrgan --tiling --tile-size 256
        """,
    )

    parser.add_argument("input", nargs="*", help="Input image(s) or folder(s)")
    parser.add_argument("-o", "--out", help="Output path (file or directory)")
    parser.add_argument("-s", "--scale", type=float, default=2.0, help="Scale factor (default: 2.0)")

    parser.add_argument(
        "-m", "--method", choices=models.list_backends(), default="ncnn",
        help=f"Upscaling method (default: ncnn). Available: {', '.join(models.list_backends())}",
    )
    parser.add_argument("-d", "--device", default=None, help="Device: 'cuda:0', 'cpu' (default: auto)")

    # PIL options
    parser.add_argument("-f", "--filter", default=None, help="PIL filter: lanczos, bicubic, nearest, etc.")

    # Torch options
    parser.add_argument("--sharpness", type=float, default=None, help="Unsharp mask strength (torch method)")

    # Model options (Real-ESRGAN / ncnn)
    parser.add_argument("--model", default=None, help="Model name (realesr-animevideov3, realesrgan-x4plus, etc.)")

    # Tiling
    parser.add_argument("--tiling", action="store_true", help="Enable tiling for large images")
    parser.add_argument("--tile-size", type=int, default=512, help="Tile size in pixels (default: 512)")
    parser.add_argument("--tile-overlap", type=int, default=32, help="Tile overlap in pixels (default: 32)")

    parser.add_argument("-q", "--quality", type=int, default=95, help="Output JPEG/WEBP quality (0-100)")
    parser.add_argument("--list-methods", action="store_true", help="List available upscaling methods and exit")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    return parser


def run_cli(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_methods:
        print("Available upscaling methods:")
        for name in models.list_backends():
            backend = models.get_backend(name)
            print(f"  {name:16s}  {backend.device:>8s}  {backend.display_name}")
        return 0

    if not args.input:
        parser.print_help()
        return 1

    # Build engine
    try:
        engine = UpscaleEngine(backend_name=args.method, device=args.device)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Backend options
    opts = {}
    if args.filter is not None:
        opts["filter"] = args.filter
    if args.sharpness is not None:
        opts["sharpness"] = args.sharpness
    if args.model is not None:
        opts["model"] = args.model
    if args.tiling:
        opts["tiling"] = True
        opts["tile_size"] = args.tile_size
        opts["tile_overlap"] = args.tile_overlap
    engine.set_options(**opts)

    # Gather inputs
    import os
    input_paths = []
    for p in args.input:
        path = Path(p)
        if path.is_dir():
            input_paths.extend(sorted(path.iterdir()))
        else:
            input_paths.append(path)

    if not input_paths:
        print("No input files found.", file=sys.stderr)
        return 1

    # Determine output: for single file, -o can be a filename; for batch it's a directory
    output_dir = None
    single_output = None
    if args.out:
        out_path = Path(args.out)
        # If it has an image extension and there's only one input, treat as filename
        is_img_ext = out_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}
        if is_img_ext and len(input_paths) == 1:
            single_output = out_path
        else:
            output_dir = out_path

    if args.verbose:
        print(f"Backend: {engine.backend.display_name} on {engine.device}")
        print(f"Scale:   {args.scale}x")
        print(f"Files:   {len(input_paths)}")
        print("-" * 40)

    if single_output:
        # Single file → one job with explicit output
        from ..core import UpscaleJob
        job = UpscaleJob(input_paths[0], output_path=single_output, scale=args.scale)
        results = engine.upscale_many([job])
    else:
        results = engine.upscale_paths(input_paths, output_dir=output_dir, scale=args.scale)

    ok = 0
    failed = 0
    for job in results:
        if job.error:
            failed += 1
            print(f"FAIL  {job.input_path.name}: {job.error}", file=sys.stderr)
        else:
            ok += 1
            if args.verbose:
                old = f"{job.input_size[0]}x{job.input_size[1]}"
                new = f"{job.output_size[0]}x{job.output_size[1]}"
                print(f"OK    {job.input_path.name}  {old} -> {new}  {job.duration:.1f}s")

    if args.verbose:
        print("-" * 40)
        print(f"Done: {ok} OK, {failed} failed")

    return 0 if failed == 0 else 1
