#!/usr/bin/env python3
"""r15 state load sampler. Read-only apart from its own evidence JSON and a SIGUSR2
diagnostic probe (the app logs each screen's page state; no rendering is forced).

CPU: summed process CPU time deltas of the app and its own WebKit group, 100% = one core.
Memory: per-process phys_footprint (not summed as unique RAM).
GPU: whole-machine IOAccelerator "Device Utilization %" (includes other apps).
Frames: renderedFrames difference per window between two probes.
"""
import argparse, json, os, re, signal, subprocess, time
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'evidence/deskworlds-runtime.log'
APP = str(Path.home() / 'Applications/Deskworlds.app/Contents/MacOS/Deskworlds')

def etime_seconds(text):
    days = 0
    if '-' in text:
        d, text = text.split('-'); days = int(d)
    parts = [float(p) for p in text.split(':')]
    while len(parts) < 3: parts.insert(0, 0)
    return days * 86400 + parts[0] * 3600 + parts[1] * 60 + parts[2]

def group():
    rows = subprocess.check_output(['ps', '-axo', 'pid=,etime=,comm='], text=True).splitlines()
    app = None; webkit = []
    for row in rows:
        pid, et, comm = row.strip().split(None, 2)
        if comm == APP: app = (int(pid), etime_seconds(et))
        elif comm.split('/')[-1] in ('com.apple.WebKit.GPU', 'com.apple.WebKit.WebContent', 'com.apple.WebKit.Networking'):
            webkit.append((int(pid), etime_seconds(et), comm.split('/')[-1]))
    if not app: raise SystemExit('Deskworlds is not running')
    # WebKit helpers launched with this app instance (within 8 s of it). WebContent
    # reloaded later for a released screen is newer, so include anything younger too.
    members = {app[0]: 'Deskworlds'}
    for pid, et, name in webkit:
        if et <= app[1] + 1 and et >= 0: members[pid] = name
    return members

def cpu_seconds(pids):
    out = subprocess.run(['ps', '-o', 'pid=,time=', '-p', ','.join(map(str, pids))], text=True, capture_output=True).stdout
    return {int(p): etime_seconds(t) for p, t in (l.split() for l in out.splitlines())}

def footprint(pid):
    out = subprocess.run(['footprint', '-p', str(pid), '-f', 'bytes', '--noCategories'], text=True, capture_output=True).stdout
    m = re.search(r'Footprint: (\d+) B', out)
    return int(m.group(1)) / 1048576 if m else None

def gpu():
    out = subprocess.run(['ioreg', '-r', '-c', 'IOAccelerator', '-d', '1'], text=True, capture_output=True).stdout
    m = re.search(r'"Device Utilization %"=(\d+)', out)
    return int(m.group(1)) if m else None

def probe(app_pid):
    mark = LOG.stat().st_size
    os.kill(app_pid, signal.SIGUSR2)
    time.sleep(1.5)
    with LOG.open() as f:
        f.seek(mark); text = f.read()
    states = {}
    for line in text.splitlines():
        if f'Deskworlds[{app_pid}:' in line and 'page state: ' in line:
            try: d = json.loads(line.split('page state: ', 1)[1])
            except Exception: continue
            s = d.get('stats') or {}
            states[d.get('windowID')] = {'pixels': d.get('pixels'), 'frames': s.get('renderedFrames'),
                'observedAtMs': d.get('observedAtMs'), 'running': (s.get('loop') or {}).get('running')}
    return time.monotonic(), states

p = argparse.ArgumentParser(); p.add_argument('label'); p.add_argument('--duration', type=float, default=90)
p.add_argument('--interval', type=float, default=2)
a = p.parse_args()
out = ROOT / 'evidence' / f'r15-load-{a.label}.json'
if out.exists(): raise FileExistsError(out)
members = group(); app_pid = next(k for k, v in members.items() if v == 'Deskworlds')
t0, first = probe(app_pid)
samples = []; prev_cpu = cpu_seconds(members); prev_t = time.monotonic(); end = prev_t + a.duration
while time.monotonic() < end:
    time.sleep(a.interval)
    now = time.monotonic(); cpu = cpu_seconds(members)
    row = {'t': round(now - t0, 2), 'cpu_percent': round(100 * sum(cpu.get(k, 0) - prev_cpu.get(k, 0) for k in members) / (now - prev_t), 2),
           'gpu_device_percent': gpu(), 'footprint_mib': {f'{members[k]}:{k}': (round(v, 1) if v else v) for k in members for v in [footprint(k)]}}
    samples.append(row); prev_cpu, prev_t = cpu, now
t1, last = probe(app_pid)
frames = {}
for wid, s in last.items():
    b = first.get(wid)
    if b and s['frames'] is not None and b['frames'] is not None and s['observedAtMs'] and b['observedAtMs']:
        frames[wid] = {'pixels': s['pixels'], 'frames': s['frames'] - b['frames'],
                       'fps': round(1000 * (s['frames'] - b['frames']) / (s['observedAtMs'] - b['observedAtMs']), 2), 'running': s['running']}
    else:
        frames[wid] = {'pixels': s['pixels'], 'frames': None, 'note': 'page reloaded or not probed at start', 'running': s['running']}
def median(v):
    v = sorted(x for x in v if x is not None); return v[len(v)//2] if v else None
summary = {'label': a.label, 'at': datetime.now().astimezone().isoformat(), 'seconds': round(samples[-1]['t'], 1) if samples else 0,
    'cpu_percent_one_core_mean': round(sum(s['cpu_percent'] for s in samples) / len(samples), 2),
    'gpu_device_percent_median': median([s['gpu_device_percent'] for s in samples]),
    'footprint_last_mib': samples[-1]['footprint_mib'],
    'footprint_gpu_plus_webcontent_last_mib': round(sum(v for k, v in samples[-1]['footprint_mib'].items() if v and ('GPU' in k or 'WebContent' in k)), 1),
    'frames': frames, 'members': {str(k): v for k, v in members.items()}}
out.write_text(json.dumps({'summary': summary, 'samples': samples}, indent=1) + '\n')
print(json.dumps(summary, ensure_ascii=False))

