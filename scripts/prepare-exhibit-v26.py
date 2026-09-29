from pathlib import Path
import subprocess,argparse
from exhibit_overlay import apply_exhibit
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args()
subprocess.run(['python3',str(ROOT/'scripts/prepare-preview.py'),a.name],check=True)
apply_exhibit(ROOT/'preview'/a.name,'v26')
print(ROOT/'preview'/a.name)
