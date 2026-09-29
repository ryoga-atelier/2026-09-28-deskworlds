"""Loopback-only visual QA; accepts only our named canvas captures under evidence/."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import re,os
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
 def do_POST(self):
  name=self.path.removeprefix('/capture/')
  size=int(self.headers.get('Content-Length','0'))
  if not self.path.startswith('/capture/') or not re.fullmatch(r'(guppy-(side|oblique|front|turn|swim|tank)-(comparison|before|after)|natural-v(?:[789]|10|11)-(side|oblique|front|turn|swim|tank|before|after|metrics)-[A-Za-z0-9-]+|clearwater-(shrimp-v5|guppy-v6)-20\d{6}T\d{6}Z-(before|after|swim|native|fish-closeup))\.(png|webm|json)',name) or not 0<size<80_000_000:
   self.send_error(400);return
  path=ROOT/'evidence'/name
  if path.exists():
   from datetime import datetime
   path.rename(path.with_stem(path.stem+'-'+datetime.now().strftime('%H%M%S')))
  path.write_bytes(self.rfile.read(size));self.send_response(200);self.end_headers();self.wfile.write(b'saved')
os.chdir(ROOT)
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8766)
ThreadingHTTPServer(('127.0.0.1',parser.parse_args().port),Handler).serve_forever()
