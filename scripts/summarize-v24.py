"""Summarize attributed native measurements without claiming GPU or total RAM use."""
from pathlib import Path
import json
from collections import defaultdict
root=Path(__file__).resolve().parents[1]
rows=[]
for rev in ['v21final','v24final']:
    for state in ['running','covered','paused']:
        load=root/'evidence'/f'{rev}-load-{state}.json'
        frames=root/'evidence'/f'{rev}-frames-{state}.json'
        if not load.exists() or not frames.exists():continue
        d=json.loads(load.read_text()); samples=json.loads(frames.read_text())
        groups=defaultdict(list)
        for sample in samples:
            p=sample['page']
            if p.get('stats'):groups[p.get('windowID',str(p['pixels']))].append(p)
        windows=[]
        for group in groups.values():
            first,last=group[0],group[-1];a,b=first['stats'],last['stats']
            seconds=(last['observedAtMs']-first['observedAtMs'])/1000
            delta=b['renderedFrames']-a['renderedFrames']
            windows.append({'pixels':last['pixels'],'seconds':seconds,'frames_delta':delta,'fps':delta/seconds if seconds else None,'paused':b['loop']['paused'],'running':b['loop']['running'],'water_delta':b['livingWater']['time']-a['livingWater']['time'],'fish_delta':b['fish']['simulationTime']-a['fish']['simulationTime']})
        proc=d['summary']['processes']
        identity_file=root/'evidence'/f"{rev}-{'pause-cycle' if state=='paused' else 'refresh'}.json"
        identities=json.loads(identity_file.read_text())['processes']
        roles={x['pid']:x['command'].split('/')[-1]for x in identities}
        rows.append({'revision':rev,'state':state,'seconds':d['actual_duration_seconds'],'complete':d['completed'] and all(x['complete']for x in proc),'cpu_percent_one_core':sum(x['cpu']['mean_percent_one_core']for x in proc),'windows':windows,'memory_per_pid':[{'pid':x['pid'],'role':roles.get(x['pid'],'unknown'),'start_MiB':x['physical_footprint']['start_bytes']/2**20,'end_MiB':x['physical_footprint']['end_bytes']/2**20,'max_MiB':x['physical_footprint']['max_bytes']/2**20}for x in proc]})
out={'method':'90s per state; same two connected screens, Balanced. libproc attributed app + 4 WebKit processes. CPU 100%=one core; physical footprint per PID, no cross-PID memory sum. Actual submission-frame counters, not monitor presentation timing. GPU and battery not measured.','rows':rows}
(root/'evidence/v24-performance-summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
for row in rows:print(row['revision'],row['state'],round(row['cpu_percent_one_core'],2),[(x['pixels'],x['frames_delta'],round(x['fps'],3))for x in row['windows']])
