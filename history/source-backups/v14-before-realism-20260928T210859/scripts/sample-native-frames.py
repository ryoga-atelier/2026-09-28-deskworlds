#!/usr/bin/env python3
"""Read passive app diagnostics for an explicitly attributed Deskworlds PID."""
import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time

p = argparse.ArgumentParser()
p.add_argument('--pid', type=int, required=True)
p.add_argument('--duration', type=float, default=90)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
root = Path(__file__).resolve().parents[1]
expected = str(Path.home() / 'Applications/Deskworlds.app/Contents/MacOS/Deskworlds')
if a.output.exists():
    raise FileExistsError(a.output)
log = root / 'evidence/deskworlds-runtime.log'
start = log.stat().st_size
deadline = time.monotonic() + a.duration
while True:
    actual = subprocess.check_output(['ps', '-p', str(a.pid), '-o', 'comm='], text=True).strip()
    if actual != expected:
        raise RuntimeError('Explicit PID no longer belongs to Deskworlds')
    os.kill(a.pid, signal.SIGUSR2)
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        break
    time.sleep(min(5, remaining))
time.sleep(.4)
with log.open('rb') as f:
    f.seek(start)
    lines = f.read().decode().splitlines()
rows = []
for line in lines:
    if f'Deskworlds[{a.pid}:' in line and 'deskworlds page state: ' in line:
        timestamp, value = line.split(' deskworlds page state: ', 1)
        rows.append({'native_log_time': timestamp, 'page': json.loads(value)})
a.output.write_text(json.dumps(rows, indent=2) + '\n')
print(json.dumps({'samples': len(rows), 'file': str(a.output)}))
