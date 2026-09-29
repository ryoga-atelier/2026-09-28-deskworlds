import assert from 'node:assert/strict';
import {register} from 'node:module';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const root=pathToFileURL(resolve(process.argv[2])+'/');register(new URL('scenes/riverscape/tests/three-loader.mjs',root));
const {GUPPY_PALETTE,GUPPY_VARIANTS}=await import(new URL('scenes/riverscape/src/guppy-palette.js',root));
assert.deepEqual(GUPPY_PALETTE.map((p,i)=>GUPPY_VARIANTS.filter(x=>x===i).length),[3,3,4,2,2,4,3,3]);
const {makeAnatomy}=await import(new URL('scenes/riverscape/src/fish-anatomy.js',root));
const shape=makeAnatomy();let tailDepth=0,abdomenDepth=0,width=0;
for(const [key,g]of Object.entries(shape)){const p=g.attributes.position,n=g.attributes.normal,part=g.attributes.aPart;let tailLow=Infinity,tailHigh=-Infinity,low=Infinity,high=-Infinity;
 for(const i of new Set(g.index.array)){assert.ok([p.getX(i),p.getY(i),p.getZ(i),n.getX(i),n.getY(i),n.getZ(i)].every(Number.isFinite));assert.ok(Math.abs(Math.hypot(n.getX(i),n.getY(i),n.getZ(i))-1)<1e-4);
 if(part.getX(i)===0){if(p.getX(i)<-.25){tailLow=Math.min(tailLow,p.getY(i));tailHigh=Math.max(tailHigh,p.getY(i));}if(p.getX(i)>.10&&p.getX(i)<.21){low=Math.min(low,p.getY(i));high=Math.max(high,p.getY(i));width=Math.max(width,Math.abs(p.getZ(i))*2);}}}
 if(key==='body'){tailDepth=tailHigh-tailLow;abdomenDepth=high-low;}}
assert.ok(abdomenDepth>.21&&abdomenDepth<.245,'Forward abdomen retains volume');assert.ok(tailDepth/abdomenDepth>.15&&tailDepth/abdomenDepth<.28,'Explicit user refinement: posterior profile narrows after the rounded abdomen');assert.ok(width>.08&&width<.11,'Guppy cross section remains slender');
console.log(JSON.stringify({pass:true,tailDepth,abdomenDepth,width,colorCounts:[3,3,4,2,2,4,3,3],renderedNormals:'finite/unit'}));
