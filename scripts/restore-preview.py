#!/usr/bin/env python3
"""Restore an archived comparison tree into a NEW preview folder, checking hashes."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('name', nargs='?', help='Saved preview name, or all')
parser.add_argument('--list', action='store_true')
args = parser.parse_args()
manifests = ROOT / 'history/previews'
if args.list:
    print('\n'.join(p.stem for p in sorted(manifests.glob('*.json'))))
    raise SystemExit(0)
if not args.name or not re.fullmatch(r'[a-z0-9-]+', args.name):
    parser.error('Specify a saved name, all, or --list')
names = [p.stem for p in sorted(manifests.glob('*.json'))] if args.name == 'all' else [args.name]
for name in names:
    entries = json.loads((manifests / (name + '.json')).read_text())
    target = ROOT / 'preview' / name
    if target.exists():
        raise SystemExit(f'Already exists; refusing to overwrite: {target}')
    # Validate the entire manifest and all content before creating the folder.
    for relative, info in entries.items():
        path = PurePosixPath(relative)
        if path.is_absolute() or '..' in path.parts or '\\' in relative:
            raise ValueError(f'Unsafe snapshot path: {relative}')
        if not re.fullmatch(r'[0-9a-f]{64}(\.[A-Za-z0-9_-]+)?', info['blob']):
            raise ValueError('Invalid blob name')
        data = (ROOT / 'history/blobs' / info['blob']).read_bytes()
        if len(data) != info['bytes'] or hashlib.sha256(data).hexdigest() != info['sha256']:
            raise ValueError(f'Corrupt archived file: {relative}')
    target.mkdir(parents=True)
    for relative, info in entries.items():
        out = target / relative
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'history/blobs' / info['blob'], out)
        out.chmod(info['mode'] & 0o777)
    print(f'Restored {name}: {len(entries)} files')
