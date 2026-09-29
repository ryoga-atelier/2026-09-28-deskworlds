#!/usr/bin/env python3
"""Build/install or retire the pinned Deskworlds app without deleting files."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import plistlib
import shutil
import signal
import subprocess
import time
from customize import apply_guppy
from exhibit_overlay import apply_exhibit
from native_diagnostics import apply_native_probe
from native_release import apply_native_release

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "upstream/deskworlds"
PIN = "3950c45ef5798ed2df9f78037994bcddacebbb01"
LABEL = "com.chaselean.deskworlds"
APP = Path.home() / "Applications/Deskworlds.app"
AGENT = Path.home() / "Library/LaunchAgents" / f"{LABEL}.plist"
DOMAIN = f"gui/{os.getuid()}"


def run(*args, check=True, **kwargs):
    return subprocess.run(args, check=check, text=True, **kwargs)


def timestamp():
    return dt.datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%f%z")


def loaded():
    return run("launchctl", "print", f"{DOMAIN}/{LABEL}", check=False,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def archive(path, target, records):
    if path.exists() or path.is_symlink():
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            raise FileExistsError(target)
        shutil.move(str(path), str(target))
        records.append({"from": str(path), "to": str(target)})


def record(folder, data):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "manifest.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def stop_agent():
    if loaded():
        run("launchctl", "bootout", f"{DOMAIN}/{LABEL}")
    # A later Finder launch can exist outside launchd's job. Stop only this exact binary.
    expected = str(APP / "Contents/MacOS/Deskworlds")
    processes = run("ps", "-axo", "pid=,comm=", capture_output=True).stdout
    for line in processes.splitlines():
        pid, command = line.strip().split(None, 1)
        if command != expected:
            continue
        pid = int(pid)
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            continue
        for _ in range(30):
            current = run("ps", "-p", str(pid), "-o", "comm=", check=False,
                          capture_output=True).stdout.strip()
            if current != expected:
                break
            time.sleep(0.1)
        else:
            raise RuntimeError(f"App did not stop normally (PID {pid}); no files were moved")


def build(variant="guppy-v29"):
    actual = run("git", "-C", str(SOURCE), "rev-parse", "HEAD", capture_output=True).stdout.strip()
    if actual != PIN:
        raise RuntimeError(f"Unexpected source commit: {actual}")
    if run("git", "-C", str(SOURCE), "status", "--porcelain", capture_output=True).stdout.strip():
        raise RuntimeError("Upstream contains changes; inspect before building")
    out = ROOT / "build" / timestamp() / "Deskworlds.app"
    macos = out / "Contents/MacOS"
    resources = out / "Contents/Resources"
    macos.mkdir(parents=True)
    resources.mkdir()
    swift_source = out.parent / "Wallpaper.swift"
    swift_source.write_text(apply_native_release(apply_native_probe((SOURCE / "wallpaper/Wallpaper.swift").read_text())))
    arch = run("uname", "-m", capture_output=True).stdout.strip()
    run("swiftc", "-O", "-target", f"{arch}-apple-macos13.0", "-o", str(macos / "Deskworlds"),
        str(swift_source), "-framework", "Cocoa",
        "-framework", "WebKit", "-framework", "IOKit")
    shutil.copy2(SOURCE / "wallpaper/Info.plist", out / "Contents/Info.plist")
    for name in ("AppIcon.icns", "menubar.svg"):
        shutil.copy2(SOURCE / "wallpaper" / name, resources / name)
    for name in ("scenes", "vendor", "ui"):
        shutil.copytree(SOURCE / name, resources / "scene" / name,
                        ignore=shutil.ignore_patterns("tests", "__pycache__"))
    customization = apply_guppy(resources / "scene") if variant in ("guppy", "guppy-v15", "guppy-v16", "guppy-v17", "guppy-v18", "guppy-v19", "guppy-v20", "guppy-v21", "guppy-v22", "guppy-v23", "guppy-v24", "guppy-v25", "guppy-v26", "guppy-v27", "guppy-v28", "guppy-v29") else None
    if variant in ("guppy-v15","guppy-v16","guppy-v17","guppy-v18","guppy-v19","guppy-v20","guppy-v21","guppy-v22","guppy-v23","guppy-v24","guppy-v25","guppy-v26","guppy-v27","guppy-v28","guppy-v29"): customization = apply_exhibit(resources / "scene", variant.removeprefix("guppy-"))
    shutil.copy2(SOURCE / "LICENSE", resources / "LICENSE")
    shutil.copy2(SOURCE / "README.md", resources / "UPSTREAM-README.md")
    (resources / "source.json").write_text(json.dumps({
        "url": "https://github.com/chaseleantj/deskworlds", "commit": PIN,
        "source_post": "https://x.com/chaseleantj/status/2100663203076128908",
        "variant": variant, "customization": customization,
        "native_diagnostic": "SIGUSR2 passive stats; event-triggered menu/sleep/wake/startup audit v1; SIGUSR1 upstream forced snapshot",
        "native_revision": "background-swimming-v2",
        "native_release": "Awake aquariums keep swimming at 24 fps when under 40% is exposed; Balanced stays capped at 24 fps otherwise. Pause and Low Power stop drawing. Only display/session sleep for 60 s releases the page, retaining a bounded aquarium bitmap until the reloaded scene renders.",
        "native_source_sha256": hashlib.sha256(swift_source.read_bytes()).hexdigest(),
    }, indent=2) + "\n")
    run("codesign", "--sign", "-", str(out))
    run("codesign", "--verify", "--deep", "--strict", str(out))
    run("plutil", "-lint", str(out / "Contents/Info.plist"))
    return out


def install(variant="guppy-v29"):
    candidate = build(variant)  # Fully build and verify before touching installed state.
    backup = ROOT / "rollback" / timestamp()
    records = []
    was_loaded = loaded()
    agent_data = {
        "Label": LABEL, "ProgramArguments": [str(APP / "Contents/MacOS/Deskworlds")],
        "RunAtLoad": True, "KeepAlive": {"SuccessfulExit": False}, "ProcessType": "Interactive",
        "StandardErrorPath": str(ROOT / "evidence/deskworlds-runtime.log"),
    }
    stop_agent()
    try:
        archive(APP, backup / "previous/Deskworlds.app", records)
        archive(AGENT, backup / "previous" / AGENT.name, records)
        record(backup, {"previous_agent_loaded": was_loaded, "moves": records})
        APP.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(candidate, APP)
        AGENT.parent.mkdir(parents=True, exist_ok=True)
        with AGENT.open("xb") as f:
            plistlib.dump(agent_data, f)
        os.chmod(AGENT, 0o644)
        run("plutil", "-lint", str(AGENT))
        run("launchctl", "bootstrap", DOMAIN, str(AGENT))
    except Exception:
        stop_agent()
        failed = []
        archive(APP, backup / "failed/Deskworlds.app", failed)
        archive(AGENT, backup / "failed" / AGENT.name, failed)
        for item in reversed(records):
            shutil.move(item["to"], item["from"])
        record(backup, {"rolled_back": True, "previous_agent_loaded": was_loaded,
                        "moves": records, "failed_installation": failed})
        if was_loaded and AGENT.exists():
            run("launchctl", "bootstrap", DOMAIN, str(AGENT))
        raise
    record(ROOT / "evidence", {"installed_at": dt.datetime.now().astimezone().isoformat(),
           "source_commit": PIN, "app": str(APP), "launch_agent": str(AGENT),
           "variant": variant,
           "backup": str(backup), "build": str(candidate),
           "binary_sha256": hashlib.sha256((APP / "Contents/MacOS/Deskworlds").read_bytes()).hexdigest()})
    print(f"Installed: {APP}\nLogin agent: {AGENT}\nBackup: {backup}")


def retire(whole_app):
    backup = ROOT / "rollback" / timestamp()
    moves = []
    stop_agent()
    archive(AGENT, backup / AGENT.name, moves)
    if whole_app:
        archive(APP, backup / "Deskworlds.app", moves)
    record(backup, {"action": "retire" if whole_app else "disable-autostart", "moves": moves})
    print(f"Stopped; files retained at {backup}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["build", "install", "disable-autostart", "retire"])
    parser.add_argument("--variant", choices=["guppy", "guppy-v15", "guppy-v16", "guppy-v17", "guppy-v18", "guppy-v19", "guppy-v20", "guppy-v21", "guppy-v22", "guppy-v23", "guppy-v24", "guppy-v25", "guppy-v26", "guppy-v27", "guppy-v28", "guppy-v29", "original"], default="guppy-v29")
    args = parser.parse_args()
    action = args.action
    if action == "build":
        print(build(args.variant))
    elif action == "install":
        install(args.variant)
    else:
        retire(action == "retire")
