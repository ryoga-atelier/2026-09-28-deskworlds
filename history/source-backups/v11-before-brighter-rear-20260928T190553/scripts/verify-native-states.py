"""Verify this app's saved pause state, then restore its original preference.

No UI automation or system-wide preferences. Attribution uses the disappearance
and replacement of the previously recorded, dedicated WebKit process group.
"""
import json
import re
import subprocess
import time
from pathlib import Path
from provision import ROOT, AGENT, DOMAIN, LABEL, stop_agent


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def processes():
    result = []
    for line in run('ps', '-axo', 'pid=,comm=').splitlines():
        pid, command = line.strip().split(None, 1)
        if command.endswith(('/Deskworlds', '/com.apple.WebKit.GPU',
                             '/com.apple.WebKit.Networking', '/com.apple.WebKit.WebContent')):
            result.append({'pid': int(pid), 'command': command})
    return result


def start():
    subprocess.run(['launchctl', 'bootstrap', DOMAIN, str(AGENT)], check=True)
    for _ in range(40):
        state = run('launchctl', 'print', f'{DOMAIN}/{LABEL}')
        match = re.search(r'\bpid = (\d+)', state)
        if match:
            pid = int(match.group(1))
            time.sleep(2)
            return pid
        time.sleep(.2)
    raise RuntimeError('App did not start')


def stopped_inventory(old):
    old_ids = {p['pid'] for p in old}
    for _ in range(40):
        current = processes()
        if not old_ids.intersection(p['pid'] for p in current):
            return current
        time.sleep(.2)
    raise RuntimeError('Old attributed processes did not all exit')


if __name__ == '__main__':
    output = ROOT / 'evidence/v11-process-state-cycle.json'
    if output.exists():
        raise FileExistsError(output)
    original_pause = run('defaults', 'read', LABEL, 'paused')
    original_world = run('defaults', 'read', LABEL, 'world')
    before = json.loads((ROOT / 'evidence/v11-processes-running.json').read_text())
    report = {'original_pause': original_pause, 'original_world': original_world, 'before': before}
    try:
        stop_agent()
        empty = stopped_inventory(before)
        report['stopped'] = empty
        subprocess.run(['defaults', 'write', LABEL, 'paused', '-bool', 'true'], check=True)
        paused_pid = start()
        prior = {p['pid'] for p in empty}
        paused = [p for p in processes() if p['pid'] not in prior]
        if len(paused) != 5 or paused_pid not in [p['pid'] for p in paused]:
            raise RuntimeError('Unexpected process group; do not attribute measurements')
        report['paused'] = paused
        report['paused_preference'] = run('defaults', 'read', LABEL, 'paused')
        meter = subprocess.Popen(['python3', str(ROOT/'scripts/measure-v7.py'),
            '--pids', *[str(p['pid']) for p in paused], '--label', 'v11-native-paused',
            '--duration', '60', '--interval', '2', '--output', str(ROOT/'evidence/v11-load-paused.json')])
        probe = subprocess.Popen(['python3', str(ROOT/'scripts/sample-native-frames.py'),
            '--pid', str(paused_pid), '--duration', '60',
            '--output', str(ROOT/'evidence/v11-frames-paused.json')])
        meter_code, probe_code = meter.wait(), probe.wait()
        if meter_code or probe_code:
            raise RuntimeError('Paused measurement did not complete')
    finally:
        stop_agent()
        subprocess.run(['defaults', 'write', LABEL, 'paused', '-bool',
                        'true' if original_pause == '1' else 'false'], check=True)
        report['restored_pid'] = start()
        report['restored'] = processes()
        report['restored_pause'] = run('defaults', 'read', LABEL, 'paused')
        report['restored_world'] = run('defaults', 'read', LABEL, 'world')
        report['preferences_restored'] = (report['restored_pause'] == original_pause
            and report['restored_world'] == original_world)
        output.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'pid': report['restored_pid'],
                          'preferences_restored': report['preferences_restored']}))
