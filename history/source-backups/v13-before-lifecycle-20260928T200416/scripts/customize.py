"""Apply the local appearance overlay to a disposable scene copy, never upstream."""
from pathlib import Path
import hashlib
import json
import shutil
import re
from aquascape import apply_aquascape
from natural_tank import apply_natural_tank
from photo_habitat import apply_photo_habitat

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
    stations = [[0.35, 0.0242, 0.0122, 0.003, 1.9, 2.0], [0.342539, 0.0272, 0.0044, 0.01, 1.9, 2.0], [0.33033, 0.0296, -0.007, 0.016, 1.9, 2.0], [0.312696, 0.0332, -0.0172, 0.023, 1.9, 2.0], [0.292348, 0.0374, -0.0298, 0.03, 1.9, 2.0], [0.272, 0.0416, -0.0394, 0.034, 1.9, 2.0], [0.246373, 0.0476, -0.0484, 0.037, 1.9, 2.0], [0.214339, 0.056, -0.0556, 0.038, 1.9, 2.0], [0.169492, 0.0668, -0.0628, 0.037, 1.9, 2.0], [0.111831, 0.0812, -0.0676, 0.034, 1.9, 2.0], [0.044559, 0.0932, -0.058, 0.03, 1.9, 2.0], [-0.003492, 0.1004, -0.0478, 0.027, 1.9, 2.0], [-0.061153, 0.0914, -0.0358, 0.024, 1.9, 2.0], [-0.122017, 0.0824, -0.0304, 0.021, 1.9, 2.0], [-0.176475, 0.0782, -0.0286, 0.018, 1.9, 2.0], [-0.234136, 0.0722, -0.0292, 0.014, 1.9, 2.0], [-0.272576, 0.0674, -0.0298, 0.011, 1.9, 2.0], [-0.295, 0.0668, -0.0298, 0.009, 1.9, 2.0]]
    anatomy, count = re.subn(r'const STATIONS = \[.*?\n\];',
        'const STATIONS = ' + json.dumps(stations) + ';', anatomy, flags=re.S)
    if count != 1:
        raise RuntimeError('Upstream body profile changed')
    anatomy = anatomy.replace('const MEMBRANE_STEPS = 8;', 'const MEMBRANE_STEPS = 32;')
    base.write_text(anatomy)
    overlay = ROOT / 'custom/guppy/fish-anatomy.js'
    shutil.copy2(overlay, original)
    shutil.copy2(ROOT / 'custom/guppy/photo-material.js', folder / 'photo-material.js')
    asset_root = folder.parent / 'assets'
    asset_root.mkdir(exist_ok=True)
    for asset in (ROOT / 'custom/guppy/assets').iterdir():
        if asset.is_file(): shutil.copy2(asset, asset_root / asset.name)
    shutil.copy2(ROOT / 'custom/guppy/photo-prompt-v8.txt', asset_root / 'photo-prompt-v8.txt')
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
                        'guppy-natural-v11-${withColor ? "skin" : "depth"}')
    # In a calm planted tank guppies explore independently and form loose groups.
    # Keep alarm/feeding mechanics, but avoid the bloodfin's tightly recruited shoal.
    for before, after in {
        'const MAX_EXPLORERS = 7;': 'const MAX_EXPLORERS = 12;',
        '  spacing: 1.05,': '  spacing: 1.32,',
        '  alignment: 0.5,': '  alignment: 0.22,',
        '  cohesion: 0.3,': '  cohesion: 0.14,',
        '  follow: 0.28,': '  follow: 0.18,',
        '  recruitRate: 0.15,': '  recruitRate: 0.08,',
        '        range(2.55, 5.75),': '        range(3.0, 6.8),',
    }.items():
        if text.count(before) != 1: raise RuntimeError('Guppy behaviour anchor changed: '+before)
        text=text.replace(before,after)
    fish.write_text(text)
    for name in ('index.html', 'wallpaper.html'):
        path = folder.parent / name
        if path.exists():
            path.write_text(path.read_text().replace('Riverbed', 'Guppy Garden'))
    aquascape = apply_aquascape(folder)
    aquascape['materials'] = apply_natural_tank(folder)
    aquascape['photo_habitat'] = apply_photo_habitat(folder)
    main = folder / 'main.js'
    main_text = main.read_text()
    main_text = 'import { photoPigmentStatus, loadPhotoPigment } from "./photo-material.js";\n' + main_text
    fish_anchor = '  const fish = createFishSchool(scene, {'
    if main_text.count(fish_anchor)!=1: raise RuntimeError('Fish creation anchor changed')
    main_text = main_text.replace(fish_anchor, '  await loadPhotoPigment();\n'+fish_anchor)
    anchor = 'frameTiming: frameMetrics.stats(),'
    if main_text.count(anchor) != 1: raise RuntimeError('Frame stats anchor changed')
    main.write_text(main_text.replace(anchor, anchor + '\n      pigmentAsset: photoPigmentStatus(),'))
    metadata = {'variant': 'guppy', 'revision': 'living-blue-water-v13', 'colors': ['blue grass', 'red mosaic', 'gold snakeskin', 'Japan blue', 'red blonde'],
                'overlay_sha256': hashlib.sha256(overlay.read_bytes()).hexdigest(),
                'motion_sha256': hashlib.sha256(motion.read_bytes()).hexdigest(),
                'texture_sha256': hashlib.sha256((ROOT/'custom/guppy/assets/red-mosaic-material-v8.png').read_bytes()).hexdigest(),
                'scope': 'Photographic AI pigment plate on a closed anatomical 3D body; fine translucent caudal membrane. Slender male guppy anatomy with seated eyes, mouth detail and physical-coordinate caudal pigment; asymmetric grounded aquascape, connected internal filter, neutral transparent water and GPU surface waves; passive actual-frame diagnostics',
                'aquascape': aquascape,
                'customizer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (scene_root / 'guppy-customization.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return metadata
