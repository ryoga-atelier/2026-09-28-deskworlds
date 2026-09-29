"""Local planted-tank composition, applied only to a disposable upstream copy."""
from pathlib import Path
import hashlib
import shutil

ROOT = Path(__file__).resolve().parents[1]


def apply_aquascape(folder):
    folder = Path(folder).resolve()
    upstream = (ROOT / 'upstream/deskworlds').resolve()
    if folder == upstream or upstream in folder.parents:
        raise ValueError('Refusing to modify upstream')

    def patch(name, changes):
        path = folder / name
        text = path.read_text()
        for before, after in changes:
            if text.count(before) != 1:
                raise RuntimeError(f'Aquascape anchor changed in {name}: {before}')
            text = text.replace(before, after)
        path.write_text(text)

    layout = ROOT / 'custom/guppy/aquascape-layout.js'
    shutil.copy2(layout, folder / layout.name)
    for name in ('aquarium-details.js', 'shrimp.js'):
        shutil.copy2(ROOT / 'custom/guppy' / name, folder / name)
    patch('main.js', [
        ('renderer.toneMappingExposure = 1.17;', 'renderer.toneMappingExposure = 1.00;'),
        ('new THREE.Color("#050f0c")', 'new THREE.Color("#53645b")'),
        ('new THREE.FogExp2("#16312a", 0.034)', 'new THREE.FogExp2("#718176", 0.0035)'),
        ('new THREE.HemisphereLight(0xc3d7bd, 0x353427, 0.3)',
         'new THREE.HemisphereLight(0xe5efe8, 0x68665a, 0.46)'),
        ('new THREE.DirectionalLight(0xfff8ee, 4.5)', 'new THREE.DirectionalLight(0xfff8ee, 3.0)'),
        ('new THREE.DirectionalLight(0xc2d8e4, 0.44)', 'new THREE.DirectionalLight(0xdce9ef, 0.60)'),
        ('new THREE.DirectionalLight(0xdbf9ba, 0.8)', 'new THREE.DirectionalLight(0xe4efe1, 0.55)'),
        ('new THREE.Color("#253129")', 'new THREE.Color("#36443c")'),
        ('new THREE.Color(0.24, 0.32, 0.29)', 'new THREE.Color(0.34, 0.38, 0.34)'),
        ('new THREE.PlaneGeometry(44, 24)', 'new THREE.PlaneGeometry(44, 24, 96, 48)'),
        ('new THREE.MeshStandardMaterial({ color: 0x1d3a2c, roughness: 1 })',
         'new THREE.MeshStandardMaterial({ color: 0xffffff, vertexColors: true, roughness: 1 })'),
        ('  backboard.position.set(0, 7, -7.2);', '''  // A clear, softly lit back plane: darker planted depths rise to the surface light.
  const backColors = [];
  const backPosition = backboard.geometry.attributes.position;
  const low = new THREE.Color('#203229'), high = new THREE.Color('#708a76');
  for (let i = 0; i < backPosition.count; i++) {
    const t = backboardGradient(backPosition.getY(i));
    const x = backPosition.getX(i), y = backPosition.getY(i);
    const color = low.clone().lerp(high, t);
    // Broad, low-contrast leaf shadows break the single flat green back wall without
    // adding noisy speckles or distracting from the guppies.
    const mottling = Math.sin(x * 0.31 + Math.sin(y * 0.19) * 1.2) *
      Math.sin(y * 0.24 + x * 0.08);
    const centreGlow = 0.055 * Math.exp(-((x / 5.4) ** 2 + ((y + 0.8) / 4.6) ** 2));
    const bankShade = 0.06 * THREE.MathUtils.smoothstep(Math.abs(x), 3.4, 10.0);
    const leafShadow =
      0.045 * Math.exp(-(((x + 4.8) / 2.8) ** 2 + ((y - 1.0) / 1.8) ** 2)) +
      0.04 * Math.exp(-(((x - 5.2) / 3.2) ** 2 + ((y + 2.4) / 2.2) ** 2));
    color.multiplyScalar(0.95 + 0.055 * mottling + centreGlow - bankShade - leafShadow);
    backColors.push(color.r, color.g, color.b);
  }
  backboard.geometry.setAttribute('color', new THREE.Float32BufferAttribute(backColors, 3));
  backboard.position.set(0, 7, -7.2);'''),
        ('...settings, animatedShadows: profile !== "reference",',
         '...settings, backgroundDensity: settings.backgroundDensity * 0.82, animatedShadows: profile !== "reference",'),
        ('import { createFood } from "./food.js";',
         'import { createFood } from "./food.js";\nimport { backboardGradient, createAquariumDetails } from "./aquarium-details.js";\nimport { createShrimpGroup } from "./shrimp.js";'),
        ('  const { obstacles, landmarks } = await createEnvironment(scene);',
         '  const { obstacles, landmarks } = await createEnvironment(scene);\n  const aquarium = createAquariumDetails(scene);'),
        ('  const food = createFood(scene, { thickets: plants.thickets });',
         '  const food = createFood(scene, { thickets: plants.thickets });\n  const shrimp = createShrimpGroup(scene);'),
        ('      food.update(step, time);',
         '      aquarium.update(time);\n      shrimp.update(time, step);\n      food.update(step, time);'),
    ])
    patch('plants.js', [
        ('import { plantStems } from "./stemplants.js";',
         'import { plantStems } from "./stemplants.js";\nimport { woodPoint, WOOD_SCALE } from "./aquascape-layout.js";'),
        ('range(0.044, 0.115)', 'range(0.024, 0.062)'),
        ('range(0.7, 0.88)', 'range(0.50, 0.70)'),
        ('range(0.7, 3.0) * (0.6 + 0.6 * age)', 'range(0.45, 1.9) * (0.6 + 0.6 * age) * Math.min(1, height / 4)'),
        ('0.2 + 0.17 * age', '0.19 + 0.13 * age'),
        ('      0.85,\n      range(0.14, 0.28),', '      0.62,\n      range(0.16, 0.28),'),
        ('minY: 1.2, maxY: 6.5 },\n  { minX: 4.4', 'minY: 0.9, maxY: 4.8 },\n  { minX: 4.4'),
        ('minY: 1.2, maxY: 6.5 },\n];', 'minY: 0.9, maxY: 5.7 },\n];'),
        ('{ minX: -9.6, maxX: -2.6, minZ: -5.7, maxZ: -2.0, clumps: 9 }',
         '{ minX: -9.6, maxX: -3.8, minZ: -5.7, maxZ: -2.7, clumps: 7, height: 0.90 }'),
        ('{ minX: 3.9, maxX: 10.4, minZ: -5.7, maxZ: -2.2, clumps: 7 }',
         '{ minX: 4.8, maxX: 10.4, minZ: -5.7, maxZ: -2.8, clumps: 6, height: 1.04 }'),
        ('{ minX: -2.8, maxX: 3.8, minZ: -5.8, maxZ: -3.6, clumps: 6, height: 0.85 }',
         '{ minX: -3.2, maxX: 3.8, minZ: -5.8, maxZ: -4.1, clumps: 4, height: 0.58 }'),
        ('const grassHeight = (x) => 5.4 + 4.0 * smoothstep(2.0, 7.5, Math.abs(x));',
         'const grassHeight = (x) => 2.7 + 3.0 * smoothstep(2.8, 8.0, Math.abs(x));'),
        ('fernTuft(batch, vec(x, y, z), s, n, onWood);',
         'fernTuft(batch, onWood ? woodPoint(x, y, z) : vec(x, y, z), onWood ? s * WOOD_SCALE : s, n, onWood);'),
    ])
    patch('stemplants.js', [
        ('x: [-10.6, -6.2]', 'x: [-9.2, -4.2]'),
        ('x: [5.6, 10.6]', 'x: [5.0, 9.6]'),
        ('height: [5.4, 10.2]', 'height: [3.2, 5.5]'),
        ('height: [5.2, 10.0]', 'height: [3.8, 6.2]'),
        ('feathery: 0.78', 'feathery: 0.60'),
        ('feathery: 0.74', 'feathery: 0.48'),
        ('feathery: 0.5 }', 'feathery: 0.2 }'),
        ('height: [4.2, 7.6]', 'height: [2.2, 3.8]'),
        ('height: [2.4, 4.2]', 'height: [1.8, 3.3]'),
        ('height: [2.2, 3.4]', 'height: [2.0, 3.0]'),
    ])
    patch('environment.js', [
        ('const TAU = Math.PI * 2;', 'import { woodPoint, WOOD_SCALE } from "./aquascape-layout.js";\n\nconst TAU = Math.PI * 2;'),
        ('];\n// The stones,', '''].map((colony, i) => i < 4 ? {
  ...colony, center: woodPoint(colony.center.x, colony.center.y, colony.center.z),
  radius: colony.radius * WOOD_SCALE,
} : colony);
// The stones,'''),
        ('];\n\nfunction mossCoverage', '''].map(branch => ({
  ...branch,
  p: branch.p.map(point => woodPoint(...point).toArray()),
  r: branch.r * WOOD_SCALE, t: branch.t * WOOD_SCALE,
}));

function mossCoverage'''),
        ('depth: radius * (0.3 + sample() * 0.8)', 'depth: radius * (0.12 + sample() * 0.30)'),
        ('Math.min(0.52, depression * 2.1)', 'Math.min(0.24, depression * 1.1)'),
        ('0x62665d, "#2e4315"', '0x898b80, "#405342"'),
        ('0xc3ad8e, "#334a16"', '0xb4a08a, "#3c5137"'),
        ('0xf4e5c8, "#5a5a26", "#23401a"', '0xe3dccb, "#68684f", "#405039"'),
        ('const debris = 780,\n    bubbles = 120,', 'const debris = 150,\n    bubbles = 12,'),
        ('* vFade * 0.72;', '* vFade * 0.34;'),
    ])
    patch('foliage.js', [
        ('vec3(.55, .85, .30) * (vThin * .9)', 'vec3(.68, .81, .50) * (vThin * .62)'),
    ])
    patch('water.js', [
        ('export const SURFACE_Y = 10;', 'export const SURFACE_Y = 9.8;'),
        ('vec3(0.020, 0.008, 0.012)', 'vec3(0.009, 0.006, 0.007)'),
    ])
    patch('stemplants.js', [
        ('height: [3.2, 5.5]', 'height: [4.8, 7.6]'),
        ('height: [3.8, 6.2]', 'height: [4.6, 7.9]'),
        ('height: [2.2, 3.8]', 'height: [2.8, 5.0]'),
    ])
    patch('stemplants.js', [
        ('''  { x: [4.3, 5.4], z: [-2.9, -1.7], clumps: 3, shoots: [3, 5], height: [2.0, 3.0], exposure: [0.9, 1.1], feathery: 0.1, canopy: 2.4 },
];''', '''  { x: [4.3, 5.4], z: [-2.9, -1.7], clumps: 3, shoots: [3, 5], height: [2.0, 3.0], exposure: [0.9, 1.1], feathery: 0.1, canopy: 2.4 },
  // A softer, less regular planting behind the channel: small mixed groups peek between
  // the side banks, with open water above for the guppies to swim.
  { x: [-6.4, -3.4], z: [-6.8, -6.0], clumps: 5, shoots: [2, 4], height: [3.5, 5.4], exposure: [0.52, 0.76], feathery: 0.58 },
  { x: [3.3, 6.4], z: [-6.8, -6.0], clumps: 5, shoots: [2, 4], height: [3.2, 5.3], exposure: [0.50, 0.74], feathery: 0.55 },
  { x: [-2.8, 2.9], z: [-6.9, -6.35], clumps: 6, shoots: [3, 4], height: [3.8, 5.8], exposure: [0.34, 0.54], feathery: 0.46 },
];'''),
    ])
    patch('stemplants.js', [
        ('{ x: [-9.2, -4.2], z: [-6.0, -3.1], clumps: 11, shoots: [3, 5], height: [4.8, 7.6], exposure: [0.94, 1.16], feathery: 0.60 },',
         '{ x: [-9.2, -4.2], z: [-6.0, -3.1], clumps: 8, shoots: [2, 4], height: [4.8, 7.6], exposure: [0.88, 1.10], feathery: 0.56 },'),
        ('{ x: [5.0, 9.6], z: [-6.0, -3.1], clumps: 10, shoots: [3, 5], height: [4.6, 7.9], exposure: [0.9, 1.12], feathery: 0.48 },',
         '{ x: [5.0, 9.6], z: [-6.0, -3.1], clumps: 7, shoots: [2, 4], height: [4.6, 7.9], exposure: [0.84, 1.08], feathery: 0.46 },'),
        ('{ x: [-2.8, 2.9], z: [-6.9, -6.35], clumps: 6, shoots: [3, 4], height: [3.8, 5.8], exposure: [0.34, 0.54], feathery: 0.46 },',
         '{ x: [-5.4, -2.3], z: [-6.95, -6.25], clumps: 4, shoots: [2, 3], height: [6.9, 8.35], exposure: [0.30, 0.48], feathery: 0.32 },\n  { x: [2.4, 5.4], z: [-6.95, -6.25], clumps: 3, shoots: [2, 3], height: [6.6, 8.1], exposure: [0.30, 0.48], feathery: 0.32 },'),
    ])
    patch('broadleaf.js', [
        ('export function plantForeground(batch) {', '''// Compact crypt rosettes soften the rear channel banks while leaving a clear swim lane.
export const BACK_CHANNEL_PATCHES = Object.freeze([
  [-2.85, -4.55, 0.82, 7, 0.13],
  [-2.15, -3.75, 0.62, 6, 0.27],
  [2.55, -4.65, 0.88, 8, 0.27],
  [3.25, -3.90, 0.60, 6, 0.13],
]);

export function plantForeground(batch) {'''),
        ('    [5.2, -2.85, 0.9, 7, BRONZE],\n  ]) {',
         '    [5.2, -2.85, 0.9, 7, BRONZE],\n    ...BACK_CHANNEL_PATCHES,\n  ]) {'),
    ])
    patch('main.js', [
        ('new THREE.Color("#53645b")', 'new THREE.Color("#708f84")'),
        ('new THREE.FogExp2("#718176", 0.0035)', 'new THREE.FogExp2("#829f94", 0.0035)'),
        ("new THREE.Color('#203229'), high = new THREE.Color('#708a76')",
         "new THREE.Color('#2b433a'), high = new THREE.Color('#839f91')"),
    ])
    patch('environment.js', [
        ('const debris = 150,\n    bubbles = 12,', 'const debris = 82,\n    bubbles = 4,'),
    ])
    patch('composite.js', [
        ('0.022 * 12', '0.016 * 12'),
        ('color*=1.-vignette*.15;', 'color*=1.-vignette*.06;'),
    ])
    return {'revision': 'clearwater-shrimp-v5h',
            'layout_sha256': hashlib.sha256(layout.read_bytes()).hexdigest(),
            'aquarium_sha256': hashlib.sha256((ROOT / 'custom/guppy/aquarium-details.js').read_bytes()).hexdigest(),
            'shrimp_sha256': hashlib.sha256((ROOT / 'custom/guppy/shrimp.js').read_bytes()).hexdigest(),
            'customizer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'description': 'Waterline raised out of the desktop frame, tall asymmetrical rear plant groups, eight rear and midground broadleaf clusters around an open swim lane, brighter clear-water depth; five guppy colour families; contact-grounded shrimp and surface-aware aquarium equipment'}
