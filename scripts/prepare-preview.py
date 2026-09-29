"""Make a new review tree from pinned source; existing previews are never overwritten."""
from pathlib import Path
import argparse,re,shutil,subprocess
from customize import apply_guppy
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('name');args=parser.parse_args()
if not re.fullmatch(r'[a-z0-9][a-z0-9-]+',args.name):raise SystemExit('Use a plain preview name')
source=root/'upstream/deskworlds'
if subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()!='3950c45ef5798ed2df9f78037994bcddacebbb01':raise SystemExit('Source pin mismatch')
target=root/'preview'/args.name;target.mkdir()
for name in ['scenes','vendor','ui']:shutil.copytree(source/name,target/name)
for name in ['package.json','serve.mjs']:shutil.copy2(source/name,target/name)
apply_guppy(target);print(target)
