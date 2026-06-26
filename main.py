#!/usr/bin/env python3
"""x2-upscale — Image upscaling with GUI and CLI.

Usage:
  python main.py gui          # Launch GUI
  python main.py input.jpg    # Quick CLI upscale (2x)
  python main.py --help       # Full CLI usage
"""

import sys
from app import cli
from app import __version__


def main():
    if len(sys.argv) == 1:
        # No args → GUI
        from app.gui import run_gui
        run_gui()
        return

    if sys.argv[1] in ("gui", "--gui", "-g"):
        from app.gui import run_gui
        run_gui()
        return

    if sys.argv[1] in ("--version", "-V"):
        print(f"x2-upscale v{__version__}")
        return

    # Otherwise pass to CLI
    exit_code = cli.run_cli()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
