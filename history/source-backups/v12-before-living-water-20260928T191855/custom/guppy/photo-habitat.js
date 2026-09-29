import * as THREE from 'three';
import { waterTime } from './water.js';

// A photographic 2.5D environment, with a depth buffer for genuine 3D fish occlusion.
// The artist-generated depth plate is approximate; no claim of measured scene depth.
export const HABITAT_ASPECT = 1554 / 1012;
const common = /* glsl */ `
  uniform sampler2D habitatColor;
  uniform sampler2D habitatDepth;
  uniform float habitatTime;
  uniform vec2 habitatCrop;
  uniform vec2 habitatNearFar;
  vec2 habitatUV(vec2 screenUV) {
    vec2 p = (screenUV - .5) * habitatCrop + .5;
    // Long submerged leaves sway slightly. Sand and stone bases remain still.
    float bank = smoothstep(.14,.38,abs(p.x-.51));
    float stem = smoothstep(.24,.53,p.y) * (1.-smoothstep(.91,.99,p.y));
    float phase = habitatTime * .47 + p.x * 15.0 + p.y * 4.2;
    p.x += bank * stem * .00075 * (sin(phase) + .25*sin(phase*1.7+p.y*5.0));
    p.y += .00014 * smoothstep(.94,1.,p.y) * sin(habitatTime*.63+p.x*27.0);
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
    textures = await Promise.all(['aquarium-photo-v12.png','aquarium-depth-v10.png'].map(name =>
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
  };
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
    resize(aspect) {
      uniforms.habitatCrop.value.set(Math.min(1,aspect/HABITAT_ASPECT),Math.min(1,HABITAT_ASPECT/aspect));
      camera.fov = THREE.MathUtils.radToDeg(2*Math.atan(Math.tan(THREE.MathUtils.degToRad(25.8)/2)*Math.min(1,HABITAT_ASPECT/aspect)));
    },
    bindComposite(post) {
      Object.assign(post.uniforms,uniforms);
      post.fragmentShader = common + post.fragmentShader
        .replace('vec3 color=texture2D(beauty,vUv).rgb;', 'vec4 rendered=texture2D(beauty,vUv); vec3 color=rendered.rgb/max(rendered.a,.001);')
        .replace('#include <colorspace_fragment>', /* glsl */ `
          #include <colorspace_fragment>
          vec2 photoUV = habitatUV(vUv);
          vec3 photograph = texture2D(habitatColor,photoUV).rgb;
          // Slow transmitted-light movement; not a replacement video loop.
          float caustic = (sin(photoUV.x*43.+photoUV.y*22.-habitatTime*.34)
            + .5*sin(photoUV.x*29.-photoUV.y*39.+habitatTime*.23))*.004;
          photograph *= 1. + caustic * (1.-smoothstep(.20,.40,photoUV.y));
          gl_FragColor=vec4(mix(photograph,gl_FragColor.rgb,clamp(rendered.a,0.,1.)),1.);
        `);
      post.needsUpdate=true;
    },
    stats() { return {enabled:true,mode:'2.5D generated color and approximate depth plates; 3D fish',photo:[textures[0].image.width,textures[0].image.height],depth:[textures[1].image.width,textures[1].image.height]}; },
  };
}
