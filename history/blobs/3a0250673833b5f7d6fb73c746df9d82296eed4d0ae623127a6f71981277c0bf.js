import * as THREE from 'three';
import {currentVelocity} from './water.js';
import { groundHeight, randomGenerator } from './math.js';

// Fixed pools keep particles bounded. No timers: all motion shares the fish's
// simulation clock, so pause, coverage and sleep stop the whole aquarium.
export function createLivingWater(scene,{bedAnchor}={}) {
  const rng = randomGenerator(0x130928), bubbleCount = 28, dustCount = 96;
  let projectionScale = 900, time = 0, emitted = 0, cursor = 0, activeDust = 0;
  const cooldown = new Map();
  const dust = Array.from({length:dustCount},()=>({age:99,life:1,x:0,y:0,z:0,vx:0,vz:0,r:.04}));
  const bubbleSeed = Array.from({length:bubbleCount},(_,i)=>({phase:i/bubbleCount,
    dx:0,dz:0,previous:0,speed:.77+rng()*.3,x:(rng()-.5)*.30,z:(rng()-.5)*.32,r:.045+rng()*.053}));
  const anchor=new THREE.Vector3(), flowPoint=new THREE.Vector3(), flow=new THREE.Vector3();
  function layer(count, bubble) {
    const geometry = new THREE.BufferGeometry();
    const pos = new Float32Array(count*3), sizes = new Float32Array(count), alpha = new Float32Array(count);
    geometry.setAttribute('position',new THREE.BufferAttribute(pos,3).setUsage(THREE.DynamicDrawUsage));
    geometry.setAttribute('particleSize',new THREE.BufferAttribute(sizes,1).setUsage(THREE.DynamicDrawUsage));
    geometry.setAttribute('particleAlpha',new THREE.BufferAttribute(alpha,1).setUsage(THREE.DynamicDrawUsage));
    const material = new THREE.ShaderMaterial({
      transparent:true,depthWrite:false,depthTest:true,toneMapped:false,
      uniforms:{pixelScale:{value:projectionScale}},
      vertexShader:`attribute float particleSize;attribute float particleAlpha;
        uniform float pixelScale;varying float opacity;
        void main(){vec4 eye=modelViewMatrix*vec4(position,1.);gl_Position=projectionMatrix*eye;
          gl_PointSize=clamp(particleSize*pixelScale/max(1.,-eye.z),1.,15.);opacity=particleAlpha;}`,
      fragmentShader: bubble ? `varying float opacity;
        void main(){vec2 p=gl_PointCoord*2.-1.;float r=length(p);if(r>.98)discard;
          float rim=exp(-pow((r-.76)*10.,2.));
          float glint=exp(-dot(p-vec2(-.29,-.39),p-vec2(-.29,-.39))*48.);
          vec3 c=mix(vec3(.15,.36,.45),vec3(.83,.97,1.),smoothstep(-.4,.65,-p.y-p.x*.5));
          gl_FragColor=vec4(mix(c,vec3(1.),glint),opacity*(rim*.52+glint*.85));}`
        : `varying float opacity;
          void main(){vec2 p=gl_PointCoord*2.-1.;float r=dot(p,p);if(r>1.)discard;
            gl_FragColor=vec4(.63,.56,.39,opacity*exp(-r*4.)*(1.-r));}`,
    });
    const points = new THREE.Points(geometry,material);points.frustumCulled=false;
    points.name=bubble?'Small filter aeration bubbles':'Fish-disturbed sand grains';
    points.renderOrder=bubble?5:4;scene.add(points);
    return {geometry,material,points,pos,sizes,alpha};
  }
  const bubbles=layer(bubbleCount,true), sand=layer(dustCount,false);
  function update(dt,now,fish=[]) {
    if (!(dt>0)) return;
    time=now;
    for(let i=0;i<bubbleCount;i++) {
      const b=bubbleSeed[i], progress=(time*.076*b.speed+b.phase)%1;
      const emitterY=groundHeight(6.35,-.15)+.13;
      const y=emitterY+progress*(8.05-emitterY);
      if(progress<b.previous){b.dx=0;b.dz=0;}b.previous=progress;
      currentVelocity(flowPoint.set(6.35+b.x,y,-.15+b.z),time,flow);
      b.dx+=flow.x*dt*.35;b.dz+=flow.z*dt*.35;
      bubbles.pos.set([6.35+b.x+b.dx-.23*progress+.08*Math.sin(progress*19.+i),y,
        -.15+b.z+b.dz+.055*Math.sin(time*.8+i)],i*3);
      bubbles.sizes[i]=b.r*(.8+progress*.35);
      bubbles.alpha[i]=Math.min(1,progress*15,(1-progress)*24)*.83;
    }
    // Only a moving fish close to the bed can lift grains. A stationary or
    // mid-water fish cannot create an unrelated sand cloud.
    for(const f of fish) {
      const p=f.position, speed=f.velocity.length(), height=p.y-groundHeight(p.x,p.z);
      if(height<.42 || height>1.48 || speed<.30 || time<(cooldown.get(f.id)||0))continue;
      cooldown.set(f.id,time+1.5+rng()*.8);
      anchor.set(p.x,groundHeight(p.x,p.z)+.06,p.z);
      if(bedAnchor&&!bedAnchor(anchor,anchor))continue;
      const strength=Math.min(1,(1.55-height)*.85)*Math.min(1,speed);
      for(let k=0;k<7;k++) {
        const d=dust[cursor++%dustCount];
        Object.assign(d,{age:0,life:2.5+rng()*1.5,x:anchor.x+(rng()-.5)*.13,
          z:anchor.z+(rng()-.5)*.07,y:anchor.y,
          vx:-f.velocity.x*.07+(rng()-.5)*.035,vz:-f.velocity.z*.06,
          r:.16+rng()*.16,strength});
      }
      emitted++;
    }
    activeDust=0;
    for(let i=0;i<dustCount;i++) {
      const d=dust[i];d.age+=dt;
      if(d.age>=d.life){sand.alpha[i]=0;continue;}
      activeDust++;
      const u=d.age/d.life;
      currentVelocity(flowPoint.set(d.x,d.y,d.z),time,flow);
      d.x+=(d.vx+flow.x*.28)*dt;d.z+=(d.vz+flow.z*.28)*dt;
      sand.pos.set([d.x,d.y+.20*Math.sin(u*Math.PI),d.z],i*3);
      sand.sizes[i]=d.r*(1.+u*.9);
      sand.alpha[i]=Math.sin(u*Math.PI)*d.strength*.60;
    }
    for(const l of [bubbles,sand])for(const attr of Object.values(l.geometry.attributes))attr.needsUpdate=true;
  }
  return {update,resize(scale){projectionScale=scale;for(const l of [bubbles,sand])l.material.uniforms.pixelScale.value=scale;},
    stats(){return {time,bubbles:bubbleCount,activeDust,sandEvents:emitted,maxDust:dustCount};},
    dispose(){for(const l of [bubbles,sand]){scene.remove(l.points);l.geometry.dispose();l.material.dispose();}}};
}
