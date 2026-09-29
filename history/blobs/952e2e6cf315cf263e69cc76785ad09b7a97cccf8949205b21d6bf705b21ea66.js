import * as THREE from 'three';

const plate = { value: null }, ready = { value: 0 };
let pending, failure = null;
export async function loadLeafMaterial() {
  if (typeof document === 'undefined') return false;
  if (!pending) pending = new THREE.TextureLoader().loadAsync(
    new URL('../assets/aquatic-leaf-v9.png', import.meta.url).href,
  ).then(texture => {
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = 4;
    texture.minFilter = THREE.LinearMipmapLinearFilter;
    plate.value = texture;
    ready.value = 1;
    return true;
  }).catch(error => { failure = String(error); return false; });
  return pending;
}
export const leafMaterialStatus = () => ({ loaded: !!ready.value, error: failure });

export function bindLeafMaterial(shader) {
  shader.uniforms.leafPlate = plate;
  shader.uniforms.leafReady = ready;
  shader.fragmentShader = 'uniform sampler2D leafPlate; uniform float leafReady;\n' + shader.fragmentShader;
  shader.fragmentShader = shader.fragmentShader.replace(
    'diffuseColor.a = 1.0; // MSAA handles silhouettes; tissue transmission is in lighting.',
    /* glsl */ `
      // A stem shares this batch but has thin=0; never print leaf veins on a petiole.
      float tissueWeight = leafReady * smoothstep(0.02, 0.12, vThin);
      vec2 tissueUV = vec2(clamp(leafUv.x, 0.01, 0.99), clamp(leafUv.y, 0.01, 0.99));
      vec3 tissue = texture2D(leafPlate, tissueUV).rgb;
      float originalLum = dot(diffuseColor.rgb, vec3(0.2126, 0.7152, 0.0722));
      // Keep each species' bronze/green pigment, but add continuous tissue and fine veins.
      vec3 tissueColor = mix(tissue * clamp(originalLum / 0.16, 0.50, 1.55), diffuseColor.rgb, 0.35);
      float leafIdentity = 0.5 + 0.5 * sin(leafPosition.x * 2.31 + leafPosition.z * 3.07);
      tissueColor *= mix(vec3(0.88, 0.96, 0.82), vec3(1.08, 0.94, 0.85), leafIdentity);
      diffuseColor.rgb = mix(diffuseColor.rgb, tissueColor, tissueWeight);
      diffuseColor.a = 1.0;
    `,
  );
  shader.fragmentShader = shader.fragmentShader.replace(
    'float surfaceHeight = rib + veinHeight + micro;',
    /* glsl */ `
      float tissueRelief = dot(texture2D(leafPlate, clamp(leafUv, vec2(.01), vec2(.99))).rgb,
        vec3(.2126,.7152,.0722));
      float surfaceHeight = mix(rib + veinHeight + micro,
        tissueRelief * .007 + rib * .35, leafReady * smoothstep(.02,.12,vThin));
    `,
  );
}
