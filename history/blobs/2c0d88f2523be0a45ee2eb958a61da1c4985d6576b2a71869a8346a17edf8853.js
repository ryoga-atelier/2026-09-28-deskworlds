import * as THREE from 'three';
import { waterTime } from './water.js';
import { HABITAT_OPTICS_GLSL } from './water-optics.js';

// A photographic 2.5D environment, with a depth buffer for genuine 3D fish occlusion.
// The artist-generated depth plate is approximate; no claim of measured scene depth.
export const HABITAT_ASPECT = 1554 / 1012;
const common = /* glsl */ `
  uniform sampler2D habitatColor;
  uniform sampler2D habitatDepth;
  uniform float habitatTime;
  uniform vec2 habitatCrop;
  uniform vec2 habitatNearFar;
  uniform mat4 habitatInverseViewProjection;
  uniform vec3 habitatCameraPosition, habitatCameraForward;
  vec2 habitatUV(vec2 screenUV) {
    vec2 p = (screenUV - .5) * habitatCrop + .5;
    // Bend the green foliage with roots held in the bed. The same warp is used
    // for colour and depth, so fish still disappear behind the moving leaves.
    vec3 pigment = texture2D(habitatColor,p).rgb;
    float leaf = smoothstep(.015,.11,pigment.g-max(pigment.r*.86,pigment.b));
    float stem = smoothstep(.18,.68,p.y) * (1.-smoothstep(.90,.98,p.y));
    float phase = habitatTime * 1.18 + p.x * 18.0 + p.y * 3.5;
    float bend = sin(phase) + .28*sin(phase*1.53+p.y*7.0);
    float pipe = 1.-smoothstep(.946,.961,p.x);
    p.x += leaf * stem * pipe * .0046 * bend;
    p.y += leaf * stem * pipe * .0008 * sin(phase*.87+p.x*23.);
    float openWater=smoothstep(.04,.17,pigment.b-pigment.r)
      * (1.-smoothstep(.02,.14,texture2D(habitatDepth,p).r));
    p.x += openWater*.0028*sin(p.y*19.+habitatTime*.49);
    p.y += openWater*.0017*sin(p.x*23.-habitatTime*.57);
    // Refract only the surface reflection band, never the sand or the fish.
    float surface = smoothstep(.855,.96,p.y);
    p.x += surface*.0052*sin(p.x*42.+p.y*73.-habitatTime*1.65);
    p.y += surface*.0055*(sin(p.x*35.-habitatTime*1.8)
      + .38*sin(p.x*69.+p.y*92.+habitatTime*2.3));
    return clamp(p, vec2(.0002), vec2(.9998));
  }
  float habitatDistance(vec2 uv) {
    float d = texture2D(habitatDepth, uv).r;
    // Black is open water/rear glass. Near-white is the front of the sand bed.
    return mix(32.0, 14.8, smoothstep(.02,.99,d));
  }
`;

export async function createPhotoHabitat(scene, camera) {
  const hidden = scene.children.filter(object => object.isMesh || object.isGroup);
  let textures;
  try {
    const loader = new THREE.TextureLoader();
    textures = await Promise.all(['aquarium-photo-v13.png','aquarium-depth-v10.png'].map(name =>
      loader.loadAsync(new URL('../assets/' + name, import.meta.url).href)));
  } catch (error) {
    return { enabled: false, error: String(error), resize() {}, bindComposite() {}, stats() { return {enabled:false,error:String(error)}; } };
  }
  // The color plate already contains photographic display tones. Composite it after
  // Three's tone mapping instead of applying a second filmic curve to the photograph.
  for (const texture of textures) {
    texture.colorSpace = THREE.NoColorSpace;
    texture.anisotropy = 4;
    texture.minFilter = THREE.LinearMipmapLinearFilter;
  }
  const uniforms = {
    habitatColor: {value: textures[0]}, habitatDepth: {value: textures[1]},
    habitatTime: waterTime, habitatCrop: {value: new THREE.Vector2(1,1)},
    habitatNearFar: {value:new THREE.Vector2(camera.near,camera.far)},
    habitatInverseViewProjection:{value:new THREE.Matrix4()},
    habitatCameraPosition:{value:camera.position},
    habitatCameraForward:{value:new THREE.Vector3()},
  };
  // The photographic bed differs from the original modelled terrain. Project
  // a near-bed disturbance onto the visible sand, rather than behind the plate.
  const sampleWidth=512,sampleHeight=Math.round(512/HABITAT_ASPECT);
  const scratch=document.createElement('canvas');scratch.width=sampleWidth;scratch.height=sampleHeight;
  const context=scratch.getContext('2d',{willReadFrequently:true});
  const sampleData=textures.map(texture=>{context.clearRect(0,0,sampleWidth,sampleHeight);
    context.drawImage(texture.image,0,0,sampleWidth,sampleHeight);
    return context.getImageData(0,0,sampleWidth,sampleHeight).data;});
  const clip=new THREE.Vector3(),ray=new THREE.Vector3(),forward=new THREE.Vector3();
  function bedAnchor(point,out){
    clip.copy(point).project(camera);
    const u=clip.x*.5*uniforms.habitatCrop.value.x+.5;
    const v=clip.y*.5*uniforms.habitatCrop.value.y+.5;
    if(u<0||u>1||v<0||v>.34)return null;
    const index=(Math.min(sampleHeight-1,Math.floor((1-v)*sampleHeight))*sampleWidth
      +Math.min(sampleWidth-1,Math.floor(u*sampleWidth)))*4;
    const [r,g,b]=sampleData[0].slice(index,index+3);
    if(r<g*.98||g<b*1.055||r<100)return null;
    const d=32.-17.2*THREE.MathUtils.smoothstep(sampleData[1][index]/255,.02,.99);
    ray.set(clip.x,clip.y,.5).unproject(camera).sub(camera.position);
    camera.getWorldDirection(forward);
    return out.copy(camera.position).addScaledVector(ray,(d-.10)/ray.dot(forward));
  }
  const material = new THREE.ShaderMaterial({
    uniforms, depthTest: true, depthWrite: true, blending: THREE.NoBlending,
    vertexShader: 'varying vec2 vUv; void main(){vUv=uv;gl_Position=vec4(position.xy,0.,1.);}',
    fragmentShader: common + /* glsl */ `
      varying vec2 vUv;
      void main(){
        float d = habitatDistance(habitatUV(vUv));
        float n = habitatNearFar.x, f = habitatNearFar.y;
        gl_FragDepth = f*(d-n)/((f-n)*d);
        gl_FragColor=vec4(0.0);
      }
    `,
  });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(2,2),material);
  mesh.name = 'Photographic aquarium depth surface';
  mesh.frustumCulled = false;
  mesh.renderOrder = -1000;
  for (const object of hidden) object.visible = false;
  scene.background = null;
  scene.add(mesh);
  return {
    enabled: true,
    bedAnchor,
    resize(aspect) {
      uniforms.habitatCrop.value.set(Math.min(1,aspect/HABITAT_ASPECT),Math.min(1,HABITAT_ASPECT/aspect));
      camera.fov = THREE.MathUtils.radToDeg(2*Math.atan(Math.tan(THREE.MathUtils.degToRad(25.8)/2)*Math.min(1,HABITAT_ASPECT/aspect)));
      camera.updateProjectionMatrix();camera.updateMatrixWorld();
      uniforms.habitatInverseViewProjection.value.multiplyMatrices(camera.matrixWorld,camera.projectionMatrixInverse);
      camera.getWorldDirection(uniforms.habitatCameraForward.value);
    },
    bindComposite(post) {
      Object.assign(post.uniforms,uniforms);
      post.fragmentShader = common + HABITAT_OPTICS_GLSL + post.fragmentShader
        .replace('vec3 color=texture2D(beauty,vUv).rgb;', 'vec4 rendered=texture2D(beauty,vUv); vec3 color=rendered.rgb/max(rendered.a,.001);')
        .replace('#include <colorspace_fragment>', /* glsl */ `
          #include <colorspace_fragment>
          vec2 photoUV = habitatUV(vUv);
          vec3 photograph = texture2D(habitatColor,photoUV).rgb;
          photograph=tankPhotograph(photoUV,photograph);
          gl_FragColor=vec4(mix(photograph,gl_FragColor.rgb,clamp(rendered.a,0.,1.)),1.);
        `);
      post.needsUpdate=true;
    },
    stats() { return {enabled:true,mode:'2.5D planted habitat; shared spectral water, depth-projected caustics, surface reflection, soft shafts; 3D fish',motionTime:waterTime.value,photo:[textures[0].image.width,textures[0].image.height],depth:[textures[1].image.width,textures[1].image.height]}; },
  };
}
