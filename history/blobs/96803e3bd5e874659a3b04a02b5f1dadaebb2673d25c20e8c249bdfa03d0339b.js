// AI-generated pigment plate. The original PNG/alpha and prompt are shipped together.
// This is mapped onto a closed 3D body and articulated fin meshes, not billboards.
import * as THREE from 'three';
let plate;
const readyUniform = {value: 0};
let loadError = null;
export function photoPigmentStatus() { return {loaded: readyUniform.value===1,error:loadError,source:"AI-generated RGBA pigment plate"}; }
function pigmentPlate() {
  if (plate || typeof document === 'undefined') return plate || null;
  plate = new THREE.TextureLoader().load(new URL('../assets/red-mosaic-material-v8.png', import.meta.url).href, () => {readyUniform.value=1;}, undefined, () => {loadError='load-failed';});
  plate.colorSpace = THREE.SRGBColorSpace;
  plate.minFilter = THREE.LinearMipmapLinearFilter;
  plate.magFilter = THREE.LinearFilter;
  plate.anisotropy = 4;
  return plate;
}
export function applyPhotographicPigment(shader) {
  shader.uniforms.guppyPlate = { value: pigmentPlate() };
  shader.uniforms.guppyPlateReady = readyUniform;
  shader.fragmentShader = shader.fragmentShader.replace('void main() {', /* glsl */ `
    uniform sampler2D guppyPlate;
    uniform float guppyPlateReady;
    vec4 guppyPixel(vec2 px) {
      return texture2D(guppyPlate, vec2(px.x / 1774.0, 1.0 - px.y / 887.0));
    }
    vec3 guppyVariety(vec3 c) {
      // Preserve luminance/microstructure. Recolour pigment only, not the silver cheek.
      float warm = smoothstep(0.025,0.12,c.r-max(c.g,c.b));
      vec3 tint = vGuppyVariant<0.5 ? vec3(0.13,0.62,0.91)
        : (vGuppyVariant<1.5 ? vec3(1.0,0.32,0.08)
        : (vGuppyVariant<2.5 ? vec3(0.94,0.73,0.22)
        : (vGuppyVariant<3.5 ? vec3(0.16,0.76,0.73) : vec3(0.96,0.48,0.16))));
      float luminance = dot(c,vec3(0.2126,0.7152,0.0722));
      vec3 chroma = tint * luminance / max(dot(tint,vec3(0.2126,0.7152,0.0722)),0.01);
      return mix(c,chroma,warm*(vGuppyVariant>0.5 && vGuppyVariant<1.5 ? 0.0 : 0.85));
    }
    vec4 guppyBodyPlate(vec3 point) {
      float x = point.x<=0.272 ? mix(715.0,1600.0,(point.x+0.295)/0.567)
        : mix(1600.0,1715.0,(point.x-0.272)/0.078);
      return guppyPixel(vec2(x,438.0-(point.y-0.014)/0.00060));
    }
    vec4 guppyFinPlate(float part, vec2 uv) {
      float across=1.0-2.0*uv.x, r=clamp(uv.y,0.0,1.0);
      if(part<1.5) {
        vec2 root=vec2(719.0,438.0-across*65.0);
        vec2 edge=vec2(63.0+78.0*pow(abs(across),2.5),438.0-across*393.0);
        // Small stable variation moves pigment within a specimen, not the fin outline.
        float inside=r*(0.96+0.035*vGuppySeed);
        return guppyPixel(mix(root,edge,inside));
      }
      if(part<2.5) {
        vec2 root=mix(vec2(1190.0,298.0),vec2(765.0,359.0),uv.x);
        vec2 edge=vec2(mix(1175.0,603.0,uv.x),290.0-125.0*sin(PI2*0.5*uv.x));
        return guppyPixel(mix(root,edge,r*0.95));
      }
      return vec4(0.25,0.29,0.26,0.20);
    }
    void main() {
  `).replace('#include <alphamap_fragment>', /* glsl */ `
    if(guppyPlateReady>0.5 && vFishPart<0.5) {
      vec4 plate=guppyBodyPlate(vSkinPoint);
      // The dorsal/ventral join follows the 3D surface, with a smooth pigment fade.
      float sideMask=smoothstep(0.015,0.12,fishBand)*(1.0-smoothstep(0.88,0.995,fishBand));
      diffuseColor.rgb=mix(diffuseColor.rgb,guppyVariety(plate.rgb)*0.78,
        smoothstep(0.25,0.8,plate.a)*sideMask);
      gFishThrough*=0.38;
    } else if(guppyPlateReady>0.5 && vFishPart<2.5) {
      vec4 plate=guppyFinPlate(vFishPart,vFishUV);
      diffuseColor.rgb=guppyVariety(plate.rgb)*0.82;
      gFishThrough=diffuseColor.rgb*0.11;
      #ifdef FISH_MEMBRANE
        diffuseColor.a=plate.a*0.92;
      #endif
    }
    #include <alphamap_fragment>
  `);
}
