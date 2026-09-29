"""Verify one installed revision after an ordinary app restart, without OS UI changes."""
import argparse
import json
import subprocess
import runpy
from provision import ROOT, LABEL, stop_agent, loaded

helpers = runpy.run_path(str(ROOT / 'scripts/verify-native-states.py'))
processes, start, run = (helpers[k] for k in ('processes', 'start', 'run'))
p = argparse.ArgumentParser()
p.add_argument('--revision', required=True)
p.add_argument('--duration', default=90, type=int)
a = p.parse_args()
if not a.revision.isalnum():
    raise ValueError('Revision must be alphanumeric')
prefix = ROOT / 'evidence' / a.revision
report_file = prefix.with_name(prefix.name + '-refresh.json')
if report_file.exists():
    raise FileExistsError(report_file)
report = {'before_pause': run('defaults', 'read', LABEL, 'paused'),
          'before_world': run('defaults', 'read', LABEL, 'world')}
try:
    before = processes()
    stop_agent()
    import time
    time.sleep(3)
    stopped = processes()
    stopped_ids = {x['pid'] for x in stopped}
    report['exited'] = [x for x in before if x['pid'] not in stopped_ids]
    pid = start()
    active = [x for x in processes() if x['pid'] not in stopped_ids]
    if len(active) != 5 or pid not in [x['pid'] for x in active]:
        raise RuntimeError('Unexpected replacement process group; measurement not attributed')
    report.update(pid=pid, processes=active,
        after_pause=run('defaults', 'read', LABEL, 'paused'),
        after_world=run('defaults', 'read', LABEL, 'world'))
    report['preferences_preserved'] = (report['before_pause'] == report['after_pause']
        and report['before_world'] == report['after_world'])
    tasks = [
        ['python3', str(ROOT/'scripts/measure-v7.py'), '--pids',
         *[str(x['pid']) for x in active], '--label', a.revision+'-native-running',
         '--duration', str(a.duration), '--interval', '2', '--output', str(prefix)+'-load-running.json'],
        ['python3', str(ROOT/'scripts/sample-native-frames.py'), '--pid', str(pid),
         '--duration', str(a.duration), '--output', str(prefix)+'-frames-running.json']]
    children = [subprocess.Popen(command) for command in tasks]
    codes = [child.wait() for child in children]
    report['measurement_exit_codes'] = codes
    if any(codes):
        raise RuntimeError('Measurement failed')
finally:
    if not loaded():
        report['recovery_pid'] = start()
    report_file.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
