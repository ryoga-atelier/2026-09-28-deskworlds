import * as THREE from 'three';
export const exhibitFlow=(t,x,z)=>({x:.018+.011*Math.sin(t*.43+z*.7)+.004*Math.sin(x*.9+t*.8),z:.005*Math.sin(t*.37+x*.6)});
export async function createExhibitPlants(scene,water,timeUniform) {
 let seed=212;const rand=()=>((seed=seed*16807%2147483647)/2147483647),group=new THREE.Group();group.name='Rooted three-dimensional planting';scene.add(group);
 const leafTexture=await new THREE.TextureLoader().loadAsync('/preview/anatomy-study-v15-r1/scenes/riverscape/assets/aquatic-leaf-v9.png');leafTexture.colorSpace=THREE.SRGBColorSpace;leafTexture.anisotropy=4;
 const material=new THREE.MeshStandardMaterial({color:0xffffff,map:leafTexture,roughness:.48,side:THREE.DoubleSide,vertexColors:true,metalness:0});
 material.onBeforeCompile=s=>{s.uniforms.plantTime=timeUniform;s.vertexShader=s.vertexShader.replace('#include <common>',`#include <common>
uniform float plantTime;attribute float flexibility;varying vec2 leafUv;`).replace('#include <begin_vertex>',`#include <begin_vertex>
leafUv=uv;float wave=.018+.011*sin(plantTime*.43+position.z*.7)+.004*sin(position.x*.9+plantTime*.8);transformed.x+=flexibility*wave;transformed.z+=flexibility*.005*sin(plantTime*.37+position.x*.6);`);
 s.fragmentShader=s.fragmentShader.replace('#include <common>','#include <common>\nvarying vec2 leafUv;').replace('#include <color_fragment>',`#include <color_fragment>
 float mid=exp(-abs(leafUv.x-.5)*160.);float sideVein=pow(.5+.5*cos(leafUv.y*70.+abs(leafUv.x-.5)*34.),20.);
 float grain=fract(sin(dot(floor(leafUv*vec2(140.,340.)),vec2(12.98,78.23)))*43758.54);
 diffuseColor.rgb*=.86+.14*grain;diffuseColor.rgb=mix(diffuseColor.rgb,diffuseColor.rgb*1.26,mid*.48+sideVein*.15);
 if(!gl_FrontFacing)diffuseColor.rgb*=1.14;`);
 };water.receive(material);
 const pos=[],norm=[],uv=[],col=[],flex=[],idx=[];
 function leaf(base,angle,length,width,lift,colour,kind=0){const rows=18,cols=8,start=pos.length/3;
  for(let j=0;j<=rows;j++){const v=j/rows;for(let k=0;k<=cols;k++){const u=k/cols,side=u*2-1;const shape=Math.pow(Math.sin(Math.PI*v),kind?.68:.84);const w=width*shape*(1+.028*Math.sin(v*55));const axial=length*v;const y=base.y+lift*Math.sin(v*1.45)+.018*side*side*shape+.016*Math.sin(v*7+angle)*side;
  const x=base.x+Math.cos(angle)*axial+Math.sin(angle)*side*w,z=base.z+Math.sin(angle)*axial-Math.cos(angle)*side*w;
  pos.push(x,y,z);uv.push(u,v);const c=colour.clone().multiplyScalar(.88+.15*v+.06*rand());col.push(c.r,c.g,c.b);flex.push(v*v*length*2.4+base.y*.55);
  if(j<rows&&k<cols){const a=start+j*(cols+1)+k,b=a+cols+1;idx.push(a,b,a+1,a+1,b,b+1);}}}
 }
 const stems=[];
 function stem(points,r){const curve=new THREE.CatmullRomCurve3(points);const g=new THREE.TubeGeometry(curve,12,r,5,false);const a=new THREE.Mesh(g,new THREE.MeshStandardMaterial({color:0x425724,roughness:.8}));water.receive(a.material);a.castShadow=a.receiveShadow=true;group.add(a);stems.push(a);}
 // Plants form unequal groups, with a sand channel and open upper water.
 const beds=[[-4.2,-1.55,25],[-3.0,-1.9,27],[3.9,-1.75,18],[3.2,-1.65,16],[-3.7,.4,10],[3.85,.65,9]];
 for(const [bx,bz,n]of beds)for(let i=0;i<n;i++){
  const x=bx+(rand()-.5)*1.25,z=bz+(rand()-.5)*.8,h=.75+rand()*2.75,lean=(rand()-.5)*.95,twist=rand()*6.28;
  const points=[new THREE.Vector3(x,.035,z),new THREE.Vector3(x+lean*.35,h*.48,z+.06),new THREE.Vector3(x+lean,h,z+.13)];stem(points,.009+rand()*.007);
  for(let j=1;j<8;j++){const v=j/8;for(let k=0;k<2;k++){const base=new THREE.Vector3(x+lean*v*v,h*v,z+.13*v);leaf(base,twist+j*2.25+k*Math.PI,.30+rand()*.27,.07+rand()*.055,.09+rand()*.17,new THREE.Color().setRGB(.65+rand()*.16,.68+rand()*.23,.50+rand()*.18));}}
 }
 // Foreground Cryptocoryne / Anubias-like rosettes: each leaf has a petiole to the root.
 for(const [x,z]of [[-3.3,1.15],[-2.7,.5],[3.6,1.1],[2.8,.3],[-4.2,1.35]])for(let i=0;i<9;i++){
  const angle=rand()*6.28,pet=.14+rand()*.25,l=.48+rand()*.48,base=new THREE.Vector3(x+Math.cos(angle)*.08,.11+pet,z+Math.sin(angle)*.08);
  stem([new THREE.Vector3(x,.03,z),new THREE.Vector3(x,.13,z),base],.012);
  leaf(base,angle,l,.11+rand()*.11,.07+rand()*.17,new THREE.Color().setRGB(.44+rand()*.15,.52+rand()*.16,.38+rand()*.12),1);
 }
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setAttribute('color',new THREE.Float32BufferAttribute(col,3));g.setAttribute('flexibility',new THREE.Float32BufferAttribute(flex,1));g.setIndex(idx);g.computeVertexNormals();const leaves=new THREE.Mesh(g,material);leaves.castShadow=leaves.receiveShadow=true;group.add(leaves);
 return {group,stats:{leaves:pos.length/3/(19*9),stems:stems.length,depthOcclusion:true,rooted:true}};
}
