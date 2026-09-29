"""Apply the local appearance overlay to a disposable scene copy, never upstream."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]


def apply_guppy(scene_root):
    scene_root = Path(scene_root).resolve()
    upstream = (ROOT / 'upstream/deskworlds').resolve()
    if scene_root == upstream or upstream in scene_root.parents:
        raise ValueError('Refusing to modify upstream')
    folder = scene_root / 'scenes/riverscape/src'
    original = folder / 'fish-anatomy.js'
    base = folder / 'fish-anatomy-base.js'
    if base.exists():
        raise FileExistsError('Guppy overlay is already applied')
    shutil.copy2(original, base)
    overlay = ROOT / 'custom/guppy/fish-anatomy.js'
    shutil.copy2(overlay, original)
    fish = folder / 'fish.js'
    text = fish.read_text()
    anchor = '  const { skin: skinMaterial, fins: finMaterial } = createFishMaterials();'
    if text.count(anchor) != 1:
        raise RuntimeError('Upstream material anchor changed')
    addition = '''  const guppyColors = new THREE.InstancedBufferAttribute(
    Float32Array.from({ length: COUNT }, (_, i) => i % 3), 1,
  );
  geometry.body.setAttribute("aGuppyVariant", guppyColors);
  geometry.fins.setAttribute("aGuppyVariant", guppyColors);
'''
    fish.write_text(text.replace(anchor, addition + anchor))
    for name in ('index.html', 'wallpaper.html'):
        path = folder.parent / name
        if path.exists():
            path.write_text(path.read_text().replace('Riverbed', 'Guppy Garden'))
    metadata = {'variant': 'guppy', 'colors': ['coral red', 'gold orange', 'sky blue'],
                'overlay_sha256': hashlib.sha256(overlay.read_bytes()).hexdigest(),
                'scope': 'Riverbed visual anatomy and pigment only; upstream swimming/feeding unchanged'}
    (scene_root / 'guppy-customization.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return metadata
