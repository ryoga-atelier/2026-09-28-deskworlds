"""Run the same source/regression checks without POSIX-shell-only npm syntax."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
scene = Path(sys.argv[1]).resolve()
files = [scene / "serve.mjs"]
for glob in ("scenes/*/src/*.js", "scenes/shared/*.js", "ui/*.js"):
    files.extend(sorted(scene.glob(glob)))
for path in files:
    subprocess.run(["node", "--check", str(path)], check=True)
for path in [
    "ui/tests/gallery.mjs", "scenes/riverscape/tests/fish-behavior.mjs",
    "scenes/riverscape/tests/render-policy.mjs", "scenes/riverscape/tests/plant-budget.mjs",
    "scenes/reefscape/tests/behavior.mjs", "scenes/reefscape/tests/assets.mjs",
    "scenes/reefscape/tests/locomotion.mjs", "scenes/reefscape/tests/anemone.mjs",
    "scenes/bettascape/tests/food.mjs",
]:
    subprocess.run(["node", path], cwd=scene, check=True)
for name in ["check-photo-guppy-v29", "check-photo-guppy-v28", "check-guppy-v17", "check-v17", "check-living-water"]:
    subprocess.run(["node", str(ROOT / "scripts" / (name + ".mjs")), str(scene)], check=True)
print("PASS: portable syntax, upstream regression, guppy and water checks")
