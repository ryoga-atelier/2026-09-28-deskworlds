// Run against a disposable, customized scene tree: node scripts/check-guppy.mjs <tree>
import assert from 'node:assert/strict';
import { register } from 'node:module';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
const root = pathToFileURL(resolve(process.argv[2]) + '/');
register(new URL('scenes/riverscape/tests/three-loader.mjs', root));
const THREE = await import(new URL('vendor/three.module.js', root));
const { makeAnatomy } = await import(new URL('scenes/riverscape/src/fish-anatomy.js', root));
const { createFishSchool, COUNT } = await import(new URL('scenes/riverscape/src/fish.js', root));
const geometries = makeAnatomy();
for (const geometry of Object.values(geometries)) {
  for (const attribute of Object.values(geometry.attributes))
    assert.ok(attribute.array.every(Number.isFinite), 'All mesh attributes must be finite');
  const position = geometry.getAttribute('position');
  const parts = geometry.getAttribute('aPart');
  for (const index of geometry.index.array) {
    assert.ok(index < position.count, 'Every triangle must reference an existing vertex');
    assert.notEqual(parts.getX(index), 12, 'No adipose fin should be rendered on a guppy');
  }
  assert.ok(geometry.boundingSphere.radius > 0 && geometry.boundingSphere.radius < 2);
}
const fins = geometries.fins, p = fins.getAttribute('position');
const parts = fins.getAttribute('aPart'), reach = fins.getAttribute('aFinProgress');
const tips = Array.from({length:p.count}, (_,i)=>i).filter(i=>parts.getX(i)===1 && reach.getX(i)>0.98);
assert.ok(tips.length > 10, 'Tail outline must be sampled');
assert.ok(Math.max(...tips.map(i=>p.getY(i))) - Math.min(...tips.map(i=>p.getY(i))) > 0.45,
  'Fancy-guppy tail must be broad enough to distinguish from the original tetra');
const scene = new THREE.Scene(), school = createFishSchool(scene);
const body = scene.getObjectByName('Silver-blue freshwater fish');
const membrane = scene.getObjectByName('Attached translucent fish fins');
const colors = body.geometry.getAttribute('aGuppyVariant');
assert.equal(colors.count, COUNT);
assert.equal(colors, membrane.geometry.getAttribute('aGuppyVariant'));
assert.equal(new Set(colors.array).size, 3, 'All three color varieties should appear');
const before = [...colors.array];
for (let frame=0;frame<600;frame++) school.update(1/60,frame/60,null);
assert.deepEqual([...colors.array], before, 'Individual colors must stay fixed while swimming');
school.dispose();
console.log('PASS: finite guppy meshes, valid indices, fan outline, no adipose fin, stable three-color instances');
