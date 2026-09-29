"""The v9 material pass, applied after the preserved v7 composition overlay."""
from pathlib import Path
import shutil
import hashlib

ROOT = Path(__file__).resolve().parents[1]

def apply_natural_tank(folder):
    folder = Path(folder).resolve()
    upstream = (ROOT / 'upstream/deskworlds').resolve()
    if folder == upstream or upstream in folder.parents:
        raise ValueError('Refusing to modify upstream')

    def patch(name, changes):
        path = folder / name
        text = path.read_text()
        for before, after in changes:
            if text.count(before) != 1:
                raise RuntimeError(f'v9 anchor changed in {name}: {before}')
            text = text.replace(before, after)
        path.write_text(text)

    shutil.copy2(ROOT / 'custom/guppy/leaf-material.js', folder / 'leaf-material.js')
    patch('foliage.js', [
        ('import * as THREE from "three";', 'import * as THREE from "three";\nimport { bindLeafMaterial } from "./leaf-material.js";'),
        ('roughness: 0.68,', 'roughness: 0.64,'),
        ('specularIntensity: 0.035,', 'specularIntensity: 0.025,'),
        ('    waterLitShader(shader, {', '    bindLeafMaterial(shader);\n    waterLitShader(shader, {'),
        ('"aquatic-leaves-v7"', '"aquatic-leaves-v9"'),
        ('(vThin * .55)', '(vThin * .38)'),
    ])
    patch('broadleaf.js', [
        ('[j / cols, uvy]', '[j / cols, v]'),
        ('cup = 0.2,', 'cup = 0.30,'),
        ('keel = 0.03,', 'keel = 0.045,'),
        ('(0.9 + 0.1 * vein ** 5)', '(0.97 + 0.03 * vein ** 5)'),
    ])
    patch('plants.js', [
        ('range(0.024, 0.062)', 'range(0.017, 0.040)'),
        ('range(0.45, 1.9) * (0.6 + 0.6 * age) * Math.min(1, height / 4)',
         'range(0.70, 2.4) * (0.45 + 0.85 * age) * Math.min(1, height / 2.5)'),
        ('h * range(0.87, 1)', 'h * (0.97 - 0.30 * age)'),
        ('clumps: 2, height: 0.40', 'clumps: 2, height: 0.68'),
        ('0.19 + 0.13 * age', '0.17 + 0.10 * age'),
    ])
    patch('foliage.js', [
        ('Math.pow(Math.sin(Math.PI * Math.pow(t, 0.58)), 0.34)',
         'Math.pow(Math.sin(Math.PI * Math.pow(t, 0.65)), 0.72)'),
    ])
    patch('main.js', [
        ('import * as THREE from "three";', 'import * as THREE from "three";\nimport { loadLeafMaterial, leafMaterialStatus } from "./leaf-material.js";'),
        ('  const { obstacles, landmarks } = await createEnvironment(scene);', '  await loadLeafMaterial();\n  const { obstacles, landmarks } = await createEnvironment(scene);'),
        ('frameTiming: frameMetrics.stats(),', 'frameTiming: frameMetrics.stats(), leafAsset: leafMaterialStatus(),'),
        ('renderer.toneMappingExposure = 1.00;', 'renderer.toneMappingExposure = 1.06;'),
        ('new THREE.DirectionalLight(0xfff8ee, 3.0)', 'new THREE.DirectionalLight(0xfffaf3, 2.8)'),
        ('backgroundDensity: settings.backgroundDensity * 0.43', 'backgroundDensity: settings.backgroundDensity * 0.64'),
        ("const low = new THREE.Color('#0d191d'), high = new THREE.Color('#40565a');", "const low = new THREE.Color('#080f11'), high = new THREE.Color('#28383b');"),
    ])
    patch('environment.js', [
        ('0x898b80, "#405342"', '0x757b71, "#405342"'),
        ('distance: 0.76 + noise(i, seed, 4) * 0.35', 'distance: 0.70 + noise(i, seed, 4) * 0.38'),
        ('surface(loader, "sand_01", [10, 6], 0xe3dccb, "#68684f", "#405039")', 'surface(loader, "sand_01", [15, 9], 0xf0e6d2, "#79705a", "#4b4e38")'),
        ('sandMaterial.normalScale.set(0.32, 0.32);', 'sandMaterial.normalScale.set(0.20, 0.20);'),
        ('woodMaterial.roughness = 0.86;', 'woodMaterial.roughness = 0.74;'),
        ('rockMaterial.normalScale.set(0.55, 0.55);', 'rockMaterial.normalScale.set(0.65, 0.65);'),
        ('0.44, 0.28 - coverage * 0.10', '0.34, 0.21 - coverage * 0.065'),
        ('samples: woodSamples, count: 800', 'samples: woodSamples, count: 520'),
        ('samples: rockSamples, count: 400', 'samples: rockSamples, count: 280'),
    ])
    return {'revision': 'natural-tank-v9',
            'leaf_sha256': hashlib.sha256((ROOT / 'custom/guppy/assets/aquatic-leaf-v9.png').read_bytes()).hexdigest(),
            'patch_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
