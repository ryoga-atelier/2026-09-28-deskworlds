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
    // A little row-to-row variation keeps the overlapping scales from reading
    // as a perfectly repeated mesh while preserving their natural shingle arcs.
    float guppyScaleVariation(vec2 grid) {
      float cell=gNoise(floor(grid)+vec2(vGuppySeed*13.7, vGuppySeed*7.1));
      return (cell-.5)*.20+.024*sin(grid.y*2.1+vGuppySeed*9.);
    }
    // A free scale margin is a fine overlapping arc. Keep enough antialiasing
    // for wallpaper scale without turning the flank into a dark net.
    float guppyScaleEdge() {
      vec2 grid=fishScaleGrid(),cell=fract(grid)-.5;
      float arc=cell.x+.35-.88*cell.y*cell.y+guppyScaleVariation(grid);
      float aa=max(.008,fwidth(arc)*.45);
      return (1.-smoothstep(.014-aa,.048+aa,abs(arc)))*fishScaleMask();
    }
    float guppyScaleHeight() {
      vec2 grid=fishScaleGrid(),c=fract(grid)-.5;
      float arc=c.x+.35-.88*c.y*c.y+guppyScaleVariation(grid);
      float dome=smoothstep(-.06,.07,arc)*(1.-smoothstep(.26,.50,c.x));
      dome*=1.-smoothstep(.32,.51,abs(c.y));
      return dome*(.50+.50*fishHash(floor(grid)+1.3))*fishScaleMask();
    }
    float guppyBellyEdge() {
      float broad=gMottle(vec2(vSkinPoint.x*34.,vSkinPoint.y*72.)+vGuppySeed*17.);
      float fine=sin(vSkinPoint.x*83.+vGuppySeed*8.)
        *sin(vSkinPoint.y*57.-vGuppySeed*5.);
      return (broad-.5)*.15+fine*.012;
    }
    // One abdominal contour contains both pale tissue and the anal-root marking.
    // The gill shapes its front edge; pigment only partitions its interior.
    float guppyGillNotch(float x,float y) {
      float opercle=fishOpercleX(y);
      return exp(-pow((x-(opercle+.008))/.022,2.)
        -pow((y+.024)/.031,2.));
    }
    float guppyGillCleft(float x,float y) {
      float underEye=smoothstep(-.068,-.051,y)*(1.-smoothstep(.005,.030,y));
      return exp(-pow((x-fishOpercleX(y))/.0035,2.))*underEye;
    }
    float guppyAnalRootIndent(float x,float y) {
      // Broad rounded rear compartment, using the r8 semicircle's proportions.
      return exp(-pow((x-.010)/.034,2.)
        -pow((y+.042)/.033,2.));
    }
    float guppyBellyProfile(float x,float y) {
      vec2 bellyCoord=(vec2(x,y)-vec2(.105,-.037))/vec2(.133,.064);
      float oval=dot(bellyCoord,bellyCoord);
      return oval+1.08*guppyGillNotch(x,y);
    }
    // Nested coverage: the silver outer tissue must extend beyond the ivory
    // centre. Reversing these masks made the old outer-minus-inner rim vanish.
    float guppyBellyOuter(float radius) {
      return 1.-smoothstep(1.04,1.28,radius);
    }
    float guppyBellyInner(float radius) {
      return 1.-smoothstep(.72,1.03,radius);
    }
    float guppyBellySeam(float radius,float y) {
      float band=smoothstep(.98,1.07,radius)*(1.-smoothstep(1.17,1.32,radius));
      // The upper tissue boundary casts a small shadow; the underside is open
      // and pale, rather than a black outline all around the abdomen.
      return band*smoothstep(-.043,-.005,y);
    }
    float guppyAnalPigment(float x,float y) {
      // Both pale tissue and this marking share the full abdominal boundary.
      // Reaching the outer tissue avoids a pale pointed tip behind the marking.
      float attachment=exp(-pow(x/.025,2.)-pow((y+.067)/.015,2.));
      return max(guppyAnalRootIndent(x,y),.70*attachment);
    }
    float guppyFinFold(float u,float reach) {
      // Derivative helper pixels can lie outside the triangle at the fin root.
      // Clamp before the fractional power, or their NaNs become black speckles.
      return sin(u*18.*PI2)*pow(max(reach,0.),1.5)*.00024;
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
    float guppyCrossVeins() {
      // A few soft cross-struts keep the clear fin legible between its radial rays.
      // These are membrane supports, not scales painted onto the fin.
      float phase=vFishUV.y*15.+.20*sin(vFishUV.x*18.8496)
        +.055*sin(vFishUV.x*56.5487+vFishUV.y*7.);
      float aa=max(.035,fwidth(phase)*.72);
      float vein=1.-smoothstep(.08-aa,.19+aa,abs(fract(phase+.5)-.5));
      return vein*(1.-smoothstep(.75,1.35,fwidth(phase)));
    }
    // Pigment masks are in rest-space: rotating the fish never moves its colours.
    float guppyBackPigment() {
      float b=clamp(vFishUV.y,0.,1.);
      return 1.-smoothstep(.04,.18,b);
    }
    float guppyHeadPigment() {
      // A small orbital accent, not a dark mask over the entire face.
      return (1.-smoothstep(1.05,1.65,fishOrbit()))*.42;
    }
    float guppyTailRoot() {
      float caudal=1.-step(1.5,vFishPart);
      float edge=.115+.12*sin(vFishUV.x*3.14159265)+.010*sin(vFishUV.x*17.);
      return caudal*(1.-smoothstep(edge-.10,edge+.13,vFishUV.y));
    }
    float guppyFinClearEdge() {
      float caudal=1.-step(1.5,vFishPart);
      // Outer tail 22% and dorsal/anal 34% contain nearly clear tissue.
      // A plateau, not just a fade on the last few pixels, makes the third zone visible.
      return smoothstep(mix(.43,.60,caudal)+.012*sin(vFishUV.x*31.),mix(.66,.78,caudal),vFishUV.y);
    }
    vec3 guppyLongitudinalTone(vec3 skin,float x) {
      // Positive rest-space X is the head; negative X runs to the caudal root.
      // Keep this broad and smooth so the back reads lighter at the head and
      // gathers bronze pigment toward the peduncle from ordinary viewing distance.
      float headToTail=smoothstep(-.18,.30,x);
      // Preserve the fish's colour family while making the head-to-peduncle
      // value change obvious at wallpaper size. The tail stays coloured, never black.
      vec3 tailTone=skin*vec3(.60,.58,.56)+vec3(.030,.027,.022);
      vec3 headTone=skin*vec3(1.46,1.40,1.30)+vec3(.014,.012,.009);
      return mix(tailTone,headTone,headToTail);
    }
    vec3 guppySkin() {
      float x=vSkinPoint.x,b=clamp(vFishUV.y,0.,1.);
      float seed=vGuppySeed*37.;
      float soft=gMottle(vec2(x*22.,b*7.)+seed);
      // The reference has a warm bronze dorsum, rose-silver flank and pale belly.
      // Darker pigment stays in fine scale edges and local tissue, never a black cap.
      vec3 skin=mix(vec3(.18,.11,.075),vec3(.42,.28,.18),smoothstep(.08,.54,b));
      skin=mix(skin,vec3(.57,.46,.33),smoothstep(.53,.91,b));
      skin=mix(skin,vec3(.61,.52,.41),smoothstep(.91,.995,b));
      skin*=.90+.20*soft;
      float rose=exp(-pow((b-.38)/.22,2.));
      skin=mix(skin,vec3(.43,.29,.23),rose*.20);
      float violet=exp(-pow((b-.22)/.12,2.))*(1.-smoothstep(.13,.22,x));
      skin=mix(skin,vec3(.27,.22,.27),violet*.16);
      float rear=1.-smoothstep(-.06,.14,x+(soft-.5)*.035);
      float flank=smoothstep(.17,.36,b)*(1.-smoothstep(.58,.76,b));
      float islands=smoothstep(.43,.64,gMottle(vec2(x*38.,b*11.)+seed));
      vec3 pigment=mix(guppyBodyColor(),guppyFinColor(),.36);
      skin=mix(skin,pigment,rear*flank*(.14+.10*guppyPatternAmount())*islands);
      // Preserve the eight individual body colour families over the side flank;
      // the warm photographic base remains visible through each fish's pigment.
      float familyMask=smoothstep(.11,.26,b)*(1.-smoothstep(.72,.89,b));
      float familyTexture=.74+.26*gMottle(vec2(x*18.,b*6.)+seed+41.);
      skin=mix(skin,guppyBodyColor(),familyMask*(.28+.08*guppyPatternAmount())*familyTexture);
      // Apply after the family colour layer but before the separately shaped belly.
      skin=guppyLongitudinalTone(skin,x);
      // A softly lit, slightly lighter head transitions into the bronze back.
      skin=mix(skin,vec3(.57,.46,.34),smoothstep(.20,.32,x)*.24);
      // Two visible tissue layers: warm silver outside and pale ivory inside.
      // The upper seam and fin/gill insertions interrupt their shared contour.
      float bellyRadius=guppyBellyProfile(x,vSkinPoint.y)+guppyBellyEdge();
      float bellyOuter=guppyBellyOuter(bellyRadius);
      float belly=guppyBellyInner(bellyRadius);
      float bellyRim=clamp(bellyOuter-belly,0.,1.);
      skin=mix(skin,vec3(.52,.51,.44),bellyRim*.82);
      skin=mix(skin,vec3(.72,.72,.67),belly*.90);
      float bellySeam=guppyBellySeam(bellyRadius,vSkinPoint.y);
      skin=mix(skin,vec3(.075,.070,.060),bellySeam*.72);
      float bellyHighlight=belly*exp(-pow((x-.105)/.074,2.)
        -pow((vSkinPoint.y+.052)/.022,2.));
      skin=mix(skin,vec3(.80,.79,.74),bellyHighlight*.20);
      float pearl=exp(-pow((x-.105)/.083,2.)-pow((b-.68)/.15,2.));
      skin=mix(skin,vec3(.51,.57,.59),pearl*.28);
      float gold=exp(-pow((x-.016)/.026,2.)-pow((b-.65)/.17,2.));
      skin=mix(skin,vec3(.48,.30,.13),gold*.55);
      // The operculum has rose/sage-silver tissue of its own, distinct from the
      // dorsal bronze. Its rear edge stays anchored to the gill-cover seam.
      float gill=exp(-pow((x-(fishOpercleX(vSkinPoint.y)+.031))/.033,2.)
        -pow((vSkinPoint.y+.006)/.038,2.));
      float gillIridescence=smoothstep(-.015,.027,vSkinPoint.y);
      vec3 gillTint=mix(vec3(.60,.34,.30),vec3(.40,.54,.46),gillIridescence);
      skin=mix(skin,gillTint,gill*.66);
      float cheek=exp(-pow((x-.225)/.033,2.)-pow((b-.47)/.19,2.));
      skin=mix(skin,vec3(.52,.50,.43),cheek*.34);
      // Both colours occupy the same abdomen: its silver rim encloses the pale
      // centre and grey-brown rear marking without a separate outline around either.
      float analPigment=guppyAnalPigment(x,vSkinPoint.y);
      float bellyRoot=analPigment*bellyOuter;
      float rootGrain=gMottle(vec2(x*92.,vSkinPoint.y*145.)+seed+23.);
      float rootTexture=.80+.20*rootGrain;
      // A broad, gently edged compartment stays readable at the approved lightness.
      // Its outer tissue carries the same colour so a white rear point cannot peek out.
      skin=mix(skin,vec3(.105,.097,.079),smoothstep(.07,.42,analPigment+(rootGrain-.5)*.10)*rootTexture*.67*bellyOuter);
      // The other dark tissue stays at the caudal attachment and orbital edge.
      float base=1.-smoothstep(-.284,-.245,x);
      skin=mix(skin,vec3(.035,.028,.030),base*(.82+.06*guppyDarkRoot()));
      skin=mix(skin,vec3(.17,.105,.075),guppyHeadPigment()*.40);
      float margin=x-fishOpercleX(vSkinPoint.y);
      skin*=1.-.12*exp(-pow(margin/.0028,2.))*(1.-smoothstep(.77,.98,b));
      skin=mix(skin,vec3(.14,.10,.080),guppyGillCleft(x,vSkinPoint.y)*.42);
      skin+=vec3(.031,.027,.023)*exp(-pow((margin-.007)/.0045,2.));
      // Thin brown/lilac arc lines, with very little height: skin rather than armour.
      float mask=fishScaleMask()*guppySurfaceDetail;
      float grain=fishHash(floor(fishScaleGrid())+seed);
      skin*=1.+(grain-.5)*.20*mask;
      vec3 scaleTint=mix(vec3(.43,.34,.26),vec3(.61,.51,.40),grain);
      skin=mix(skin,scaleTint,mask*.16*(1.-.62*belly)*(1.-.85*bellyRoot));
      float line=guppyScaleEdge()*guppySurfaceDetail*(1.-.24*belly);
      // Scale margins inherit the local pigment and read as muted tissue, not
      // as identical black-brown outlines stamped over every colour family.
      vec3 scaleEdgeColor=skin*vec3(.52,.51,.50)+vec3(.043,.037,.031);
      skin=mix(skin,scaleEdgeColor,line*.82);
      skin+=vec3(.052,.041,.027)*guppyScaleHeight()*guppySurfaceDetail;
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
      float bellyRadius=guppyBellyProfile(vSkinPoint.x,vSkinPoint.y)+guppyBellyEdge();
      float localInk=max(guppyAnalPigment(vSkinPoint.x,vSkinPoint.y)*.72*guppyBellyOuter(bellyRadius),
        guppyBellySeam(bellyRadius,vSkinPoint.y)*.72);
      gFishThrough*=.65*(1.-.80*max(max(guppyBackPigment(),guppyHeadPigment()),localInk));
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
      float crossVeins=guppyCrossVeins()*smoothstep(.42,.76,edge);
      float ink=smoothstep(.63,.78,cloud)*pattern*caudal*(1.-root)*(1.-edge);
      vec3 tint=guppyFinColor();
      // Dorsal and anal share the same pale tissue. Only the caudal has black root.
      tint=mix(tint,mix(tint,vec3(.42,.52,.59),.18),max(dorsalAnal,pelvic));
      tint=mix(vec3(.40,.46,.45),tint,coloured);
      // Blue-family caudal rays stay visible through the clear membrane at normal
      // desktop scale, while their own palette colours remain distinct.
      if(caudal>.5 && guppyUsesBluePlate()) tint=mix(tint,vec3(.07,.28,.78),.22);
      vec3 membrane=tint*(.50+.14*cloud);
      vec3 rayTint=tint*1.18+vec3(.025,.055,.105);
      if(caudal>.5 && guppyUsesBluePlate()) rayTint=mix(rayTint,vec3(.12,.30,.68),.25);
      membrane=mix(membrane,rayTint,clamp(ribs*.62,0.,.72));
      membrane=mix(membrane,vec3(.030,.038,.046),ink*.43);
      membrane=mix(membrane,vec3(.012,.016,.022)*(.86+.28*cloud),root*.96);
      // The outside remains see-through, while a low chromatic veil prevents it
      // disappearing on blue water. Ray and cross-vein highlights retain depth.
      vec3 clearBase=guppyUsesBluePlate()?vec3(.16,.28,.48):vec3(.38,.45,.48);
      vec3 clearTint=mix(clearBase,tint*.70+vec3(.10,.14,.20),.68);
      membrane=mix(membrane,clearTint,edge*.88);
      vec3 veinTint=mix(vec3(.52,.62,.67),tint*1.18+vec3(.10,.13,.16),.38);
      membrane=mix(membrane,veinTint,crossVeins*edge*.16);
      diffuseColor.rgb=membrane;
      // Transparent tips transmit the backdrop through alpha, not a painted grey rim.
      // Black root absorbs the fill light instead of turning silver under it.
      gFishThrough=tint*.095*(1.-root)*(1.-edge)*(1.-.35*ribs)*coloured;
      #ifdef FISH_MEMBRANE
        float density=mix(.075,.37+.09*cloud,coloured)+.30*ribs;
        float clearAlpha=.11+.20*ribs+.050*crossVeins;
        float alpha=mix(density,clearAlpha,edge);
        diffuseColor.a=clamp(mix(alpha,.94,root),.025,.95);
      #endif
    }
    #include <alphamap_fragment>
  `)
  .replace('vFishUV * FISH_SCALES', 'vFishUV * vec2(20.0, 7.0)')
  .replace('float relief = fishScaleRelief() * 0.00030;',
    'float relief = guppyScaleHeight() * 0.00016 * guppySurfaceDetail;')
  .replace('#include <normal_fragment_maps>', /* glsl */ `
    #include <normal_fragment_maps>
    #ifdef FISH_MEMBRANE
      // A double-sided sheet gets the normal of its actual deformed surface.
      // dFdx/dFdy are screen-space, so their cross product already faces the eye.
      normal=normalize(cross(dFdx(vViewPosition),dFdy(vViewPosition)));
      float fold=guppyFinFold(vFishUV.x,vFishUV.y);
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
      roughnessFactor=mix(.44,mix(.38,.47,fishHash(floor(fishScaleGrid())+13.)),mask);
      roughnessFactor=mix(roughnessFactor,.40,smoothstep(.69,.97,fishBand));
      float dark=max(guppyBackPigment(),guppyHeadPigment());
      metalnessFactor=(.035+.11*reflector)*(1.-.76*dark);
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
