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
assert.ok(Math.max(...tips.map(i=>p.getY(i))) - Math.min(...tips.map(i=>p.getY(i))) > 0.35,
  'Reference-led rounded tail must remain broad while retaining a narrow caudal peduncle');
const scene = new THREE.Scene(), school = createFishSchool(scene);
const body = scene.getObjectByName('Silver-blue freshwater fish');
const membrane = scene.getObjectByName('Attached translucent fish fins');
const colors = body.geometry.getAttribute('aGuppyVariant');
assert.equal(colors.count, COUNT);
assert.equal(colors, membrane.geometry.getAttribute('aGuppyVariant'));
assert.ok(new Set(colors.array).size >= 5, 'Five or more natural guppy colour families should appear');
const before = [...colors.array];
const seeds = body.geometry.getAttribute('aGuppySeed');
assert.equal(seeds.count, COUNT);
assert.equal(seeds, membrane.geometry.getAttribute('aGuppySeed'));
assert.equal(new Set(seeds.array).size, COUNT, 'Every fish needs its own stable pattern');
const seedBefore = [...seeds.array];
let lastPhases = school.fish.map(f => f.finPhase);
for (let frame=0;frame<600;frame++) {
  school.update(1/60,frame/60,null);
  for (let i=0;i<COUNT;i++) {
    const delta=school.fish[i].finPhase-lastPhases[i];
    assert.ok(delta>=0 && delta<0.8, 'Fin phase must not jump when residual membrane waves cross 2pi');
    lastPhases[i]=school.fish[i].finPhase;
  }
}
const bodyP=geometries.body.getAttribute('position'),bodyParts=geometries.body.getAttribute('aPart');
const peduncle=Array.from({length:bodyP.count},(_,i)=>i).filter(i=>bodyParts.getX(i)===0 && bodyP.getX(i)<-0.26);
for(let i=0;i<p.count;i++) if(parts.getX(i)===1 && reach.getX(i)<0.001) {
  const distance=Math.min(...peduncle.map(j=>Math.hypot(p.getX(i)-bodyP.getX(j),p.getY(i)-bodyP.getY(j),p.getZ(i)-bodyP.getZ(j))));
  assert.ok(distance<0.015,'Caudal membrane root must remain seated in the peduncle');
}
assert.deepEqual([...colors.array], before, 'Individual colors must stay fixed while swimming');
assert.deepEqual([...seeds.array], seedBefore, 'Markings must stay attached to each individual');
school.dispose();
console.log('PASS: finite guppy meshes, valid indices, fan outline, no adipose fin, stable varieties, 24 individual patterns, continuous fin phases and attached caudal roots');
