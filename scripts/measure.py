#!/usr/bin/env python3
"""Measure CPU-time deltas and RSS for explicitly selected app processes."""
import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("label")
parser.add_argument("pids", nargs="+", type=int)
parser.add_argument("--seconds", type=int, default=12)
args = parser.parse_args()

def seconds(value):
    total = 0.0
    for part in value.split(":"):
        total = total * 60 + float(part)
    return total

def read():
    output = subprocess.check_output(["ps", "-o", "pid=,time=,rss=,comm=", "-p",
                                      ",".join(map(str, args.pids))], text=True)
    result = {}
    for line in output.splitlines():
        pid, cpu, rss, command = line.strip().split(None, 3)
        result[int(pid)] = {"cpu_seconds": seconds(cpu), "rss_mib": int(rss) / 1024,
                            "command": command}
    return result

start = read()
t0 = time.monotonic()
time.sleep(args.seconds)
end = read()
elapsed = time.monotonic() - t0
rows = [{"pid": pid, **end[pid],
         "cpu_percent_one_core": (end[pid]["cpu_seconds"] - start[pid]["cpu_seconds"]) / elapsed * 100}
        for pid in start.keys() & end.keys()]
data = {"label": args.label, "at": dt.datetime.now().astimezone().isoformat(),
        "elapsed_seconds": elapsed, "processes": rows,
        "total_cpu_percent_one_core": sum(r["cpu_percent_one_core"] for r in rows),
        "sum_rss_mib": sum(r["rss_mib"] for r in rows),
        "notes": "RSS sum may double-count shared memory; CPU is total CPU time over elapsed time, not GPU utilization or battery life."}
path = Path(__file__).resolve().parents[1] / "evidence" / f"load-{args.label}.json"
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(data, ensure_ascii=False, indent=2))
