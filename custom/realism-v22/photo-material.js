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

// Skin, chromatophores, guanine scales and fin tissue are independent layers.
// The old fancy-guppy plate contributes only a little grain; its photographed
// shadow, silhouette and large-fin pattern no longer determine this specimen.
export function applyPhotographicPigment(shader) {
  shader.uniforms.guppyPlate = {value: pigmentPlate()};
  shader.uniforms.guppyBluePlate = bluePlate;
  shader.uniforms.guppyBlueReady = blueReady;
  shader.uniforms.guppyPlateReady = readyUniform;
  shader.uniforms.guppySurfaceDetail = {value: 1};
  shader.fragmentShader = shader.fragmentShader.replace('void main() {', /* glsl */ `
    uniform sampler2D guppyPlate;
    uniform sampler2D guppyBluePlate;
    uniform float guppyPlateReady, guppyBlueReady, guppySurfaceDetail;
    float gNoise(vec2 p) {
      vec2 c=floor(p),f=fract(p); f=f*f*(3.-2.*f);
      return mix(mix(fishHash(c),fishHash(c+vec2(1,0)),f.x),
        mix(fishHash(c+vec2(0,1)),fishHash(c+vec2(1,1)),f.x),f.y);
    }
    float gMottle(vec2 p) {
      return .65*gNoise(p)+.25*gNoise(p*2.03+8.7)+.10*gNoise(p*4.11-3.1);
    }
    // A free scale margin is an arc, not a dark rectangular grid. The continuous
    // ramp is a tiny overlapping plate; surface derivatives tilt its reflection.
    float guppyScaleEdge() {
      vec2 cell=fract(fishScaleGrid())-.5;
      float arc=cell.x+.35-.88*cell.y*cell.y;
      float aa=max(.015,fwidth(arc)*.75);
      return (1.-smoothstep(.027-aa,.052+aa,abs(arc)))*fishScaleMask();
    }
    float guppyScaleHeight() {
      vec2 grid=fishScaleGrid(),c=fract(grid)-.5;
      float arc=c.x+.35-.88*c.y*c.y;
      float dome=smoothstep(-.06,.07,arc)*(1.-smoothstep(.26,.50,c.x));
      dome*=1.-smoothstep(.32,.51,abs(c.y));
      return dome*(.50+.50*fishHash(floor(grid)+1.3))*fishScaleMask();
    }
    float guppyPatternAmount() { return smoothstep(.20,.70,fract(vGuppySeed*11.31)); }
    float guppyRays() {
      float count=vFishPart<1.5?18.:(vFishPart<2.5?9.:vFishPart<3.5?8.:7.);
      float reach=vFishUV.y;
      float phase=vFishUV.x*count+.025*sin(reach*7.+vFishUV.x*15.);
      float aa=max(.016,fwidth(phase)*.75);
      float stem=1.-smoothstep(.035-aa,.070+aa,abs(fract(phase+.5)-.5));
      float split=1.-smoothstep(.018-aa,.040+aa,abs(fract(phase*2.+.25)-.5));
      float fade=1.-smoothstep(.40,1.15,fwidth(phase));
      return clamp(stem+split*smoothstep(.48,.82,reach)*.55,0.,1.)*fade;
    }
    // Pigment masks are in rest-space: rotating the fish never moves its colours.
    float guppyBackPigment() {
      float b=clamp(vFishUV.y,0.,1.);
      return 1.-smoothstep(.42,.58,b);
    }
    float guppyHeadPigment() {
      float x=vSkinPoint.x,b=clamp(vFishUV.y,0.,1.);
      float skull=smoothstep(.195,.255,x)*(1.-smoothstep(.36,.56,b));
      float orbit=1.-smoothstep(1.10,2.25,fishOrbit());
      return max(skull,orbit*.80);
    }
    float guppyTailRoot() {
      float caudal=1.-step(1.5,vFishPart);
      float edge=.22+.016*sin(vFishUV.x*17.+vGuppySeed*4.);
      return caudal*(1.-smoothstep(edge-.10,edge+.13,vFishUV.y));
    }
    float guppyFinClearEdge() {
      float caudal=1.-step(1.5,vFishPart);
      return smoothstep(mix(.60,.72,caudal)+.016*sin(vFishUV.x*31.),.99,vFishUV.y);
    }
    vec3 guppySkin() {
      float x=vSkinPoint.x,b=clamp(vFishUV.y,0.,1.);
      float seed=vGuppySeed*37.;
      float soft=gMottle(vec2(x*22.,b*7.)+seed);
      vec3 skin=mix(vec3(.235,.15,.115),vec3(.43,.39,.345),smoothstep(.13,.50,b));
      skin=mix(skin,vec3(.61,.56,.445),smoothstep(.62,.92,b));
      float cavity=fishCavity(x,b);
      skin=mix(skin,vec3(.55,.61,.60),cavity*.52);
      skin*=.93+.16*soft;
      float rose=exp(-pow((b-.33)/.22,2.));
      skin=mix(skin,vec3(.43,.25,.27),rose*.26);
      float rear=1.-smoothstep(-.025,.18,x+(soft-.5)*.065);
      float flank=smoothstep(.10,.30,b)*(1.-smoothstep(.63,.86,b));
      float pattern=guppyPatternAmount();
      float islands=smoothstep(.42,.61,gMottle(vec2(x*38.,b*11.)+seed));
      vec3 pigment=mix(guppyBodyColor(),guppyFinColor(),.50)*(.86+.24*soft);
      float silverSpecimen=step(.88,fract(vGuppySeed*5.71+.13));
      float colourAmount=mix(.55+.15*pattern,.12,silverSpecimen);
      skin=mix(skin,pigment,rear*flank*colourAmount*(.55+.45*islands));
      // Small dark concentrations at the caudal base and belly rear are tissue
      // markings. They never cover the entire shadow-facing side of the fish.
      float base=1.-smoothstep(-.280,-.225,x);
      skin=mix(skin,vec3(.016,.020,.027),base*(.91+.04*guppyDarkRoot()));
      float abdomen=exp(-pow((x-.008)/.025,2.)-pow((b-.76)/.17,2.));
      skin=mix(skin,vec3(.086,.073,.042),abdomen*.43);
      float gold=exp(-pow((x-.07)/.053,2.)-pow((b-.63)/.19,2.));
      skin=mix(skin,vec3(.58,.36,.103),gold*.44);
      float gill=exp(-pow((x-.195)/.035,2.)-pow((b-.62)/.21,2.));
      skin=mix(skin,vec3(.57,.29,.235),gill*.42);
      float cheek=exp(-pow((x-.214)/.034,2.)-pow((b-.46)/.20,2.));
      skin=mix(skin,vec3(.45,.52,.48),cheek*.50);
      float abdominalSpan=smoothstep(-.06,.015,x)*(1.-smoothstep(.18,.23,x));
      float bellyBand=.55+.045*sin(x*18.);
      float boundary=exp(-pow((b-bellyBand)/.021,2.))*abdominalSpan;
      skin=mix(skin,vec3(.64,.64,.565),smoothstep(bellyBand-.010,bellyBand+.028,b)*abdominalSpan*.91);
      skin*=1.-boundary*.22;
      // Melanophores on the back and skull, separated from the pale peritoneum.
      // Keep bronze/rose scale variation, rather than a uniform black stripe.
      vec3 dorsal=mix(vec3(.058,.039,.036),vec3(.132,.080,.070),soft);
      skin=mix(skin,dorsal,guppyBackPigment()*.91);
      skin=mix(skin,vec3(.055,.051,.045),guppyHeadPigment()*.79);
      float margin=x-fishOpercleX(vSkinPoint.y);
      skin*=1.-.28*exp(-pow(margin/.0026,2.))*(1.-smoothstep(.77,.98,b));
      skin+=vec3(.08,.09,.076)*exp(-pow((margin-.007)/.0038,2.));
      // Tonal differences are attached to scales, independent of colour-family.
      float mask=fishScaleMask()*guppySurfaceDetail;
      float grain=fishHash(floor(fishScaleGrid())+seed);
      skin*=1.+(grain-.5)*.21*mask-.25*guppyScaleEdge()*guppySurfaceDetail;
      // Optional photographic fine grain. Asset failure leaves the same skin,
      // palette and geometry rather than switching to a different fish design.
      if(guppyPlateReady>.5) {
        vec2 uv=vec2(mix(715.,1600.,clamp((x+.295)/.567,0.,1.))/1774.,
          1.-mix(360.,530.,b)/887.);
        vec3 px=guppyUsesBluePlate()&&guppyBlueReady>.5
          ?texture2D(guppyBluePlate,uv).rgb:texture2D(guppyPlate,uv).rgb;
        float lum=dot(px,vec3(.2126,.7152,.0722));
        skin*=1.+(smoothstep(.01,.40,lum)-.5)*.10*mask;
      }
      float cleft=exp(-pow((vSkinPoint.y-fishCleftY(x))/.0019,2.))*smoothstep(.311,.327,x);
      skin=mix(skin,vec3(.029,.023,.018),cleft*.82);
      float orbit=fishOrbit();
      float ring=(1.-smoothstep(1.,1.17,orbit))*smoothstep(.89,1.,orbit);
      return mix(skin,vec3(.33,.29,.17),ring*.55);
    }
    void main() {
  `).replace('#include <alphamap_fragment>', /* glsl */ `
    if(vFishPart<.5) {
      diffuseColor.rgb=guppySkin();
      gFishThrough*=.65*(1.-.80*max(guppyBackPigment(),guppyHeadPigment()));
    } else if(vFishPart<6.5) {
      float reach=clamp(vFishUV.y,0.,1.);
      float ribs=guppyRays();
      float caudal=1.-step(1.5,vFishPart);
      float dorsalAnal=step(1.5,vFishPart)*(1.-step(3.5,vFishPart));
      float pelvic=step(5.5,vFishPart);
      float coloured=max(caudal,max(dorsalAnal,pelvic));
      float pattern=guppyPatternAmount();
      vec2 point=vec2(vSkinPoint.x*-48.,vSkinPoint.y*37.)+vGuppySeed*29.;
      float cloud=gMottle(point);
      float root=guppyTailRoot(),edge=guppyFinClearEdge();
      float ink=smoothstep(.63,.78,cloud)*pattern*caudal*(1.-root)*(1.-edge);
      vec3 tint=guppyFinColor();
      // Dorsal and anal share the same pale tissue. Only the caudal has black root.
      tint=mix(tint,mix(tint,vec3(.42,.52,.59),.18),max(dorsalAnal,pelvic));
      tint=mix(vec3(.40,.46,.45),tint,coloured);
      vec3 membrane=tint*(.78+.18*cloud+.48*ribs);
      membrane=mix(membrane,vec3(.030,.038,.046),ink*.43);
      membrane=mix(membrane,vec3(.012,.016,.022)*(.86+.28*cloud),root*.96);
      diffuseColor.rgb=membrane;
      // Transparent tips transmit the backdrop through alpha, not a painted grey rim.
      // Black root absorbs the fill light instead of turning silver under it.
      gFishThrough=tint*.095*(1.-root)*(1.-edge)*(1.-.35*ribs)*coloured;
      #ifdef FISH_MEMBRANE
        float density=mix(.075,.43+.12*cloud,coloured)+.24*ribs;
        float clearAlpha=.025+.16*ribs;
        float alpha=mix(density,clearAlpha,edge);
        diffuseColor.a=clamp(mix(alpha,.94,root),.025,.95);
      #endif
    }
    #include <alphamap_fragment>
  `)
  .replace('float relief = fishScaleRelief() * 0.00030;',
    'float relief = guppyScaleHeight() * 0.00055 * guppySurfaceDetail;')
  .replace('#include <normal_fragment_maps>', /* glsl */ `
    #include <normal_fragment_maps>
    #ifdef FISH_MEMBRANE
      // A double-sided sheet gets the normal of its actual deformed surface.
      // dFdx/dFdy are screen-space, so their cross product already faces the eye.
      normal=normalize(cross(dFdx(vViewPosition),dFdy(vViewPosition)));
      float fold=sin(vFishUV.x*18.*PI2)*pow(vFishUV.y,1.5)*.00024;
      vec3 dx=dFdx(-vViewPosition),dy=dFdy(-vViewPosition);
      vec3 rx=cross(dy,normal),ry=cross(normal,dx);
      float det=dot(dx,rx);
      normal=normalize(abs(det)*normal-sign(det)*(dFdx(fold)*rx+dFdy(fold)*ry));
    #endif
  `)
  .replace('#include <lights_physical_fragment>', /* glsl */ `
    if(vFishPart<.5) {
      float reflector=fishReflector(fishBand,fishX);
      float mask=fishScaleMask()*guppySurfaceDetail;
      roughnessFactor=mix(.38,mix(.27,.40,fishHash(floor(fishScaleGrid())+13.)),mask);
      roughnessFactor=mix(roughnessFactor,.40,smoothstep(.69,.97,fishBand));
      float dark=max(guppyBackPigment(),guppyHeadPigment());
      metalnessFactor=(.08+.25*reflector)*(1.-.76*dark);
      roughnessFactor=mix(roughnessFactor,.51,dark*.70);
    } else if(vFishPart<6.5) {
      roughnessFactor=mix(mix(.49,.34,guppyRays()),.62,guppyTailRoot());
      metalnessFactor=.015;
    }
    #include <lights_physical_fragment>
    #ifdef USE_CLEARCOAT
      if(vFishPart<.5) material.clearcoat*=1.-.70*max(guppyBackPigment(),guppyHeadPigment());
    #endif
  `);
}
