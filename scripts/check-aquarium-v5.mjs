// Semantic geometry and motion checks for the clear-water shrimp preview.
import assert from 'node:assert/strict';
import { register } from 'node:module';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const root = pathToFileURL(resolve(process.argv[2]) + '/');
register(new URL('scenes/riverscape/tests/three-loader.mjs', root));
const THREE = await import(new URL('vendor/three.module.js', root));
const { backboardGradient, createAquariumDetails } = await import(new URL('scenes/riverscape/src/aquarium-details.js', root));
const { SURFACE_Y } = await import(new URL('scenes/riverscape/src/water.js', root));
const {
  BODY_CLEARANCE, SHRIMP_COUNT, createShrimpGroup, shrimpPose, shrimpSupportHeight,
} = await import(new URL('scenes/riverscape/src/shrimp.js', root));
const { COUNT, createFishSchool } = await import(new URL('scenes/riverscape/src/fish.js', root));
const { createPlants } = await import(new URL('scenes/riverscape/src/plants.js', root));
const { BACK_CHANNEL_PATCHES } = await import(new URL('scenes/riverscape/src/broadleaf.js', root));

assert.equal(SHRIMP_COUNT, 3, 'A few shrimp should inhabit the foreground');
const modes = new Set(), supports = new Set();
const travelled = new Array(SHRIMP_COUNT).fill(0);
let previous = Array.from({ length: SHRIMP_COUNT }, (_, i) => shrimpPose(i, 0));
for (let frame = 1; frame <= 2400; frame++) {
  const time = frame / 20;
  for (let i = 0; i < SHRIMP_COUNT; i++) {
    const pose = shrimpPose(i, time);
    modes.add(pose.behaviour);
    supports.add(pose.support);
    assert.ok([pose.x, pose.y, pose.z, pose.yaw, pose.walk, pose.foraging].every(Number.isFinite));
    assert.ok(Math.abs(pose.y - shrimpSupportHeight(i, pose.x, pose.z) - BODY_CLEARANCE) < 1e-5,
      `Shrimp ${i} stays seated on its ${pose.support} support`);
    if (pose.behaviour === 'walk')
      travelled[i] += Math.hypot(pose.x - previous[i].x, pose.z - previous[i].z);
    previous[i] = pose;
  }
}
for (const state of ['walk', 'forage', 'hide', 'rest'])
  assert.ok(modes.has(state), `Shrimp behaviour includes ${state}`);
assert.deepEqual([...supports].sort(), ['rock', 'sand', 'wood']);
assert.ok(travelled.every((distance) => distance > 0.5), `Each shrimp walks its substrate: ${travelled}`);

const scene = new THREE.Scene();
const planting = createPlants(scene, { backgroundDensity: 1, backgroundRows: 20, backgroundCols: 2 });
const plantPosition = planting.mesh.geometry.getAttribute('position');
let rearChannelLeafVertices = 0, rearChannelTallLeafVertices = 0;
let rearCanopyLeafVertices = 0, highRearCanopyVertices = 0, openSwimLaneCanopyVertices = 0;
for (let i = 0; i < plantPosition.count; i++) {
  const x = plantPosition.getX(i), y = plantPosition.getY(i), z = plantPosition.getZ(i);
  if (x > -3 && x < 3 && y > 2.4 && z < -6.0) rearChannelLeafVertices++;
  if (x > -3 && x < 3 && y > 4.2 && z < -6.0) rearChannelTallLeafVertices++;
  const inBank = (x > -5.8 && x < -2.0) || (x > 2.0 && x < 5.8);
  if (inBank && y > 5.6 && z < -5.8) rearCanopyLeafVertices++;
  if (inBank && y > 7.2 && z < -5.8) highRearCanopyVertices++;
  if (Math.abs(x) < 1.0 && y > 5.6 && z < -5.8) openSwimLaneCanopyVertices++;
}
assert.ok(rearChannelLeafVertices > 100,
  `Low-contrast rear planting reaches behind the swim channel (${rearChannelLeafVertices} vertices)`);
assert.ok(rearChannelTallLeafVertices > 250,
  `The midwater has a few tall rear stems without closing the upper water (${rearChannelTallLeafVertices} vertices)`);
assert.ok(rearCanopyLeafVertices > 120,
  `Grouped high plants frame the rear banks (${rearCanopyLeafVertices} vertices)`);
assert.ok(highRearCanopyVertices > 60,
  `Tall rear clumps reach closer to the water surface (${highRearCanopyVertices} vertices)`);
assert.ok(openSwimLaneCanopyVertices < 60,
  `The upper centre stays clear instead of becoming a uniform stem row (${openSwimLaneCanopyVertices} vertices)`);
assert.ok(BACK_CHANNEL_PATCHES.length >= 8 && BACK_CHANNEL_PATCHES.every(([x, z]) =>
  Math.abs(x) >= 1.8 && Math.abs(x) <= 3.8 && z >= -5.2 && z <= -1.2),
  'Rear and midground broad-leaf groups soften both channel banks while leaving the middle open');
assert.ok(SURFACE_Y >= 9.6,
  `The visible tank should read as filled to the top rather than show a broad air band (${SURFACE_Y})`);
const shrimp = createShrimpGroup(scene);
assert.equal(shrimp.models.length, SHRIMP_COUNT);
for (const model of shrimp.models) {
  assert.ok(model.contacts.length >= 8, 'Each animal has multiple visible ground-contacting legs');
  for (const p of model.contacts) assert.ok(p.toArray().every(Number.isFinite));
}
for (let t = 0; t <= 60; t += 0.1) {
  shrimp.update(t, 0.1);
  scene.updateMatrixWorld(true);
  for (const model of shrimp.models) {
    assert.ok(model.root.position.toArray().every(Number.isFinite));
    for (const local of model.contacts) {
      const world = model.body.localToWorld(local.clone());
      const gap = world.y - shrimpSupportHeight(model.index, world.x, world.z);
      assert.ok(gap >= -0.015 && gap <= 0.075,
        `Shrimp ${model.index} (${shrimpPose(model.index, t).support}) foot local=${local.toArray().map((n)=>n.toFixed(3))} world=${world.toArray().map((n)=>n.toFixed(3))} root=${model.root.position.toArray().map((n)=>n.toFixed(3))} bodyRotation=${model.body.rotation.z.toFixed(3)} support=${shrimpSupportHeight(model.index, world.x, world.z).toFixed(3)} gap=${gap.toFixed(3)} u`);
    }
  }
}

const aquarium = createAquariumDetails(scene);
assert.equal(backboardGradient(-10), 0);
assert.equal(backboardGradient(8), 1);
assert.ok(backboardGradient(-9.95) - backboardGradient(-10) < 0.0001,
  'The upper end of the backdrop gradient eases in smoothly');
assert.ok(backboardGradient(8) - backboardGradient(7.95) < 0.0001,
  'The upper end of the backdrop gradient eases out smoothly');
let previousShade = backboardGradient(-10), maximumGradientStep = 0;
for (let y = -9.95; y <= 8; y += 0.05) {
  const shade = backboardGradient(y);
  maximumGradientStep = Math.max(maximumGradientStep, Math.abs(shade - previousShade));
  previousShade = shade;
}
assert.ok(maximumGradientStep < 0.0043,
  `Backdrop gradient remains smooth with no horizontal clamping seam (${maximumGradientStep})`);
let frontGlassHighlight = false;
scene.traverse((object) => { frontGlassHighlight ||= object.name.startsWith('Aquarium front glass highlights'); });
assert.ok(frontGlassHighlight);
assert.ok(scene.getObjectByName('Aquarium filter return'));
assert.ok(scene.getObjectByName('Water surface ripple')); 
for (let t = 0; t < 20; t += 0.25) aquarium.update(t);
scene.traverse((object) => {
  const p = object.geometry?.getAttribute?.('position');
  if (p) assert.ok(p.array.every(Number.isFinite), `${object.name || object.type} geometry remains finite`);
});

const school = createFishSchool(scene);
const body = scene.getObjectByName('Silver-blue freshwater fish');
const variants = body.geometry.getAttribute('aGuppyVariant');
assert.equal(variants.count, COUNT);
assert.ok(new Set(variants.array).size >= 5, 'The school has several natural guppy color families');
school.dispose();

console.log(JSON.stringify({
  pass: true, shrimp: SHRIMP_COUNT, shrimpBehaviours: [...modes], supports: [...supports],
  shrimpTravelUnits: travelled.map((n) => Number(n.toFixed(2))), guppies: COUNT,
  colourFamilies: new Set(variants.array).size, rearChannelLeafVertices, rearChannelTallLeafVertices,
  rearCanopyLeafVertices, highRearCanopyVertices, openSwimLaneCanopyVertices,
  rearChannelBroadleafGroups: BACK_CHANNEL_PATCHES.length,
  surfaceY: SURFACE_Y,
  maximumGradientStep: Number(maximumGradientStep.toFixed(5)),
}, null, 2));
