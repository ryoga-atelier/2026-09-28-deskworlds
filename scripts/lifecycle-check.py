#!/usr/bin/env python3
"""Read-only Mac verification, with explicit baseline and user observation records.

Never sleeps, logs out, changes preferences, or synthesizes UI actions.
Only writes its own evidence JSON. Diagnostics observe real app events.
"""
import argparse
from collections import defaultdict
from datetime import datetime
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidence'
LOG = EVIDENCE / 'deskworlds-runtime.log'
BASELINE = EVIDENCE / 'lifecycle-baseline.json'
MANUAL = EVIDENCE / 'lifecycle-user-observations.jsonl'
LABEL = 'com.chaselean.deskworlds'
APP = Path.home() / 'Applications/Deskworlds.app'


def now():
    return datetime.now().astimezone().isoformat()


def machine():
    job = subprocess.run(['launchctl', 'print', f'gui/{os.getuid()}/{LABEL}'],
                         text=True, capture_output=True)
    fields = {}
    for name in ('state', 'pid', 'asid', 'runs', 'program'):
        match = re.search(r'^\t' + name + r' = (.+)$', job.stdout, re.M)
        fields[name] = match.group(1) if match else None
    fields['loaded'] = job.returncode == 0
    agent_path = Path.home() / 'Library/LaunchAgents' / f'{LABEL}.plist'
    agent = plistlib.loads(agent_path.read_bytes()) if agent_path.exists() else {}
    fields['run_at_load'] = agent.get('RunAtLoad') is True
    fields['agent_program'] = agent.get('ProgramArguments', [None])[0]
    fields['expected_program'] = str(APP / 'Contents/MacOS/Deskworlds')
    processes = subprocess.run(['ps', '-axo', 'pid=,comm='], text=True, capture_output=True)
    fields['app_pids'] = []
    for line in processes.stdout.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and parts[1] == fields['expected_program']:
            fields['app_pids'].append(parts[0])
    prefs = {}
    for key in ('world', 'paused'):
        value = subprocess.run(['defaults', 'read', LABEL, key], text=True,
                               capture_output=True)
        prefs[key] = value.stdout.strip() if value.returncode == 0 else None
    return {'at': now(), 'job': fields, 'preferences': prefs}


def parse(text):
    rows = []
    for line in text.splitlines():
        match = re.search(r'Deskworlds\[(\d+):\d+\] deskworlds (lifecycle|page state): (.*)', line)
        if not match:
            continue
        try:
            data = json.loads(match[3])
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            rows.append({'pid': match[1], 'kind': match[2], 'data': data})
    return rows


def summarize(rows, baseline, current, manual=()):
    events = [r for r in rows if r['kind'] == 'lifecycle']
    pages = [r for r in rows if r['kind'] == 'page state']
    samples = defaultdict(lambda: defaultdict(list))
    for row in pages:
        p = row['data']
        if p.get('probeEventID') and p.get('windowID') and p.get('stats'):
            samples[(row['pid'], p['probeEventID'])][p['windowID']].append(p)

    def windows(event):
        return samples.get((event['pid'], event['data'].get('eventID')), {})

    def advancing(event):
        # Actual render count AND fish/water/foliage clocks must advance together.
        for group in windows(event).values():
            first, last = group[0], group[-1]
            a, b = first['stats'], last['stats']
            if (last['observedAtMs'] - first['observedAtMs'] >= 1000
                    and b.get('renderedFrames', 0) > a.get('renderedFrames', 0)
                    and b.get('simulationTime', 0) > a.get('simulationTime', 0)
                    and b.get('livingWater', {}).get('time', 0) > a.get('livingWater', {}).get('time', 0)
                    and b.get('habitat', {}).get('motionTime', 0) > a.get('habitat', {}).get('motionTime', 0)):
                return True
        return False

    def frozen(event):
        groups = windows(event)
        if not groups:
            return False
        for group in groups.values():
            a, b = group[0], group[-1]
            if b['observedAtMs'] - a['observedAtMs'] < 5000:
                return False
            for p in group:
                s = p['stats']
                if s.get('loop', {}).get('running') is not False:
                    return False
                if s.get('renderedFrames') != a['stats'].get('renderedFrames'):
                    return False
                for name, key in (('livingWater', 'time'), ('habitat', 'motionTime')):
                    if s.get(name, {}).get(key) != a['stats'].get(name, {}).get(key):
                        return False
        return True

    def of(name):
        return [e for e in events if e['data'].get('event') == name]

    def status(ok, detail):
        return {'status': 'observed' if ok else 'pending', 'detail': detail}

    job = current['job']
    configured = (job.get('loaded') and job.get('run_at_load')
                  and job.get('agent_program') == job.get('expected_program'))
    launch = [e for e in of('launch') if e['pid'] in job.get('app_pids', [job.get('pid')])]
    feed = any(p['stats'].get('food', {}).get('dropped', 0) > 0
               for e in of('menu-feed') for g in windows(e).values() for p in g)
    # Pair real system notifications in order and in the same process.
    sleep_pids = set()
    wake_proof = False
    pause_pids = set()
    pause_resume = False
    quit_pids = set()
    terminated = False
    for e in events:
        name, pid = e['data'].get('event'), e['pid']
        if name == 'system-will-sleep':
            sleep_pids.add(pid)
        elif name == 'system-did-wake' and pid in sleep_pids:
            # Unlock can supersede the wake sample series. Accept a later active
            # event only after a real matched wake, within the same process.
            if advancing(e):
                wake_proof = True
        elif name == 'display-or-session-active' and pid in sleep_pids:
            prior = events[:events.index(e)]
            if any(x['pid'] == pid and x['data'].get('event') == 'system-did-wake'
                   for x in prior) and advancing(e):
                wake_proof = True
        if name == 'menu-pause' and frozen(e):
            pause_pids.add(pid)
        elif name == 'menu-resume' and pid in pause_pids and advancing(e):
            pause_resume = True
        if name == 'menu-quit':
            quit_pids.add(pid)
        elif name == 'application-will-terminate' and pid in quit_pids:
            terminated = True
    old_asid = baseline['machine']['job'].get('asid')
    new_asid = job.get('asid')
    relogin = (old_asid is not None and new_asid is not None and old_asid != new_asid
               and configured and job.get('state') == 'running'
               and any(advancing(e) for e in launch if e['pid'] == job.get('pid'))
               and current['preferences'] == baseline['machine']['preferences'])
    checks = {
        'login_registration': status(configured, 'Dedicated LaunchAgent and RunAtLoad; registration alone is not login proof.'),
        'startup_rendering': status(any(advancing(e) for e in launch), 'At least one display advances real frames and all animation clocks.'),
        'native_menu': status(bool(of('menu-open')), 'Native menu delegate event; not a browser control.'),
        'native_feed': status(feed, 'Native Feed event plus actual food counter; feeding appearance still requires observation.'),
        'native_pause_resume': status(pause_resume, 'At least 5 seconds frozen, followed by actual native Resume and advancing frames.'),
        'native_quit': status(terminated, 'Native Quit event followed by application termination.'),
        'system_sleep_wake': status(wake_proof, 'Matched OS system sleep/wake plus subsequent animation; lock/display sleep alone cannot pass.'),
        'relogin_autostart': status(relogin, 'New GUI audit session, registered agent process, actual launch rendering, and matching saved settings.'),
    }
    for key in ('dock', 'desktop_drag', 'visual_after_wake', 'visual_after_login'):
        records = [r for r in manual if r.get('check') == key]
        checks[key] = {'status': 'user_reported_' + records[-1]['result'] if records else 'pending',
                       'detail': records[-1]['note'] if records else 'Requires user observation; native app logs cannot prove this.'}
    return {'checked_at': current['at'], 'checks': checks,
            'baseline_asid': old_asid, 'current_asid': new_asid,
            'lifecycle_events': [dict(e['data'], log_pid=e['pid']) for e in events],
            'page_samples': len(pages), 'current': current}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['baseline', 'inspect', 'record'])
    parser.add_argument('--check', choices=['dock', 'desktop_drag', 'visual_after_wake', 'visual_after_login'])
    parser.add_argument('--result', choices=['pass', 'fail'])
    parser.add_argument('--note')
    args = parser.parse_args()
    if args.command == 'baseline':
        if BASELINE.exists():
            raise SystemExit('Baseline exists; preserve it. Do not erase previous sleep/login evidence.')
        data = LOG.read_bytes()
        # Include the currently running app's launch so setup can be verified.
        current = machine()
        needle = f'Deskworlds[{current["job"]["pid"]}:'.encode()
        offset, found = 0, len(data)
        for line in data.splitlines(keepends=True):
            if needle in line and b'deskworlds lifecycle:' in line and b'"event":"launch"' in line:
                found = offset
            offset += len(line)
        baseline = {'at': now(), 'machine': current, 'log_inode': LOG.stat().st_ino,
                    'log_offset': found, 'manifest': json.loads((EVIDENCE / 'manifest.json').read_text())}
        BASELINE.write_text(json.dumps(baseline, ensure_ascii=False, indent=2) + '\n')
        print(BASELINE)
        return
    if args.command == 'record':
        if not all((args.check, args.result, args.note)):
            parser.error('record requires --check, --result, --note quoting the actual user observation')
        with MANUAL.open('a') as out:
            out.write(json.dumps({'at': now(), 'check': args.check, 'result': args.result,
                                  'note': args.note, 'source': 'user_report'}, ensure_ascii=False) + '\n')
        print(MANUAL)
        return
    baseline = json.loads(BASELINE.read_text())
    if LOG.stat().st_ino != baseline['log_inode'] or LOG.stat().st_size < baseline['log_offset']:
        raise SystemExit('Runtime log was replaced/truncated; evidence needs manual reconciliation.')
    with LOG.open('rb') as inp:
        inp.seek(baseline['log_offset'])
        rows = parse(inp.read().decode(errors='replace'))
    manual = [json.loads(line) for line in MANUAL.read_text().splitlines()] if MANUAL.exists() else []
    report = summarize(rows, baseline, machine(), manual)
    output = EVIDENCE / ('lifecycle-check-' + datetime.now().strftime('%Y%m%dT%H%M%S%f') + '.json')
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'report': str(output), 'checks': report['checks']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
