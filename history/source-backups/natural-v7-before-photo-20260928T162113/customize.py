"""Apply the local appearance overlay to a disposable scene copy, never upstream."""
from pathlib import Path
import hashlib
import json
import shutil
import re
from aquascape import apply_aquascape

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
        '  y: 0.012,': '  y: 0.014,',
        'MOUTH = { cornerX: 0.322, cornerY: -0.0175, tipX: 0.3495, tipY: -0.0035 }': 'MOUTH = { cornerX: 0.322, cornerY: -0.004, tipX: 0.3495, tipY: 0.019 }',
        'radiusX: 0.0335,': 'radiusX: 0.0200,',
        'radiusY: 0.0325,': 'radiusY: 0.0190,',
        'bulge: 0.0126,': 'bulge: 0.0045,',
        'inset: 0.0228,': 'inset: 0.0290,',
        'z -= 0.0023 * Math.exp': 'z -= 0.0009 * Math.exp',
        'z += 0.0013 * Math.exp': 'z += 0.0006 * Math.exp',
        'pupil: 0.60,': 'pupil: 0.71,',
    }.items():
        if anatomy.count(before) != 1:
            raise RuntimeError(f'Upstream eye anchor changed: {before}')
        anatomy = anatomy.replace(before, after)
    # Male livebearer: broad, low skull; abdominal volume forward of the dorsal;
    # a long narrow peduncle. All skin attachments use this same surface profile.
    stations = [
        [0.35,0.024,0.015,0.003,2.2,2.3],
        [0.3425,0.033,0.006,0.010,2.2,2.3],
        [0.332,0.039,-0.006,0.019,2.2,2.3],
        [0.315,0.044,-0.021,0.026,2.2,2.3],
        [0.295,0.048,-0.036,0.033,2.2,2.3],
        [0.272,0.051,-0.050,0.036,2.2,2.3],
        [0.248,0.054,-0.058,0.037,2.2,2.3],
        [0.22,0.057,-0.064,0.036,2.15,2.25],
        [0.19,0.059,-0.069,0.034,2.1,2.2],
        [0.166,0.060,-0.072,0.032,2.05,2.2],
        [0.13,0.061,-0.074,0.030,2.05,2.15],
        [0.09,0.060,-0.070,0.027,2.0,2.1],
        [0.045,0.057,-0.063,0.024,1.95,2.05],
        [0.01,0.054,-0.056,0.0215,1.9,2.0],
        [-0.04,0.047,-0.047,0.019,1.85,1.9],
        [-0.09,0.040,-0.038,0.016,1.75,1.75],
        [-0.14,0.032,-0.030,0.013,1.65,1.65],
        [-0.19,0.026,-0.024,0.0105,1.5,1.5],
        [-0.235,0.022,-0.022,0.0085,1.45,1.45],
        [-0.27,0.0215,-0.0215,0.0065,1.4,1.4],
        [-0.295,0.022,-0.022,0.0045,1.4,1.4],
    ]
    anatomy, count = re.subn(r'const STATIONS = \[.*?\n\];',
        'const STATIONS = ' + json.dumps(stations) + ';', anatomy, flags=re.S)
    if count != 1:
        raise RuntimeError('Upstream body profile changed')
    anatomy = anatomy.replace('const MEMBRANE_STEPS = 8;', 'const MEMBRANE_STEPS = 18;')
    base.write_text(anatomy)
    overlay = ROOT / 'custom/guppy/fish-anatomy.js'
    shutil.copy2(overlay, original)
    fish = folder / 'fish.js'
    text = fish.read_text()
    anchor = '  const { skin: skinMaterial, fins: finMaterial } = createFishMaterials();'
    if text.count(anchor) != 1:
        raise RuntimeError('Upstream material anchor changed')
    addition = '''  const guppyColors = new THREE.InstancedBufferAttribute(
  Float32Array.from({ length: COUNT }, (_, i) => i % 5), 1,
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
    motion = ROOT / 'custom/guppy/swimming.js'
    shutil.copy2(motion, folder / 'guppy-swimming.js')
    text = 'import { GUPPY_SWIM_GLSL } from "./guppy-swimming.js";\n' + text
    text, count = re.subn(r'const SWIM_GLSL = /\* glsl \*/ `.*?`;',
                         'const SWIM_GLSL = GUPPY_SWIM_GLSL;', text, flags=re.S)
    if count != 1:
        raise RuntimeError('Upstream swimming shader changed')
    phase_anchor = 'f.finPhase = (f.finPhase + dt * TAU * (2.1 + f.effort * 1.5)) % TAU;'
    if text.count(phase_anchor) != 1:
        raise RuntimeError('Upstream fin phase anchor changed')
    text = text.replace(phase_anchor,
        'f.finPhase = (f.finPhase + dt * TAU * (2.7 + f.effort * 1.2) * f.character) % (TAU * 1000);')
    text = text.replace('riverscape-fish-${withColor ? "skin" : "depth"}-4',
                        'guppy-natural-v7-${withColor ? "skin" : "depth"}')
    fish.write_text(text)
    for name in ('index.html', 'wallpaper.html'):
        path = folder.parent / name
        if path.exists():
            path.write_text(path.read_text().replace('Riverbed', 'Guppy Garden'))
    aquascape = apply_aquascape(folder)
    metadata = {'variant': 'guppy', 'revision': 'natural-guppy-v7', 'colors': ['blue grass', 'red mosaic', 'gold snakeskin', 'Japan blue', 'red blonde'],
                'overlay_sha256': hashlib.sha256(overlay.read_bytes()).hexdigest(),
                'motion_sha256': hashlib.sha256(motion.read_bytes()).hexdigest(),
                'scope': 'Slender male guppy anatomy with seated eyes, mouth detail and physical-coordinate caudal pigment; asymmetric grounded aquascape, connected internal filter, neutral transparent water and GPU surface waves; passive actual-frame diagnostics',
                'aquascape': aquascape,
                'customizer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (scene_root / 'guppy-customization.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return metadata
