"""Create a full-scene candidate; no native install."""
from pathlib import Path
import sys,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1]
name=sys.argv[1]
subprocess.run(['python3',str(ROOT/'scripts/prepare-preview.py'),name],check=True)
f=ROOT/'preview'/name/'scenes/riverscape/src'
for name in ['fish-anatomy-base.js','fish-anatomy.js','photo-material.js','guppy-palette.js','guppy-swimming.js','environment.js','main.js','water.js','living-water.js','exhibit-water.js']:
 shutil.copy2(ROOT/'custom/realism-v15'/name,f/name)
shutil.copy2(ROOT/'custom/realism-v15/CAUSTIC-LICENSE.txt',f.parent/'assets/CAUSTIC-LICENSE.txt')
print('Full 3D candidate only:',f)
