#!/usr/bin/env python3
"""Measure stable ON and OFF states on macOS; restore the agent.

Explicit --run is required. No other applications or window positions are changed.
Only aggregate resource counters and aquarium diagnostics are saved, not argv,
environment variables, unrelated app names, or screenshots.
"""
import argparse
import ctypes
from datetime import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import re
import signal
import statistics
import subprocess
import time

import provision

spec = importlib.util.spec_from_file_location("measure_v7", Path(__file__).with_name("measure-v7.py"))
reader_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader_module)


def command(*args):
    return subprocess.check_output(args, text=True).strip()


def age_seconds(value):
    days, clock = value.split("-") if "-" in value else (0, value)
    result = 0.0
    for part in clock.split(":"):
        result = result * 60 + float(part)
    return int(days) * 86400 + result


def inventory():
    result = {}
    for line in command("ps", "-axo", "pid=,etime=,comm=").splitlines():
        pid, age, name = line.strip().split(None, 2)
        result[int(pid)] = {"age": age_seconds(age), "name": name}
    return result


APP = str(provision.APP / "Contents/MacOS/Deskworlds")
HELPERS = {"com.apple.WebKit.GPU", "com.apple.WebKit.Networking", "com.apple.WebKit.WebContent"}


def group():
    rows = inventory()
    apps = [(pid, row) for pid, row in rows.items() if row["name"] == APP]
    if len(apps) != 1:
        raise RuntimeError("Expected exactly one installed aquarium")
    pid, app = apps[0]
    members = {pid: "Deskworlds"}
    for other, row in rows.items():
        name = Path(row["name"]).name
        if name in HELPERS and row["age"] <= app["age"] + 2:
            members[other] = name
    # These are candidates until all have been observed to exit with the app.
    return pid, members


def probe(pid, log, condition):
    offset = log.stat().st_size
    os.kill(pid, signal.SIGUSR2)
    time.sleep(1.5)
    with log.open() as stream:
        stream.seek(offset)
        lines = stream.read().splitlines()
    states = {}
    for line in lines:
        if f"Deskworlds[{pid}:" in line and "page state: " in line:
            state = json.loads(line.split("page state: ", 1)[1])
            states[state["windowID"]] = state
    if len(states) != 2:
        raise RuntimeError("Both aquarium probes are required")
    if condition == "covered":
        valid = all(s.get("pageReleased") and s.get("retainedFrame") and s.get("requestedRate") == 0 for s in states.values())
    elif condition == "active":
        valid = all(((s.get("stats") or {}).get("loop") or {}).get("running") and ((s.get("stats") or {}).get("loop") or {}).get("fps") == 24 for s in states.values())
    else:
        valid = True
    if not valid:
        raise RuntimeError(f"Aquarium state does not match {condition}; sample rejected")
    return states


def gpu():
    text = command("ioreg", "-r", "-c", "IOAccelerator", "-d", "1")
    match = re.search(r'"Device Utilization %"=(\d+)', text)
    if not match:
        raise RuntimeError("Whole-device GPU counter unavailable")
    return int(match.group(1))


def memory():
    text = command("vm_stat")
    page_size = int(re.search(r"page size of (\d+) bytes", text).group(1))
    rows = {k.strip('"'): int(v) for k, v in re.findall(r'^([^:\n]+):\s+(\d+)\.', text, re.M)}
    keys = ["Pages active", "Pages inactive", "Pages speculative", "Pages wired down", "Pages occupied by compressor"]
    # Approximate physical RAM in use excluding file-backed and purgeable caches.
    pages = sum(rows[k] for k in keys) - rows["File-backed pages"] - rows["Pages purgeable"]
    return {"used_excluding_cache_bytes": pages * page_size, "page_size": page_size,
            "counters": {k: rows[k] for k in keys + ["Pages free", "File-backed pages", "Pages purgeable", "Swapins", "Swapouts"]}}


class CPU:
    def __init__(self):
        self.lib = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
        self.lib.mach_host_self.restype = ctypes.c_uint
        self.lib.host_statistics.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint)]
        self.host = self.lib.mach_host_self()

    def ticks(self):
        values = (ctypes.c_uint * 4)()
        count = ctypes.c_uint(4)
        if self.lib.host_statistics(self.host, 3, values, ctypes.byref(count)) or count.value != 4:
            raise RuntimeError("host_statistics failed")
        return list(values)


def busy(a, b):
    delta = [(y - x) % (2 ** 32) for x, y in zip(a, b)]
    return 100 * (sum(delta) - delta[2]) / sum(delta)


def run(args):
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    save = lambda name, data: (out / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    agent_bytes = provision.AGENT.read_bytes()
    agent_hash = hashlib.sha256(agent_bytes).hexdigest()
    log = Path(plistlib.loads(agent_bytes)["StandardErrorPath"])
    source = json.loads((provision.APP / "Contents/Resources/source.json").read_text())
    if source["native_revision"] != "covered-pause-v1" or not provision.loaded():
        raise RuntimeError("Expected covered-pause-v1 with the existing LaunchAgent loaded")
    initial_pid, initial_group = group()
    initial_probe = probe(initial_pid, log, args.condition)
    cores = int(command("sysctl", "-n", "hw.logicalcpu"))
    ram = int(command("sysctl", "-n", "hw.memsize"))
    cpu = CPU()
    reader = reader_module.MacOSReader()
    if reader.unavailable:
        raise RuntimeError(reader.unavailable)
    save("method.json", {
        "at": datetime.now().astimezone().isoformat(), "seconds_per_phase": args.duration,
        "sequence": (["off-before", "on-" + args.condition, "off-after"] if args.sequence == "off-on-off" else ["on-" + args.condition, "off-after"]),
        "logical_cores": cores, "physical_ram_bytes": ram, "model_identifier": command("sysctl", "-n", "hw.model"),
        "macos": command("sw_vers", "-productVersion"),
        "native_revision": source["native_revision"], "native_source_sha256": source["native_source_sha256"],
        "configuration": "Balanced; 24 fish; 8 colors; both screens " + args.condition + "; unchanged window layout",
        "cpu": "host_statistics busy/total ticks; app proc_pid_rusage CPU-time delta / wall time / logical cores",
        "gpu": "IOAccelerator Device Utilization percent; whole Mac; not process-attributed",
        "memory": "vm_stat: (active + inactive + speculative + wired + compressor - file_backed - purgeable) * page size; estimate excluding reclaimable cache, not Activity Monitor exact parity",
        "app_memory": "sum of per-process ri_phys_footprint; shared allocations are not deduplicated; percentage is relative to installed RAM, not unique physical occupancy",
        "attribution": "Exact app binary plus newer WebKit candidates; each measured ON group must disappear when only the aquarium is stopped",
        "limitations": "Historical pre-installation state is unavailable. OFF keeps app files installed but stops the app and its helpers. Other apps continue running; no causal GPU or system RAM attribution from one comparison.",
        "initial_probe": initial_probe,
    })

    def stop_verified(members):
        provision.stop_agent()
        time.sleep(15)
        live = inventory()
        remaining = set(members) & set(live)
        if remaining or any(r["name"] == APP for r in live.values()):
            raise RuntimeError(f"Aquarium process attribution did not validate; remaining PIDs={sorted(remaining)}")
        return {"verified_exited_roles": list(members.values())}

    def read_group(members):
        return {pid: reader.read(pid) for pid in members}

    def phase(label, enabled):
        print(f"START {label} {args.duration}s", flush=True)
        pid, members = group() if enabled else (None, {})
        before = probe(pid, log, args.condition) if enabled else {}
        base = prev = read_group(members)
        base_ticks = prev_ticks = cpu.ticks()
        start = prev_time = time.monotonic()
        samples = []
        state_checks = [{"seconds": 0, "windows": before}] if enabled else []
        for index in range(args.duration // 2):
            time.sleep(max(0, start + (index + 1) * 2 - time.monotonic()))
            cur = read_group(members)
            for p in members:
                if cur[p]["identity"] != base[p]["identity"]:
                    raise RuntimeError("Process identity changed during sampling")
            ticks = cpu.ticks()
            now = time.monotonic()
            app_ns = sum(cur[p]["cpu_user_ns"] + cur[p]["cpu_system_ns"] - prev[p]["cpu_user_ns"] - prev[p]["cpu_system_ns"] for p in members)
            mem = memory()
            app_mem = sum(cur[p]["physical_footprint_bytes"] for p in members)
            samples.append({"seconds": now - start, "system_cpu_percent": busy(prev_ticks, ticks),
                "app_cpu_percent_one_core": 100 * app_ns / 1e9 / (now - prev_time),
                "gpu_device_percent": gpu(), "memory": mem, "app_footprint_bytes_sum": app_mem,
                "app_footprint_by_pid": {p: cur[p]["physical_footprint_bytes"] for p in members}})
            prev, prev_ticks, prev_time = cur, ticks, now
            if (index + 1) % 15 == 0:
                print(f"PROGRESS {label} {round(now - start)}s", flush=True)
                if enabled and index + 1 < args.duration // 2:
                    state_checks.append({"seconds": time.monotonic() - start, "windows": probe(pid, log, args.condition)})
        elapsed = prev_time - start
        app_ns = sum(prev[p]["cpu_user_ns"] + prev[p]["cpu_system_ns"] - base[p]["cpu_user_ns"] - base[p]["cpu_system_ns"] for p in members)
        app_one = 100 * app_ns / 1e9 / elapsed
        summary = {"label": label, "seconds": elapsed, "sample_count": len(samples),
            "system_cpu_percent": busy(base_ticks, prev_ticks),
            "app_cpu_percent_one_core": app_one, "app_cpu_percent_all_cores": app_one / cores,
            "gpu_device_percent_mean": statistics.mean(s["gpu_device_percent"] for s in samples),
            "gpu_device_percent_median": statistics.median(s["gpu_device_percent"] for s in samples),
            "gpu_device_percent_range": [min(s["gpu_device_percent"] for s in samples), max(s["gpu_device_percent"] for s in samples)],
            "system_memory_used_bytes_mean": statistics.mean(s["memory"]["used_excluding_cache_bytes"] for s in samples),
            "app_footprint_bytes_sum_mean": statistics.mean(s["app_footprint_bytes_sum"] for s in samples),
            "members": members}
        summary["system_memory_percent_mean"] = 100 * summary["system_memory_used_bytes_mean"] / ram
        summary["app_footprint_percent_of_ram"] = 100 * summary["app_footprint_bytes_sum_mean"] / ram
        after = probe(pid, log, args.condition) if enabled else {}
        if enabled and args.condition == "active":
            summary["frames"] = []
            for wid, end in after.items():
                begin = before[wid]
                frames = end["stats"]["renderedFrames"] - begin["stats"]["renderedFrames"]
                fps = 1000 * frames / (end["observedAtMs"] - begin["observedAtMs"])
                summary["frames"].append({"pixels": end["pixels"], "frames": frames, "fps": fps})
                if not 23 <= fps <= 25:
                    raise RuntimeError(f"Continuous 24 fps condition not maintained: {fps}")
        if enabled and group()[1] != members:
            raise RuntimeError("Aquarium process group changed during measurement")
        if not enabled and any(r["name"] == APP for r in inventory().values()):
            raise RuntimeError("Aquarium restarted during OFF measurement")
        if enabled:
            state_checks.append({"seconds": time.monotonic() - start, "windows": after})
        save(label + ".json", {"summary": summary, "samples": samples, "before": before, "after": after, "state_checks": state_checks})
        print("RESULT " + json.dumps(summary), flush=True)
        return summary, members

    results = []
    try:
        initial_exit = None
        if args.sequence == "off-on-off":
            initial_exit = stop_verified(initial_group)
            results.append(phase("off-before", False)[0])
            print("START aquarium; wait 75 seconds for stabilization", flush=True)
            provision.run("launchctl", "bootstrap", provision.DOMAIN, str(provision.AGENT))
            time.sleep(75)
        on, members = phase("on-" + args.condition, True)
        results.append(on)
        on_exit = stop_verified(members)
        results.append(phase("off-after", False)[0])
        save("summary.json", {"phases": results, "initial_group_validation": initial_exit, "measured_group_validation": on_exit})
    finally:
        print("RESTORE original LaunchAgent and aquarium", flush=True)
        if not provision.loaded():
            provision.run("launchctl", "bootstrap", provision.DOMAIN, str(provision.AGENT))
        if hashlib.sha256(provision.AGENT.read_bytes()).hexdigest() != agent_hash:
            raise RuntimeError("LaunchAgent file changed")
        save("restoration.json", {"at": datetime.now().astimezone().isoformat(), "agent_loaded": provision.loaded(), "agent_file_unchanged": True})
    print("COMPLETE " + str(out), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="Temporarily stop/restart only Deskworlds to measure")
    parser.add_argument("--duration", type=int, default=90)
    parser.add_argument("--condition", choices=["covered", "active", "normal"], required=True)
    parser.add_argument("--sequence", choices=["off-on-off", "on-off"], default="off-on-off")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.run or args.duration < 2 or args.duration % 2:
        parser.error("Explicit --run and a positive even duration >= 2 are required")
    run(args)
