"""Install the depth-composited photographic habitat in the staged copy only."""
from pathlib import Path
import shutil
import hashlib

ROOT = Path(__file__).resolve().parents[1]

def apply_photo_habitat(folder):
    folder = Path(folder).resolve()
    upstream = (ROOT/'upstream/deskworlds').resolve()
    if folder == upstream or upstream in folder.parents:
        raise ValueError('Refusing to modify upstream')
    module=ROOT/'custom/guppy/photo-habitat.js'
    shutil.copy2(module,folder/module.name)
    p=folder/'main.js'; text=p.read_text()
    changes=[
      ('import * as THREE from "three";', 'import * as THREE from "three";\nimport { createPhotoHabitat } from "./photo-habitat.js";'),
      ('  const food = createFood(scene,', '  const photoHabitat = await createPhotoHabitat(scene,camera);\n  if(photoHabitat.enabled) renderer.setClearColor(0x000000,0);\n  const food = createFood(scene,'),
      ('  const { target, post, postScene, postCamera } = createComposite(camera, settings);', '  const { target, post, postScene, postCamera } = createComposite(camera, settings);\n  photoHabitat.bindComposite(post);'),
      ('      camera.aspect = bounds.width / bounds.height;', '      camera.aspect = bounds.width / bounds.height;\n      photoHabitat.resize(camera.aspect);'),
      ('frameTiming: frameMetrics.stats(),', 'frameTiming: frameMetrics.stats(), habitat: photoHabitat.stats(),'),
    ]
    for before,after in changes:
        if text.count(before)!=1: raise RuntimeError('Photo habitat anchor changed: '+before)
        text=text.replace(before,after)
    p.write_text(text)
    return {'revision':'photo-depth-v10','module_sha256':hashlib.sha256(module.read_bytes()).hexdigest(),
            'mode':'2.5D AI-generated aquarium with depth occlusion; interactive 3D fish; 3D fallback on asset-load failure'}
