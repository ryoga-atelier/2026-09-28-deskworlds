// Run against a disposable, v28-customized scene tree.
import assert from 'node:assert/strict';
import { register } from 'node:module';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const root = resolve(process.argv[2]);
const sceneURL = pathToFileURL(root + '/');
register(new URL('scenes/riverscape/tests/three-loader.mjs', sceneURL));
const { applyPhotographicPigment } = await import(new URL('scenes/riverscape/src/photo-material.js', sceneURL));
const shader = { uniforms: {}, fragmentShader: 'void main() {\n#include <alphamap_fragment>\n#include <normal_fragment_maps>\n#include <lights_physical_fragment>\n' };
applyPhotographicPigment(shader);

assert.ok(/float\s+guppyScaleVariation\s*\(/.test(shader.fragmentShader),
  'Photo-like overlapping scales need per-scale variation, not a uniform stamped grid');
assert.ok(/guppyScaleVariation\s*\(\s*grid\s*\)/.test(shader.fragmentShader),
  'Scale variation must affect the visible edge shape');
assert.ok(/float\s+guppyBellyEdge\s*\(/.test(shader.fragmentShader),
  'The pale belly outline must have subtle organic irregularity');
assert.ok(/float\s+bellyRadius\s*=\s*guppyBellyProfile\s*\([^)]*\)\s*\+\s*guppyBellyEdge\s*\(/.test(shader.fragmentShader),
  'Organic edge variation must be bounded around the curved belly, not replace its shape');
const bellyProfile = shader.fragmentShader.match(/float\s+guppyBellyProfile\s*\([^)]*\)\s*\{([\s\S]*?)\}/);
assert.ok(bellyProfile && /dot\(bellyCoord,bellyCoord\)/.test(bellyProfile[1]),
  'The gill and anal-fin notches must refine the oval belly instead of replacing its base curvature');
assert.ok(/vec3\(\.18,\.11,\.075\)/.test(shader.fragmentShader),
  'Dorsal tissue must retain warm bronze rather than a black or cold-purple field');

const { makeAnatomy } = await import(new URL('scenes/riverscape/src/fish-anatomy.js', sceneURL));
const { profile } = await import(new URL('scenes/riverscape/src/fish-anatomy-base.js', sceneURL));
const dorsal = [0.31, 0.23, 0.13].map(x => profile(x).top);
assert.ok(dorsal[0] < dorsal[1] && dorsal[1] < dorsal[2],
  'The head-to-back silhouette must remain continuously convex');
const abdomen = profile(0.13).top - profile(0.13).bottom;
const peduncle = profile(-0.26).top - profile(-0.26).bottom;
assert.ok(peduncle < abdomen * 0.70,
  'The slim body must taper clearly into the caudal peduncle');
const meshes = makeAnatomy();
const position = meshes.fins.getAttribute('position');
const part = meshes.fins.getAttribute('aPart');
const progress = meshes.fins.getAttribute('aFinProgress');
const tailTips = [];
for (let i = 0; i < position.count; i++)
  if (part.getX(i) === 1 && progress.getX(i) > 0.98) tailTips.push(position.getY(i));
assert.ok(Math.max(...tailTips) - Math.min(...tailTips) > 0.23,
  'The rounded caudal fan must remain legible at desktop scale');
console.log('PASS: bronze layered pigment, naturally varied scales and belly edge, convex slender anatomy, rounded guppy tail');
