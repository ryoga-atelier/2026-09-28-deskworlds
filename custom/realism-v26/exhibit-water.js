import * as THREE from 'three';
// Wave spectrum and forward projected caustic area ratio adapted from CAUSTIC//LITE,
// ScottieFox, MIT, d87351bff19831aa9d11c0679605fad6797b133f. See CAUSTIC-LICENSE.txt.
// Local adaptation: shared height/slopes, four receiver heights, real scene colour/depth.
export function createExhibitWater(renderer, scene, camera, {width=10,depth=5,level=4,lightDirection=new THREE.Vector3(-.26,.94,.22).normalize()}={}) {
  const NW=16, res=new THREE.Vector2(256,128), size=new THREE.Vector2(width,depth);
  const waveData=[], amplitudes=[]; let seed=5;
  const rand=()=>((seed=seed*16807%2147483647)/2147483647);
  for(let i=0;i<NW;i++) {const len=4*Math.pow(.12,i/(NW-1)),k=2*Math.PI/len,dir=i*2.39996+(rand()-.5)*.9;
    waveData.push(new THREE.Vector4(k*Math.cos(dir),k*Math.sin(dir),Math.sqrt(2.2*k),rand()*6.283));
    amplitudes.push(.006*Math.pow(len/2,.85)*(.7+.6*rand()));}
  const u={waterTime:{value:0},waterSize:{value:size},waterLevel:{value:level},waterW:{value:waveData},waterA:{value:amplitudes},waterSurface:{value:null}};
  const flat=new THREE.Camera(),quadScene=new THREE.Scene();
  const quad=new THREE.Mesh(new THREE.PlaneGeometry(2,2),new THREE.ShaderMaterial({uniforms:u,depthTest:false,depthWrite:false,
    vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=vec4(position,1.);}',
    fragmentShader:`varying vec2 vUv;uniform vec2 waterSize;uniform float waterTime;uniform vec4 waterW[${NW}];uniform float waterA[${NW}];
    void main(){vec2 p=(vUv-.5)*waterSize;vec3 w=vec3(0.);for(int i=0;i<${NW};i++){
      vec2 kd=waterW[i].xy,s=normalize(vec2(-kd.y,kd.x));float kb=.25*length(kd),pb=kb*dot(s,p)+waterTime*.22+float(i)*7.1;
      float phase=dot(kd,p)-waterW[i].z*waterTime+waterW[i].w+.7*sin(pb);
      float a=waterA[i]*(.85+.15*sin(waterTime*.35+float(i)));
      w+=a*vec3(sin(phase),cos(phase)*(kd+.7*kb*cos(pb)*s));}gl_FragColor=vec4(w,1.);}` }));quadScene.add(quad);
  const surf=new THREE.WebGLRenderTarget(res.x,res.y,{type:THREE.HalfFloatType,depthBuffer:false});u.waterSurface.value=surf.texture;
  const levels=[0,level/3,level*2/3,level],caus=levels.map(()=>new THREE.WebGLRenderTarget(384,192,{type:THREE.HalfFloatType,depthBuffer:false}));
  const cu={...u,receiverY:{value:0},lightDir:{value:lightDirection}};
  const cg=new THREE.PlaneGeometry(width,depth,192,96).rotateX(-Math.PI/2);
  const cm=new THREE.ShaderMaterial({uniforms:cu,side:THREE.DoubleSide,depthTest:false,depthWrite:false,transparent:true,blending:THREE.AdditiveBlending,
    vertexShader:`uniform sampler2D waterSurface;uniform vec2 waterSize;uniform float waterLevel,receiverY;uniform vec3 lightDir;varying vec2 vOrigin;varying float vEnergy;
    void main(){vec3 w=texture2D(waterSurface,position.xz/waterSize+.5).rgb;vec3 p=vec3(position.x,waterLevel+w.x,position.z),n=normalize(vec3(-w.y,1.,-w.z));
    vec3 ray=refract(-lightDir,n,1./1.333);float t=(p.y-receiverY)/max(.05,-ray.y);vec3 q=p+t*ray;
    vOrigin=position.xz;vEnergy=.98*max(lightDir.y,0.)*exp(-.003*t);gl_Position=vec4(q.xz/(waterSize*.5),0.,1.);}`,
    fragmentShader:`varying vec2 vOrigin;varying float vEnergy;void main(){vec2 a=dFdx(vOrigin),b=dFdy(vOrigin);float ratio=abs(a.x*b.y-a.y*b.x)/${width*depth/(384*192)};gl_FragColor=vec4(vec3(vEnergy*min(ratio,4.)),1.);}`});
  const cs=new THREE.Scene(),mesh=new THREE.Mesh(cg,cm);mesh.frustumCulled=false;cs.add(mesh);
  const shared=`uniform sampler2D exhibitCaustic0,exhibitCaustic1,exhibitCaustic2,exhibitCaustic3;uniform vec2 waterSize;uniform float waterLevel;varying vec3 exhibitWorld;
  float exhibitLight(){vec2 q=exhibitWorld.xz/waterSize+.5;float h=clamp(exhibitWorld.y/waterLevel*3.,0.,2.99);float a=texture2D(exhibitCaustic0,q).r,b=texture2D(exhibitCaustic1,q).r,c=texture2D(exhibitCaustic2,q).r,d=texture2D(exhibitCaustic3,q).r;
  return h<1.?mix(a,b,h):h<2.?mix(b,c,h-1.):mix(c,d,h-2.);}`;
  const received=new WeakSet();
  function receive(material) {if(received.has(material)||!material.isMeshStandardMaterial)return;received.add(material);const prior=material.onBeforeCompile;material.onBeforeCompile=function(s,...args){prior.call(this,s,...args);Object.assign(s.uniforms,{waterSize:u.waterSize,waterLevel:u.waterLevel,...Object.fromEntries(caus.map((r,i)=>['exhibitCaustic'+i,{value:r.texture}]))});
    s.vertexShader=s.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 exhibitWorld;').replace('#include <project_vertex>',`#include <project_vertex>
    vec4 ep=vec4(transformed,1.);\n#ifdef USE_INSTANCING\nep=instanceMatrix*ep;\n#endif\nexhibitWorld=(modelMatrix*ep).xyz;`);
    s.fragmentShader=s.fragmentShader.replace('gWaterLight = waterLight(vWaterPosition, waterTime) * vWaterDrift;', 'gWaterLight = vec3(1.0);').replace('#include <common>','#include <common>\n'+shared).replace('#include <lights_fragment_end>',`#include <lights_fragment_end>
      reflectedLight.directDiffuse*=clamp(.78+.24*exhibitLight(),.80,1.45);`);};
    material.customProgramCacheKey=()=> 'exhibit-v15:'+prior.toString();material.needsUpdate=true;
  }
  const screen=new THREE.WebGLRenderTarget(1280,720,{type:THREE.HalfFloatType,depthBuffer:true});screen.depthTexture=new THREE.DepthTexture(1280,720);
  const reflection=new THREE.WebGLRenderTarget(640,360,{type:THREE.HalfFloatType,depthBuffer:true});
  const reflectionCamera=camera.clone(), reflectionViewProj=new THREE.Matrix4();
  const screenU={...u,reflectionColor:{value:reflection.texture},reflectionViewProj:{value:reflectionViewProj},waterLightDirection:{value:lightDirection},sceneColor:{value:screen.texture},sceneDepth:{value:screen.depthTexture},viewProj:{value:new THREE.Matrix4()},screenSize:{value:new THREE.Vector2(1280,720)},camNearFar:{value:new THREE.Vector2(camera.near,camera.far)}};
  const surface=new THREE.Mesh(cg.clone(),new THREE.ShaderMaterial({uniforms:screenU,side:THREE.DoubleSide,transparent:false,depthWrite:true,
    vertexShader:`uniform sampler2D waterSurface;uniform vec2 waterSize;uniform float waterLevel;varying vec3 vWorld;void main(){vec3 w=texture2D(waterSurface,position.xz/waterSize+.5).rgb;vWorld=vec3(position.x,waterLevel+w.x,position.z);gl_Position=projectionMatrix*viewMatrix*vec4(vWorld,1.);}`,
    fragmentShader:`uniform sampler2D waterSurface,sceneColor,sceneDepth,reflectionColor;uniform mat4 reflectionViewProj;uniform vec2 waterSize,screenSize,camNearFar;uniform mat4 viewProj;uniform vec3 waterLightDirection;varying vec3 vWorld;
    vec2 projectPoint(vec3 p){vec4 q=viewProj*vec4(p,1.);return q.xy/q.w*.5+.5;}
    vec3 traceView(vec3 dir,out float distanceHit){vec3 found=texture2D(sceneColor,gl_FragCoord.xy/screenSize).rgb;distanceHit=0.;
      for(int i=1;i<=20;i++){float t=float(i)*.60;vec3 q=vWorld+dir*t;vec4 clip=viewProj*vec4(q,1.);vec2 uv=clip.xy/clip.w*.5+.5;
      if(any(lessThan(uv,vec2(0.)))||any(greaterThan(uv,vec2(1.))))break;
      float z=texture2D(sceneDepth,uv).r;if(clip.z/clip.w*.5+.5>=z-.0007){found=texture2D(sceneColor,uv).rgb;distanceHit=t;break;}}
      return found;}
    void main(){vec3 w=texture2D(waterSurface,vWorld.xz/waterSize+.5).rgb;vec3 n=normalize(vec3(-w.y,1.,-w.z)),incident=normalize(vWorld-cameraPosition);
      bool below=dot(incident,n)>0.;if(below)n=-n;
      vec3 ray=refract(incident,n,below?1.333:1./1.333);float F=.0204+.9796*pow(1.-max(dot(-incident,n),0.),5.);
      float hit;vec3 transmitted=traceView(ray,hit)*exp(-vec3(.008,.002,.001)*hit);
      vec3 r=reflect(incident,n);float lamp=pow(max(dot(r,waterLightDirection),0.),150.);
      vec3 reflected=vec3(.26,.42,.50)+vec3(1.8)*lamp;
      if(below){
        vec4 rp=reflectionViewProj*vec4(vWorld,1.);vec2 ruv=rp.xy/rp.w*.5+.5;
        ruv+=w.yz*vec2(.085,.11);
        reflected=texture2D(reflectionColor,clamp(ruv,vec2(.002),vec2(.998))).rgb;
        if(dot(ray,ray)<.1)F=1.;
      }
      vec3 colour=mix(transmitted,reflected,clamp(F,.02,1.));gl_FragColor=vec4(colour,1.);
      #include <tonemapping_fragment>\n#include <colorspace_fragment>
    }`}));surface.name='Shared water surface / scene-depth refraction';surface.frustumCulled=false;scene.add(surface);
  let enabled=true,lastTime=-1;
  return {receive,surface,setEnabled(v){enabled=v;surface.visible=v;},
    update(time){if(time===lastTime)return;lastTime=time;u.waterTime.value=time;const target=renderer.getRenderTarget(),clear=new THREE.Color();renderer.getClearColor(clear);const alpha=renderer.getClearAlpha();renderer.setClearColor(0,0);renderer.setRenderTarget(surf);renderer.render(quadScene,flat);for(let i=0;i<4;i++){cu.receiverY.value=levels[i];renderer.setRenderTarget(caus[i]);renderer.clear();renderer.render(cs,flat);}renderer.setRenderTarget(target);renderer.setClearColor(clear,alpha);},
    resize(w,h){screen.setSize(w,h);reflection.setSize(Math.max(1,Math.round(w*.5)),Math.max(1,Math.round(h*.5)));screenU.screenSize.value.set(w,h);},
    render(outputTarget=null){
      const shadowUpdate=renderer.shadowMap.autoUpdate;
      if(enabled){
        surface.visible=false;
        renderer.setRenderTarget(screen);renderer.render(scene,camera);
        renderer.shadowMap.autoUpdate=false;
        reflectionCamera.copy(camera);
        reflectionCamera.position.y=2*level-camera.position.y;
        const aim=camera.getWorldDirection(new THREE.Vector3()).add(camera.position);aim.y=2*level-aim.y;
        reflectionCamera.up.set(0,-1,0);reflectionCamera.lookAt(aim);reflectionCamera.updateMatrixWorld();
        reflectionViewProj.multiplyMatrices(reflectionCamera.projectionMatrix,reflectionCamera.matrixWorldInverse);
        renderer.setRenderTarget(reflection);renderer.render(scene,reflectionCamera);
        surface.visible=true;
        screenU.viewProj.value.multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse);
      }
      renderer.setRenderTarget(outputTarget);renderer.render(scene,camera);
      renderer.shadowMap.autoUpdate=shadowUpdate;
    },
    stats(){return {waves:NW,receiverLayers:4,surfaceTime:u.waterTime.value,raySteps:20,sharedHeightNormal:true,sceneDepthRefraction:true,planarSceneReflection:true};}
  };
}
