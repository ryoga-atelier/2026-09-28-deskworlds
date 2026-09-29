"""Build the portable package and point the browser test at that exact output."""
import json
import os
from pathlib import Path
import platform
import sys
from portable_setup import build_windows

root = Path(__file__).resolve().parents[1]
folder, archive = build_windows()
(root / "evidence/platform-ci.json").write_text(json.dumps({
    "os": platform.platform(), "architecture": platform.machine(),
    "python": sys.version, "package": str(archive),
    "scope": "Native OS packaging plus headless Chromium; not an interactive Lively desktop.",
}, indent=2) + "\n", encoding="utf-8")
if os.environ.get("GITHUB_ENV"):
    with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as stream:
        stream.write("GUPPY_PACKAGE=" + str(folder) + "\n")
print(archive)
