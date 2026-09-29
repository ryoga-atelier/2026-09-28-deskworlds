"""Attribute CPU samples only when native requested rate is unchanged across a sample."""
from pathlib import Path
import subprocess,time,re,json,sys
root=Path(__file__).resolve().parents[1];pids=list(map(int,sys.argv[1:]));native=pids[0]
def read():
 out=subprocess.check_output(['ps','-o','pid=,time=,rss=','-p',','.join(map(str,pids))],text=True)
 cpu=rss=0
 for line in out.splitlines():
  pid,t,m=line.split();n=0
  for a in t.split(':'):n=n*60+float(a)
  cpu+=n;rss+=int(m)/1024
 log=(root/'evidence/deskworlds-runtime.log').read_text()
 rates=re.findall(r'Deskworlds\['+str(native)+r':\d+\] deskworlds: (\d+) fps',log)
 return time.monotonic(),cpu,rss,rates
samples=[];a=read()
for _ in range(24):
 time.sleep(1);b=read();samples.append({'seconds':b[0]-a[0],'cpu_seconds':b[1]-a[1],'rss_mib':b[2],'requested_fps':int(b[3][-1]) if b[3] else 0,'stable':a[3]==b[3]});a=b
summary={}
for rate in {s['requested_fps'] for s in samples}:
 rows=[s for s in samples if s['stable'] and s['requested_fps']==rate];elapsed=sum(s['seconds'] for s in rows)
 if elapsed:summary[rate]={'seconds':elapsed,'cpu_percent_one_core':100*sum(s['cpu_seconds'] for s in rows)/elapsed,'rss_mib':rows[-1]['rss_mib']}
result={'summary':summary,'samples':samples,'note':'Native request 60 is capped to 30 by Balanced. Transitions excluded. RSS sums can double count shared pages. CPU does not measure GPU power.'}
(root/'evidence/load-livebearer-states.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(summary))
