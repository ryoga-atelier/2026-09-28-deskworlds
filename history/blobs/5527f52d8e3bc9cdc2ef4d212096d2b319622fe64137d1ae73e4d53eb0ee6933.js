import * as THREE from 'three';

// Display colours are authored in sRGB and converted once to linear shader values.
// Body, membrane and the texture-free fallback share the same specimen palette.
export const GUPPY_PALETTE = [
  {name:'水色', count:3, body:'#b4d8e2', fin:'#86cbe8', blue:true},
  {name:'赤', count:3, body:'#d9b5a8', fin:'#e77c77', blue:false},
  {name:'シャンパン', count:4, body:'#e0d6b4', fin:'#e6d49f', blue:false},
  {name:'青緑', count:2, body:'#b5d5c8', fin:'#83d2ba', blue:true},
  {name:'桃色', count:2, body:'#e2c2cc', fin:'#e6a9bf', blue:false},
  {name:'薄紫', count:4, body:'#c9c4dc', fin:'#baace3', blue:true},
  {name:'淡い黄土色', count:3, body:'#d9c39b', fin:'#d9ba80', blue:false},
  {name:'濃い青', count:3, body:'#afc7da', fin:'#649cdb', blue:true},
];
// Interleave colour families so new fish are distributed throughout the school.
export const GUPPY_VARIANTS = Object.freeze([5,2,0,6,1,3,5,7,2,4,0,6,5,1,2,7,3,4,5,6,0,2,1,7]);
const vec = hex => `vec3(${new THREE.Color(hex).toArray().map(x=>x.toFixed(6)).join(',')})`;
const choose = (name, field) => `vec3 ${name}() {\n` + GUPPY_PALETTE.map((p,i)=>
  `${i<7?`if(vGuppyVariant < ${(i+.5).toFixed(1)}) `:''}return ${vec(p[field])};`).join('\n') + '\n}';
export const GUPPY_PALETTE_GLSL = choose('guppyBodyColor','body')+'\n'+choose('guppyFinColor','fin')+`
bool guppyUsesBluePlate() {
  return ${GUPPY_PALETTE.map((p,i)=>p.blue?`abs(vGuppyVariant-${i.toFixed(1)})<.25`:null).filter(Boolean).join(' || ')};
}`;
