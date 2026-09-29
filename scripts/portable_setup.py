"""Portable preparation; delegates macOS installation to the existing installer."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PIN = "3950c45ef5798ed2df9f78037994bcddacebbb01"
UPSTREAM = "https://github.com/chaseleantj/deskworlds.git"
REVISION = "bronze-gradient-guppy-v29-r16"


def run(argv, **kwargs):
    return subprocess.run([str(x) for x in argv], check=True, **kwargs)


def stamp():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def target_platform(value):
    return {"Darwin": "macos", "Windows": "windows"}.get(platform.system(), "unsupported") if value == "auto" else value


def find_lively(explicit=None):
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not path.is_file() or path.suffix.lower() != ".exe":
            raise ValueError("--lively must name an existing Lively.exe or livelycu.exe")
        if path.name.lower() not in ("lively.exe", "livelycu.exe"):
            raise ValueError("Expected Lively.exe or livelycu.exe")
        return path
    found = shutil.which("lively.exe") or shutil.which("livelycu.exe")
    if found:
        return Path(found)
    candidates = []
    if os.environ.get("LOCALAPPDATA"):
        candidates.append(Path(os.environ["LOCALAPPDATA"]) / "Programs/Lively Wallpaper/Lively.exe")
    for key in ("ProgramFiles", "ProgramFiles(x86)"):
        if os.environ.get(key):
            candidates.append(Path(os.environ[key]) / "Lively Wallpaper/Lively.exe")
    return next((p for p in candidates if p.is_file()), None)


def lively_library(local_data=None, explicit=None):
    # Read only the library location; never modify Lively's global settings.
    if explicit:
        directory = Path(explicit).expanduser().resolve()
    else:
        base = Path(local_data or os.environ.get("LOCALAPPDATA", ""))
        candidates = [
            base / "Lively Wallpaper/Settings.json",
            base / "Packages/12030rocksdanister.LivelyWallpaper_97hta09mmv6hy/LocalCache/Local/Lively Wallpaper/Settings.json",
        ]
        settings = next((p for p in candidates if p.is_file()), None)
        if not settings:
            raise ValueError("Start Lively once to create its library, or use --library <Library folder>.")
        value = json.loads(settings.read_text(encoding="utf-8-sig")).get("WallpaperDir")
        if not isinstance(value, str) or not value:
            raise ValueError("Lively WallpaperDir is missing; select --library explicitly.")
        directory = Path(value).expanduser()
        if not directory.is_absolute():
            raise ValueError("Lively WallpaperDir must be an absolute path.")
    if not directory.is_dir() or not (directory / "wallpapers").is_dir():
        raise ValueError("Expected Lively's Library folder containing wallpapers/ (see docs/WINDOWS.md).")
    return directory


def doctor(target, lively=None):
    problems = []
    if not (ROOT / ".git").exists():
        problems.append("Use a Git clone of this repository, including its submodules; Download ZIP is not a setup bundle.")
    if target == "unsupported":
        problems.append("Desktop installation supports macOS and Windows; Windows packaging can run on other OSs.")
    if not shutil.which("git"):
        problems.append("Install Git first.")
    if target == "macos":
        if platform.system() != "Darwin":
            problems.append("The Mac app must be built on macOS.")
        elif int(platform.mac_ver()[0].split(".")[0]) < 13:
            problems.append("macOS 13 or later is required.")
        if not shutil.which("swiftc") or subprocess.run(["xcode-select", "-p"], capture_output=True).returncode:
            problems.append("Install Xcode Command Line Tools: xcode-select --install")
    if target == "windows":
        node = shutil.which("node")
        if not node or not shutil.which("npm"):
            problems.append("Install Node.js 22 or later (includes npm).")
        elif int(subprocess.check_output([node, "--version"], text=True).strip().lstrip("v").split(".")[0]) < 22:
            problems.append("Node.js 22 or later is required.")
    return {
        "platform": target, "python": platform.python_version(),
        "revision": REVISION, "ready_to_build": not problems, "problems": problems,
        "lively": str(find_lively(lively) or "") if platform.system() == "Windows" else None,
        "access": "Public repository: GitHub authentication is not required to clone or download.",
    }


def ensure_upstream(root=ROOT):
    source = root / "upstream/deskworlds"
    if not (source / ".git").exists():
        if not (root / ".git").exists():
            raise ValueError("Use git clone --recurse-submodules; GitHub Download ZIP lacks pinned submodules.")
        run(["git", "-c", "submodule.upstream/deskworlds.url=" + UPSTREAM,
             "submodule", "update", "--init", "--", "upstream/deskworlds"], cwd=root)
    actual = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if actual != PIN:
        raise ValueError("Upstream pin mismatch; inspect local changes instead of resetting it.")
    if subprocess.check_output(["git", "-C", str(source), "status", "--porcelain"], text=True).strip():
        raise ValueError("Upstream has local changes; nothing was overwritten.")
    return source


def prepare_scene(target, root=ROOT):
    from customize import apply_guppy
    from exhibit_overlay import apply_exhibit
    source = ensure_upstream(root)
    target = Path(target)
    target.mkdir(parents=True, exist_ok=False)
    for name in ("scenes", "vendor", "ui"):
        shutil.copytree(source / name, target / name)
    for name in ("package.json", "serve.mjs"):
        shutil.copy2(source / name, target / name)
    apply_guppy(target)
    apply_exhibit(target, "v29")
    return target


def build_windows(root=ROOT):
    # Node/esbuild are build-time tools only. The ZIP needs only Lively at runtime.
    if not (root / "node_modules/esbuild/package.json").is_file():
        run([shutil.which("npm") or "npm", "ci", "--no-audit", "--no-fund"], cwd=root)
    folder = root / "dist/windows" / (REVISION + "-" + stamp())
    prepare_scene(folder, root)
    for path in (root / "platforms/windows").iterdir():
        if path.is_file():
            shutil.copy2(path, folder / path.name)
    shutil.copytree(root / "licenses", folder / "licenses")
    # Keep Three.js's license adjacent to its bundled counterpart.
    shutil.copy2(root / "SOURCES-AND-LICENSES.md", folder / "SOURCES-AND-LICENSES.md")
    shutil.copy2(root / "docs/WINDOWS.md", folder / "WINDOWS-SETUP.md")
    shutil.copy2(root / "evidence/v29-r15-wallpaper-1789x1006.png", folder / "thumbnail.png")
    run(["node", root / "scripts/build-windows.mjs", folder], cwd=root)
    hashes = {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(folder.rglob("*")) if p.is_file()}
    (folder / "package-manifest.json").write_text(json.dumps({
        "revision": REVISION, "upstream_commit": PIN, "platform": "windows-lively",
        "fps": 24, "fish": 24, "colour_families": 8, "files": hashes,
    }, indent=2) + "\n", encoding="utf-8")
    archive = folder.with_suffix(".zip")
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as output:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                output.write(path, path.relative_to(folder).as_posix())
    return folder, archive


def install_lively(folder, library, executable, monitor=None):
    destination = library / "wallpapers" / ("guppy-garden-r16-" + stamp())
    shutil.copytree(folder, destination)  # New directory only; prior versions remain.
    command = [str(executable), "setwp", "--file", str(destination)]
    if monitor is not None:
        command += ["--monitor", str(monitor)]
    run(command)
    return {
        "status": "command_sent_visual_check_required",
        "installed_folder": str(destination), "command": command,
        "next": "Confirm the moving fish and Feed / Playing in Lively. CLI success alone is not visual verification.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", default="doctor", choices=["doctor", "build", "install", "prepare", "verify"])
    parser.add_argument("--platform", default="auto", choices=["auto", "macos", "windows"])
    parser.add_argument("--lively", help="Path to Lively.exe or livelycu.exe")
    parser.add_argument("--library", help="Existing Lively Library directory (parent of wallpapers)")
    parser.add_argument("--monitor", type=int, help="Lively monitor index (default: primary)")
    args = parser.parse_args(argv)
    if args.monitor is not None and args.monitor < 1:
        parser.error("--monitor must be a positive Lively screen index")
    try:
        target = target_platform(args.platform)
        report = doctor(target, args.lively)
        if args.action == "doctor":
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["ready_to_build"] else 2
        if args.action in ("prepare", "verify"):
            folder = prepare_scene(ROOT / "build" / ("portable-check-" + stamp()))
            if args.action == "verify":
                if not shutil.which("node"):
                    raise ValueError("Node.js 22 or later is required for verification.")
                run([sys.executable, ROOT / "scripts/check-portable.py", folder], cwd=ROOT)
            print(folder)
            return 0
        if not report["ready_to_build"]:
            raise ValueError("\n".join(report["problems"]))
        ensure_upstream()
        if target == "macos":
            from provision import build, install
            if args.action == "build":
                print(build())
            else:
                install()
        else:
            if args.action == "install":
                if platform.system() != "Windows":
                    raise ValueError("Windows installation must run on Windows. Use build --platform windows here.")
                executable = find_lively(args.lively)
                if not executable:
                    raise ValueError("Install and start Lively first; see docs/WINDOWS.md or use --lively.")
                library = lively_library(explicit=args.library)
            folder, archive = build_windows()
            result = {"folder": str(folder), "zip": str(archive), "revision": REVISION}
            if args.action == "install":
                result.update(install_lively(folder, library, executable, args.monitor))
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, FileExistsError, FileNotFoundError, subprocess.CalledProcessError) as error:
        print("Setup stopped: " + str(error), file=sys.stderr)
        return 2
