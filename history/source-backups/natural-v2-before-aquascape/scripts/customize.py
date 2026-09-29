"""Apply the local appearance overlay to a disposable scene copy, never upstream."""
from pathlib import Path
import hashlib
import json
import shutil
import re

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
    anatomy = original.read_text()
    # Smaller, naturally seated eyes. The base uses these dimensions for both the
    # skull socket and all lens layers, avoiding a detached or painted-on eye.
    for before, after in {
        '  y: 0.012,': '  y: 0.018,',
        'MOUTH = { cornerX: 0.322, cornerY: -0.0175, tipX: 0.3495, tipY: -0.0035 }': 'MOUTH = { cornerX: 0.322, cornerY: -0.0045, tipX: 0.3495, tipY: 0.0145 }',
        'radiusX: 0.0335,': 'radiusX: 0.0255,',
        'radiusY: 0.0325,': 'radiusY: 0.0250,',
        'bulge: 0.0126,': 'bulge: 0.0102,',
        'pupil: 0.60,': 'pupil: 0.64,',
    }.items():
        if anatomy.count(before) != 1:
            raise RuntimeError(f'Upstream eye anchor changed: {before}')
        anatomy = anatomy.replace(before, after)
    # A slimmer livebearer trunk and slightly upturned snout. Editing stations
    # lets the original surface builder keep eyes, mouth and fin insertions attached.
    profile_match = re.search(r'const STATIONS = \[(.*?)\n\];', anatomy, re.S)
    if profile_match is None:
        raise RuntimeError('Upstream body profile changed')
    profile = profile_match.group(1)
    def station(match):
        cells = [value.strip() for value in match.group(1).split(',')]
        x = -0.295 if cells[0] == 'HYPURAL_X' else float(cells[0])
        t = max(0.0, min(1.0, (x - 0.23) / 0.12))
        lift = 0.018 * t * t * (3 - 2 * t)
        cells[1] = f'{float(cells[1]) * 0.90 + lift:.7f}'
        cells[2] = f'{float(cells[2]) * 0.90 + lift:.7f}'
        return '[' + ', '.join(cells) + ']'
    profile = re.sub(r'\[([^\[\]]+)\]', station, profile)
    anatomy = anatomy[:profile_match.start(1)] + profile + anatomy[profile_match.end(1):]
    base.write_text(anatomy)
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
  const guppySeeds = new THREE.InstancedBufferAttribute(
    Float32Array.from({ length: COUNT }, (_, i) => ((i * 17 + 7) % 29) / 29), 1,
  );
  geometry.body.setAttribute("aGuppySeed", guppySeeds);
  geometry.fins.setAttribute("aGuppySeed", guppySeeds);
  geometry.body.setAttribute("aGuppyVariant", guppyColors);
  geometry.fins.setAttribute("aGuppyVariant", guppyColors);
'''
    text = text.replace(anchor, addition + anchor)
    # Shared by the color and depth passes: individual fin proportions and a gentle
    # free-edge ripple use the existing animation phase, adding no timers or RNG calls.
    motion_anchor = '  vec3 finMotion(vec3 p) {'
    if text.count(motion_anchor) != 1:
        raise RuntimeError('Upstream fin-motion anchor changed')
    text = text.replace(motion_anchor, '''  attribute float aGuppyVariant;
  attribute float aGuppySeed;
  vec3 finMotion(vec3 p) {
    if (aPart > 0.5 && aPart < 2.5) {
      float edge = aFinProgress * aFinProgress;
      p.y *= 1.0 + (aGuppySeed - 0.5) * 0.20 * aFinProgress;
      if (aPart < 1.5) {
        p.x = mix(p.x, -0.288 + (p.x + 0.288) * (0.90 + 0.18 * aGuppySeed), aFinProgress);
        p.z += edge * (0.013 * sin(aFinPhase * 0.72 + uv.x * 9.0 + aGuppySeed * 6.0)
          + 0.006 * sin(aFinPhase * 0.93 - uv.x * 16.0));
      }
    }''')
    fish.write_text(text)
    for name in ('index.html', 'wallpaper.html'):
        path = folder.parent / name
        if path.exists():
            path.write_text(path.read_text().replace('Riverbed', 'Guppy Garden'))
    metadata = {'variant': 'guppy', 'revision': 'natural-v2', 'colors': ['red grass inspired', 'gold snakeskin inspired', 'blue grass inspired'],
                'overlay_sha256': hashlib.sha256(overlay.read_bytes()).hexdigest(),
                'scope': 'Natural anatomy, individual pigment, and fin-edge motion; upstream swimming/feeding logic unchanged',
                'customizer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (scene_root / 'guppy-customization.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return metadata
