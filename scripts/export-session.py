#!/usr/bin/env python3
"""Create a new, compact source/evidence archive without modifying the aquarium."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
DEST = Path(sys.argv[1]).resolve()
DEST.mkdir(parents=True, exist_ok=False)
SKIP = {'.git', '__pycache__', 'node_modules', '.DS_Store'}


def allowed(path):
    return not any(p in SKIP or p.startswith('.env') for p in path.parts)


def copy(source, relative):
    target = DEST / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def save_json(relative, data):
    target = DEST / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


for directory in ['custom', 'scripts', 'review']:
    for path in sorted((ROOT / directory).rglob('*')):
        if path.is_file() and allowed(path.relative_to(ROOT)):
            if path.is_symlink():
                raise RuntimeError(f'Unexpected symlink: {path}')
            copy(path, path.relative_to(ROOT))
for path in sorted(ROOT.glob('*.md')):
    copy(path, path.name)

# Keep exact historical scene trees; identical bytes are stored only once.
blob_dir = DEST / 'history/blobs'
blob_dir.mkdir(parents=True)
snapshot_counts = {}
for folder in sorted((ROOT / 'preview').iterdir()):
    if not folder.is_dir():
        continue
    entries = {}
    for path in sorted(folder.rglob('*')):
        if not path.is_file() or not allowed(path.relative_to(folder)):
            continue
        if path.is_symlink():
            raise RuntimeError(f'Unexpected symlink: {path}')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        blob = digest + path.suffix
        if not (blob_dir / blob).exists():
            shutil.copy2(path, blob_dir / blob)
        entries[path.relative_to(folder).as_posix()] = {
            'blob': blob, 'sha256': digest, 'bytes': path.stat().st_size,
            'mode': path.stat().st_mode & 0o777,
        }
    save_json(f'history/previews/{folder.name}.json', entries)
    snapshot_counts[folder.name] = len(entries)

# Preserve earlier editable backups and generated native patches, not app bundles.
for folder in sorted((ROOT / 'rollback').iterdir()):
    if not folder.is_dir() or folder.name.startswith('2026'):
        continue
    for path in sorted(folder.rglob('*')):
        if path.is_file() and allowed(path.relative_to(folder)) and path.suffix in {'.js', '.mjs', '.py', '.swift', '.md', '.json', '.txt', '.html', '.css'}:
            copy(path, Path('history/source-backups') / path.relative_to(ROOT / 'rollback'))
for path in sorted((ROOT / 'build').glob('*/Wallpaper.swift')):
    copy(path, Path('history/native-builds') / path.parent.name / path.name)

images = {
    'user-selected-guppy-reference.png', 'v29-r15-wallpaper-1789x1006.png',
    'v29-r15-side-r14-vs-r15.png', 'v29-r15-head-r14-vs-r15.png',
    'v29-r15-atlas-r14-vs-r15.png', 'v29-r15-front-r14-vs-r15.png',
    'v29-r15-shadow-r14-vs-r15.png',
}
inventory = []
for path in sorted((ROOT / 'evidence').iterdir()):
    if not path.is_file():
        continue
    # Process samples/runtime logs can contain unrelated windows/process metadata.
    include = path.suffix in {'.json', '.md', '.patch'} or path.name in images
    if path.suffix == '.log':
        include = any(x in path.name for x in ['check', 'test', 'syntax', 'regression', 'anatomy', 'shape-swim', 'living-water'])
    if include:
        copy(path, Path('evidence') / path.name)
    inventory.append({'path': 'evidence/' + path.name, 'bytes': path.stat().st_size,
                      'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                      'included': include,
                      'reason': 'included' if include else 'local-only capture, video, runtime or machine diagnostic'})
save_json('history/evidence-inventory.json', inventory)
save_json('history/archive-summary.json', {
    'revision': 'bronze-gradient-guppy-v29-r16',
    'upstream': '3950c45ef5798ed2df9f78037994bcddacebbb01',
    'previews': snapshot_counts,
    'unique_preview_blobs': len(list(blob_dir.iterdir())),
    'unique_preview_bytes': sum(p.stat().st_size for p in blob_dir.iterdir()),
    'evidence_included': sum(p['included'] for p in inventory),
    'evidence_local_only': sum(not p['included'] for p in inventory),
})
print(json.dumps(json.loads((DEST / 'history/archive-summary.json').read_text()), ensure_ascii=False))
