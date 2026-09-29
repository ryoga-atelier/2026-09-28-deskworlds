import * as THREE from 'three';

// Display colours are authored in sRGB and converted once to linear shader values.
// Body, membrane and the texture-free fallback share the same specimen palette.
export const GUPPY_PALETTE = [
  {name:'水色', count:3, body:'#72b9da', fin:'#32afed', blue:true},
  {name:'赤・ワインレッド', count:3, body:'#bd718a', fin:'#cf255e', blue:false},
  {name:'シャンパン・ライム', count:4, body:'#dbcb8d', fin:'#d7dc35', blue:false},
  {name:'青緑', count:2, body:'#64bca8', fin:'#13b58d', blue:true},
  {name:'桃色', count:2, body:'#d898b3', fin:'#e8549a', blue:false},
  {name:'紫・パステルパープル', count:4, body:'#b49cd2', fin:'#8844d5', blue:true},
  {name:'淡い黄土色', count:3, body:'#c9ad77', fin:'#dba139', blue:false},
  {name:'コバルトブルー', count:3, body:'#6a97c4', fin:'#245bdc', blue:true},
];
// Interleave colour families so new fish are distributed throughout the school.
export const GUPPY_VARIANTS = Object.freeze([5,2,0,6,1,3,5,7,2,4,0,6,5,1,2,7,3,4,5,6,0,2,1,7]);
const vec = hex => `vec3(${new THREE.Color(hex).toArray().map(x=>x.toFixed(6)).join(',')})`;
const choose = (name, field) => `vec3 ${name}() {\n` + GUPPY_PALETTE.map((p,i)=>
  `${i<7?`if(vGuppyVariant < ${(i+.5).toFixed(1)}) `:''}return ${vec(p[field])};`).join('\n') + '\n}';
export const GUPPY_PALETTE_GLSL = choose('guppyBodyColor','body')+'\n'+choose('guppyBaseFinColor','fin')+`
float guppyDarkRoot() { return max(step(.72,fract(vGuppySeed*7.13+.19)),step(6.5,vGuppyVariant)*.88); }
vec3 guppyFinColor() {
 vec3 c=guppyBaseFinColor();
 // Seed is stable per individual; deep violet coexists with pastel purple.
 if(abs(vGuppyVariant-5.)<.25) c=mix(c,${vec('#bea0ed')},smoothstep(.48,.72,vGuppySeed));
 if(abs(vGuppyVariant-2.)<.25) c=mix(c,${vec('#dfbf72')},smoothstep(.46,.68,vGuppySeed));
 if(abs(vGuppyVariant-1.)<.25) c=mix(c,${vec('#ea482b')},smoothstep(.64,.82,vGuppySeed));
 return c;
}
float guppyFinRays(vec2 uv) {
 float phase=uv.x*18.+.025*sin(uv.y*7.+uv.x*15.);
 float dist=abs(fract(phase+.5)-.5);
 float aa=max(.018,fwidth(phase)*.7);
 float primary=1.-smoothstep(.035-aa,.075+aa,dist);
 float branch=1.-smoothstep(.025-aa,.055+aa,abs(fract(phase*2.+.25)-.5));
 return clamp(primary+branch*smoothstep(.56,.86,uv.y)*.55,0.,1.);
}
bool guppyUsesBluePlate() {
  return ${GUPPY_PALETTE.map((p,i)=>p.blue?`abs(vGuppyVariant-${i.toFixed(1)})<.25`:null).filter(Boolean).join(' || ')};
}`;
