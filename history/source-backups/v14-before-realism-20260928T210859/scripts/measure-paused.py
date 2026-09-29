"""Measure actual paused rendering, then restore only this app's preference and job."""
import argparse,json,subprocess,time,runpy
from provision import ROOT,LABEL,stop_agent

p=argparse.ArgumentParser();p.add_argument('--revision',required=True);a=p.parse_args()
if not a.revision.isalnum():raise ValueError('Plain revision required')
h=runpy.run_path(str(ROOT/'scripts/verify-native-states.py'))
run,processes,start=(h[k] for k in ('run','processes','start'))
output=ROOT/'evidence'/f'{a.revision}-pause-cycle.json'
if output.exists():raise FileExistsError(output)
before={'paused':run('defaults','read',LABEL,'paused'),'world':run('defaults','read',LABEL,'world')}
report={'before':before,'kind':'saved app pause preference and ordinary restart; not a native menu test'}
try:
    stop_agent();time.sleep(3);old={p['pid'] for p in processes()}
    subprocess.run(['defaults','write',LABEL,'paused','-bool','true'],check=True)
    pid=start();time.sleep(8)
    active=[p for p in processes() if p['pid'] not in old]
    if len(active)!=5 or pid not in [p['pid'] for p in active]:raise RuntimeError('Process attribution uncertain')
    report['processes']=active
    tasks=[['python3',str(ROOT/'scripts/measure-v7.py'),'--pids',*[str(p['pid'])for p in active],
      '--label',a.revision+'-paused','--duration','90','--interval','2','--output',str(ROOT/'evidence'/f'{a.revision}-load-paused.json')],
      ['python3',str(ROOT/'scripts/sample-native-frames.py'),'--pid',str(pid),'--duration','90',
       '--output',str(ROOT/'evidence'/f'{a.revision}-frames-paused.json')]]
    children=[subprocess.Popen(t,stdout=subprocess.DEVNULL)for t in tasks]
    report['exit_codes']=[c.wait()for c in children]
    if any(report['exit_codes']):raise RuntimeError('Measurement failed')
finally:
    stop_agent()
    subprocess.run(['defaults','write',LABEL,'paused','-bool','true'if before['paused']=='1'else'false'],check=True)
    report['restored_pid']=start()
    report['after']={'paused':run('defaults','read',LABEL,'paused'),'world':run('defaults','read',LABEL,'world')}
    output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
