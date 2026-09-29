#!/usr/bin/env python3
"""One entry point for the pinned Mac app and the Windows Lively package."""
import os
import sys
from pathlib import Path

# Historical overlay scripts contain Japanese text. Make encoding explicit even
# on a Windows machine whose system code page is not UTF-8.
if os.name == "nt" and not sys.flags.utf8_mode:
    os.execv(sys.executable, [sys.executable, "-X", "utf8", __file__, *sys.argv[1:]])
if sys.version_info < (3, 10):
    raise SystemExit("Python 3.10 or newer is required: https://www.python.org/downloads/")
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
from portable_setup import main

if __name__ == "__main__":
    raise SystemExit(main())
