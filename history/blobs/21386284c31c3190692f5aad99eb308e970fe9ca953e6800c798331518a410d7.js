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
      vec3 pigment=guppyFinColor();
      float peak=max(pigment.r,max(pigment.g,pigment.b));
      vec3 hue=pigment/max(peak,.08);
      // Pigment keeps chroma; silver skin is handled separately, never bleached here.
      float lifted=.009+(membrane?.82:.60)*pow(max(luminance,0.),.60);
      return clamp(mix(vec3(1.),hue,membrane?.98:.94)*lifted,vec3(.003),vec3(.86));
    }

    vec4 guppyBodyPlate(vec3 point) {
      float x = point.x<=0.272 ? mix(715.0,1600.0,(point.x+0.295)/0.567)
        : mix(1600.0,1715.0,(point.x-0.272)/0.078);
      float top=mix(360.,306.,smoothstep(715.,1120.,x));
      top=mix(top,420.,smoothstep(1200.,1715.,x));
      float bottom=mix(502.,568.,smoothstep(1050.,1420.,x));
      bottom=mix(bottom,466.,smoothstep(1470.,1715.,x));
      return guppyPixel(vec2(x,mix(top+5.,bottom-5.,clamp(vFishUV.y,0.,1.))));
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
      float lum=dot(plate.rgb,vec3(.2126,.7152,.0722));
      float detail=smoothstep(.009,.54,lum);
      float dorsal=1.0-smoothstep(.08,.47,fishBand);
      float ventral=smoothstep(.54,.89,fishBand);
      vec3 silver=mix(vec3(.31,.40,.41),vec3(.14,.20,.19),dorsal*.70);
      silver=mix(silver,vec3(.57,.63,.62),ventral*.85);
      silver*=.94+.08*detail;
      float side=sin(3.14159265*clamp(fishBand,0.,1.));
      float broken=gMottle(vec2(fishX*28.0,fishBand*8.0)+vGuppySeed*29.0);
      float rear=1.-smoothstep(.04,.23,fishX+(broken-.5)*.055);
      float mid=1.-smoothstep(.44,.74,fishBand);
      float pigmentMask=clamp(rear*mid*(.82+.18*smoothstep(.38,.64,broken)),0.,1.);
      vec3 colour=guppyFinColor()*mix(.65,1.03,detail);
      vec3 bodyPigment=mix(silver,colour,pigmentMask*.90);
      float gill=exp(-pow((fishX-.193)/.031,2.)-pow((fishBand-.69)/.19,2.));
      bodyPigment=mix(bodyPigment,vec3(.53,.33,.27),gill*.30);
      // Localized melanophores remain dark while the silver belly stays reflective.
      float ink=(1.-smoothstep(.009,.055,lum))*rear*mid;
      bodyPigment=mix(bodyPigment,vec3(.015,.034,.032),ink*.58);
      float scales=fishScaleMask();
      bodyPigment*=1.-.045*scales*smoothstep(.3,.51,length(fract(fishScaleGrid())-.5));
      float cheek=exp(-pow((fishX-.20)/.054,2.))*smoothstep(.25,.50,fishBand);
      bodyPigment=mix(bodyPigment,vec3(.40,.50,.50),cheek*.35);
      // Keep the actual fine pigment structure; the low-frequency silver/body field
      // supplies volume and the plate never supplies the pupil or the silhouette.
      float chroma=max(plate.r,max(plate.g,plate.b))-min(plate.r,min(plate.g,plate.b));
      float pigmented=smoothstep(.009,.10,chroma)*rear;
      vec3 neutralPlate=vec3(lum)*(.9+.32/(.30+sqrt(max(lum,.0001))));
      vec3 photographic=mix(neutralPlate,guppyVariety(plate.rgb,false),pigmented);
      float pigmentDetail=plate.a*sideMask*(1.-smoothstep(.23,.29,fishX));
      bodyPigment=mix(bodyPigment,photographic,pigmentDetail*.78);
      diffuseColor.rgb=mix(diffuseColor.rgb,bodyPigment,sideMask*.97);
      gFishThrough*=0.75;
    } else if(guppyPlateReady>0.5 && vFishPart<2.5) {
      vec4 plate=guppyFinPlate(vFishPart,vFishUV);
      float lum=dot(plate.rgb,vec3(.2126,.7152,.0722));
      float rays=guppyFinRays(vFishUV);
      float ink=1.-smoothstep(.016,.095,lum);
      float tissue=smoothstep(.04,.25,vFishUV.y);
      float rim=smoothstep(.91,1.,vFishUV.y);
      vec3 fin=guppyVariety(plate.rgb,true);
      vec3 lineColor=guppyFinColor()*(.60+.28*lum);
      // Fine coloured strands on a translucent veil, not opaque wire geometry.
      diffuseColor.rgb=mix(fin,lineColor,rays*.62);
      diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.014,.021,.025),ink*.36);
      gFishThrough=diffuseColor.rgb*.10;
      #ifdef FISH_MEMBRANE
        diffuseColor.a=plate.a*(.34+.28*smoothstep(.02,.25,lum)+.24*rays+.12*ink)
          *(1.-.46*rim)*mix(.86,1.,tissue);
      #endif
    }
    #include <alphamap_fragment>
  `);
}
