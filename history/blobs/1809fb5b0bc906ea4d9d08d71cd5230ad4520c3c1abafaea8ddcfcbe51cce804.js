// AI-generated pigment plate. The original PNG/alpha and prompt are shipped together.
// This is mapped onto a closed 3D body and articulated fin meshes, not billboards.
import * as THREE from 'three';
let plate;
const bluePlate = {value: null};
const blueReady = {value: 0};
let blueLoading;
const readyUniform = {value: 0};
let finishLoading;
const loading = new Promise(resolve => {finishLoading = resolve;});
export function loadPhotoPigment() {
  if (typeof document === "undefined") return Promise.resolve(false);
  pigmentPlate();
  if (!blueLoading) blueLoading = new THREE.TextureLoader().loadAsync(
    new URL('../assets/blue-grass-material-v9.png', import.meta.url).href,
  ).then(texture => {
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.minFilter = THREE.LinearMipmapLinearFilter;
    texture.anisotropy = 4;
    bluePlate.value = texture;
    blueReady.value = 1;
    return true;
  }).catch(() => false);
  return Promise.all([loading, blueLoading]);
}
let loadError = null;
export function photoPigmentStatus() { return {loaded: readyUniform.value===1,blueLoaded:blueReady.value===1,error:loadError,source:"Two AI-generated RGBA pigment plates"}; }
function pigmentPlate() {
  if (plate || typeof document === 'undefined') return plate || null;
  plate = new THREE.TextureLoader().load(new URL('../assets/red-mosaic-material-v8.png', import.meta.url).href, () => {readyUniform.value=1;finishLoading(true);}, undefined, () => {loadError='load-failed';finishLoading(false);});
  plate.colorSpace = THREE.SRGBColorSpace;
  plate.minFilter = THREE.LinearMipmapLinearFilter;
  plate.magFilter = THREE.LinearFilter;
  plate.anisotropy = 4;
  return plate;
}
export function applyPhotographicPigment(shader) {
  shader.uniforms.guppyPlate = { value: pigmentPlate() };
  shader.uniforms.guppyBluePlate = bluePlate;
  shader.uniforms.guppyBlueReady = blueReady;
  shader.uniforms.guppyPlateReady = readyUniform;
  shader.fragmentShader = shader.fragmentShader.replace('void main() {', /* glsl */ `
    uniform sampler2D guppyPlate;
    uniform sampler2D guppyBluePlate;
    uniform float guppyBlueReady;
    uniform float guppyPlateReady;
    vec4 guppyPixel(vec2 px) {
      vec2 sampleUV = vec2(px.x / 1774.0, 1.0 - px.y / 887.0);
      bool blue = guppyUsesBluePlate();
      if (blue && guppyBlueReady > .5) return texture2D(guppyBluePlate, sampleUV);
      return texture2D(guppyPlate, sampleUV);
    }
    vec3 guppyVariety(vec3 c, bool membrane) {
      float luminance=dot(c,vec3(.2126,.7152,.0722));
      // Neutralize the plate's baked dark lighting without erasing fine dark ink.
      float ink=1.0-smoothstep(.004,.026,luminance);
      float detail=smoothstep(.012,.52,luminance);
      vec3 pigment=membrane?guppyFinColor():guppyBodyColor();
      vec3 bright=pigment*mix(.56,1.14,detail);
      if(!membrane) {
        float chroma=max(c.r,max(c.g,c.b))-min(c.r,min(c.g,c.b));
        bright=mix(bright,mix(pigment,vec3(.63,.64,.60),.44)*mix(.64,1.06,detail),
          (1.0-smoothstep(.025,.16,chroma))*.60);
      }
      return mix(bright,vec3(.015,.021,.027),ink*(membrane?.80:.60));
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
        vec2 pigmentUV=mix(root,edge,inside);
        vec4 outline=guppyPixel(pigmentUV);
        // Vary interior markings while preserving the photographed free margin.
        float interior=sin(3.14159265*r)*max(0.0,1.0-across*across);
        pigmentUV+=interior*vec2(48.0*sin(vGuppySeed*19.0+across*2.4),
          42.0*sin(vGuppySeed*27.0+r*3.1));
        vec4 pigment=guppyPixel(pigmentUV);
        return vec4(pigment.rgb,outline.a);
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
      diffuseColor.rgb=mix(diffuseColor.rgb,guppyVariety(plate.rgb,false),
        smoothstep(0.25,0.8,plate.a)*sideMask);
      gFishThrough*=0.75;
    } else if(guppyPlateReady>0.5 && vFishPart<2.5) {
      vec4 plate=guppyFinPlate(vFishPart,vFishUV);
      diffuseColor.rgb=guppyVariety(plate.rgb,true);
      gFishThrough=diffuseColor.rgb*0.16;
      #ifdef FISH_MEMBRANE
        float ink=1.0-smoothstep(0.035,0.21,dot(plate.rgb,vec3(.2126,.7152,.0722)));
        diffuseColor.a=plate.a*(mix(.84,.68,smoothstep(.25,1.0,vFishUV.y))+.10*ink);
      #endif
    }
    #include <alphamap_fragment>
  `);
}
