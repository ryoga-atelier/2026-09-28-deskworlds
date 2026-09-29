// Run against a disposable customized scene tree. Sample the actual scalar
// GLSL masks: source-string checks missed an outer rim that was zero everywhere.
// Real WebGL comparison remains the appearance test.
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

function glslFunction(name) {
  const start = shader.fragmentShader.search(new RegExp(`\\b${name}\\s*\\([^)]*\\)\\s*\\{`));
  assert.notEqual(start, -1, `${name} must be present in the actual injected fish shader`);
  const open = shader.fragmentShader.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < shader.fragmentShader.length; i++) {
    if (shader.fragmentShader[i] === '{') depth++;
    if (shader.fragmentShader[i] === '}' && --depth === 0) return shader.fragmentShader.slice(open + 1, i);
  }
  assert.fail(`${name} must have a closed function body`);
}

const gradient = glslFunction('guppyLongitudinalTone');
assert.match(gradient, /smoothstep\([^;]*x/s,
  'The head-to-tail tone must be driven by fish position, not a fixed body tint');
assert.match(gradient, /mix\(\s*tailTone\s*,\s*headTone\s*,\s*headToTail\s*\)/,
  'The rear body must transition continuously into a lighter head-side tone');
const channelFactors = label => {
  const match = gradient.match(new RegExp(`vec3 ${label}Tone=skin\\*vec3\\(([^)]+)\\)`));
  assert.ok(match, `${label} tone must expose measurable channel factors`);
  return match[1].split(',').map(Number);
};
const luminance = ([r,g,b]) => .2126*r+.7152*g+.0722*b;
assert.ok(luminance(channelFactors('head')) / luminance(channelFactors('tail')) >= 2.20,
  'The rear-to-head luminance separation must remain visible at normal desktop size');

// These helpers contain scalar GLSL only. Evaluate their actual bodies rather
// than copying the implementation into the test with matching magic numbers.
const smoothstep = (a,b,x) => { const t=Math.min(1,Math.max(0,(x-a)/(b-a))); return t*t*(3-2*t); };
const environment = {smoothstep,exp:Math.exp,pow:Math.pow,max:Math.max,sin:Math.sin,PI2:Math.PI*2,mix:(a,b,t)=>a*(1-t)+b*t};
function scalar(name,args) {
  const body=glslFunction(name).replace(/\bfloat\b/g,'let');
  return new Function(...args,...Object.keys(environment),body);
}
function bindScalar(name,args) {
  const fn=scalar(name,args), values=Object.values(environment);
  return (...valuesIn) => fn(...valuesIn,...values);
}
const outer=bindScalar('guppyBellyOuter',['radius']);
const inner=bindScalar('guppyBellyInner',['radius']);
const seam=bindScalar('guppyBellySeam',['radius','y']);
const radii=Array.from({length:401},(_,i)=>i/200);
const rim=radii.map(r=>outer(r)-inner(r));
for(const r of radii) {
  assert.ok(outer(r)>=inner(r)-1e-8,'Outer tissue must contain inner tissue at every sampled radius');
  assert.ok(outer(r)>=0 && outer(r)<=1 && inner(r)>=0 && inner(r)<=1,'Coverage is bounded');
}
assert.ok(Math.max(...rim)>.5,'Outer tissue must form a visible ring, not a zero-width or cancelled layer');
assert.ok(rim.filter(v=>v>.25).length>15,'The outer layer must occupy a measurable band');
assert.ok(inner(0)>.95 && outer(2)<.01,'Pale tissue fills the centre and does not bleed across the whole fish');
assert.ok(Math.max(...radii.map(r=>seam(r,.02)))>.5,'Upper abdominal seam is present');
assert.ok(Math.max(...radii.map(r=>seam(r,-.075)))<.01,'Seam must not outline the lower belly in black');
assert.ok(seam(0,.02)<.01 && seam(2,.02)<.01,'Boundary shadow must not darken the centre or distant back');

environment.guppyAnalRootIndent=bindScalar('guppyAnalRootIndent',['x','y']);
const anal=bindScalar('guppyAnalPigment',['x','y']);
const patchSamples=[];
for(let xi=0;xi<=60;xi++)for(let yi=0;yi<=40;yi++) {
  const x=-.28+xi*.01,y=-.10+yi*.005,value=anal(x,y);
  assert.ok(Number.isFinite(value) && value>=0 && value<=1,'Anal pigment coverage is finite and bounded');
  patchSamples.push(value);
}
assert.ok(anal(0,-.045)>.6,'Dark pigment must appear on visible tissue just above the anal-fin root');
assert.ok(anal(.11,-.04)<.01 && anal(.20,0)<.01 && anal(0,.075)<.01,'Patch stays away from the main white belly, gill and back');
const analCoverage=patchSamples.filter(v=>v>.25).length/patchSamples.length;
assert.ok(analCoverage>.030 && analCoverage<.055,'The broad rounded marking stays local to the rear abdomen');
assert.ok(anal(.035,-.042)>.5 && anal(.010,-.016)>.5,
  'The marking fills the rear compartment with a rounded edge instead of a low narrow spot');

// Measure rendered head geometry, including the matching corneal ring. A smaller
// shader orbit alone would leave the old large eye mesh floating over the face.
const {makeAnatomy}=await import(new URL('scenes/riverscape/src/fish-anatomy.js',sceneURL));
const {STANDARD_LENGTH,profile,surfacePoint}=await import(new URL('scenes/riverscape/src/fish-anatomy-base.js',sceneURL));
const body=makeAnatomy().body,position=body.attributes.position,part=body.attributes.aPart;
const vertices=(id,side=1)=>Array.from({length:position.count},(_,i)=>i)
  .filter(i=>part.getX(i)===id && Math.sign(position.getZ(i))===side)
  .map(i=>[position.getX(i),position.getY(i),position.getZ(i)]);
const extent=(points,axis)=>Math.max(...points.map(p=>p[axis]))-Math.min(...points.map(p=>p[axis]));
const eye=vertices(10),eyeWidth=extent(eye,0);
assert.ok(eyeWidth/STANDARD_LENGTH>.055 && eyeWidth/STANDARD_LENGTH<.070,
  'The visible eye including its rim stays small relative to the slim body');
assert.ok(Math.abs(eyeWidth-extent(vertices(10,-1),0))<1e-6,'Both eyes must use the same reduced anatomy');
let largestEyeGap=0;
for(const id of [7,8,10])for(const [x,y,z] of vertices(id)) {
  const section=profile(x),middle=(section.top+section.bottom)/2;
  const v=(y-middle)/(y>=middle?section.top-middle:middle-section.bottom);
  const skin=surfacePoint(x,v,1);
  const gap=z-skin.z;
  assert.ok(gap>-.0008 && gap<.003,'The reduced iris, pupil and rim stay seated in their body socket');
  largestEyeGap=Math.max(largestEyeGap,gap);
}
const lips=vertices(9),startX=Math.min(...lips.map(p=>p[0])),tipX=Math.max(...lips.map(p=>p[0]));
const meanY=points=>points.reduce((sum,p)=>sum+p[1],0)/points.length;
const mouthRise=meanY(lips.filter(p=>p[0]>tipX-.003))-meanY(lips.filter(p=>p[0]<startX+.003));
assert.ok(mouthRise>.020 && mouthRise<.035,'The actual mouth opening curves upward toward the snout');

// Fragment derivatives also evaluate helper pixels just outside a fin triangle.
// Negative reach at the root used to feed a fractional power and produce NaNs.
let fold;
if(/float guppyFinFold\(/.test(shader.fragmentShader)) {
  fold=bindScalar('guppyFinFold',['u','reach']);
} else {
  const expression=shader.fragmentShader.match(/float fold=([^;]+);/)[1]
    .replaceAll('vFishUV.x','u').replaceAll('vFishUV.y','reach');
  const fn=new Function('u','reach',...Object.keys(environment),'return '+expression);
  fold=(u,reach)=>fn(u,reach,...Object.values(environment));
}
for(const u of [-.01,0,.17,.43,.8,1,1.01]) {
  for(const reach of [-.05,-.005,0,.0001,.005,.5,1,1.05]) {
    const centre=fold(u,reach),gradient=fold(u,reach+.001)-fold(u,reach-.001);
    assert.ok(Number.isFinite(centre) && Number.isFinite(gradient),'Fin helper pixels and derivatives must stay finite on both sides of the root');
    assert.ok(Math.abs(gradient)<.00001,'Fin-root relief must not spike as a fragment crosses its boundary');
  }
}

console.log(JSON.stringify({pass:true,finiteFinRoot:true,headToTailTone:true,outerRingPeak:Math.max(...rim),upperSeamPeak:Math.max(...radii.map(r=>seam(r,.02))),analCoverageFraction:analCoverage,eyeWidth,largestEyeGap,mouthRise}));
