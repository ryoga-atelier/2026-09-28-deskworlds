"""Isolated reference study. Canonical local source; never installs or edits upstream."""
from pathlib import Path
import argparse, subprocess, shutil
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('name'); a=p.parse_args()
subprocess.run(['python3',str(ROOT/'scripts/prepare-preview.py'),a.name],check=True)
f=ROOT/'preview'/a.name/'scenes/riverscape/src'
for source in (ROOT/'custom/realism-v15').glob('*.js'):
 if not source.name.startswith('exhibit-'): shutil.copy2(source,f/source.name)
print('Isolated v15 prototype:',f)
