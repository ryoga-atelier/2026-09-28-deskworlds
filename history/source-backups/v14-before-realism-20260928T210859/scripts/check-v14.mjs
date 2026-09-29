import assert from 'node:assert/strict';
import {register} from 'node:module';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const root=pathToFileURL(resolve(process.argv[2])+'/');
register(new URL('scenes/riverscape/tests/three-loader.mjs',root));
const THREE=await import(new URL('vendor/three.module.js',root));
const {GUPPY_PALETTE,GUPPY_VARIANTS}=await import(new URL('scenes/riverscape/src/guppy-palette.js',root));
const expected=[3,3,4,2,2,4,3,3];
assert.equal(GUPPY_VARIANTS.length,24);
assert.deepEqual(expected,GUPPY_PALETTE.map((p,i)=>GUPPY_VARIANTS.filter(n=>n===i).length));
assert.equal(new Set(GUPPY_PALETTE.map(p=>p.fin)).size,8);
const {makeAnatomy,applySkin}=await import(new URL('scenes/riverscape/src/fish-anatomy.js',root));
let peakWidth=0,peakBelly=0,referenceWidth=0,actualWidth=0;
for(const [name,g]of Object.entries(makeAnatomy())) {
 const p=g.attributes.position,old=g.attributes.aPigmentPoint,n=g.attributes.normal,parts=g.attributes.aPart;
 for(const i of g.index.array){
  assert.ok([p.getX(i),p.getY(i),p.getZ(i),n.getX(i),n.getY(i),n.getZ(i)].every(Number.isFinite));
  assert.ok(Math.abs(Math.hypot(n.getX(i),n.getY(i),n.getZ(i))-1)<1e-4,'Rendered normals stay normalized');
  assert.equal(p.getX(i),old.getX(i),'Standard length remains unchanged');
  if(old.getX(i)<-.18||old.getX(i)>.30) {
   assert.equal(p.getY(i),old.getY(i),'Tail and snout stay anchored');
   assert.equal(p.getZ(i),old.getZ(i));
  }
  if(parts.getX(i)===0&&old.getX(i)>.04&&old.getX(i)<.19){
   peakBelly=Math.max(peakBelly,old.getY(i)-p.getY(i));
   referenceWidth=Math.max(referenceWidth,Math.abs(old.getZ(i)));
   actualWidth=Math.max(actualWidth,Math.abs(p.getZ(i)));
   if(Math.abs(old.getZ(i))>.005)peakWidth=Math.max(peakWidth,Math.abs(p.getZ(i)/old.getZ(i)));
  }
 }
}
assert.ok(peakWidth>1.17&&peakWidth<1.181,'Forward torso actually gains the approved width');
assert.ok(peakBelly>.008&&peakBelly<.012,'The ventral contour gains modest fullness');
const probe={uniforms:{},vertexShader:THREE.ShaderLib.physical.vertexShader,fragmentShader:THREE.ShaderLib.physical.fragmentShader};
applySkin(probe);
assert.ok(probe.fragmentShader.includes('guppyBodyColor()')&&probe.fragmentShader.includes('guppyFinColor()'));
console.log(JSON.stringify({pass:true,counts:expected,peakWidth,peakBelly,referenceWidth,actualWidth,notes:'Eyes and fin roots use the same smooth body warp; original pigment coordinates preserved.'}));
