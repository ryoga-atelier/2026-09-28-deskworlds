// Natural fancy-guppy appearance, based on observed ornamental-guppy photographs.
// The adjacent base retains the upstream surface, gill, eye and tissue-light models.
import * as THREE from 'three';
import { applyPhotographicPigment } from './photo-material.js';
import { GUPPY_PALETTE_GLSL } from './guppy-palette.js';
import {
  makeAnatomy as originalAnatomy,
  applySkin as originalSkin,
  createFishMaterials as originalMaterials,
} from './fish-anatomy-base.js';
export { SNOUT_X, STANDARD_LENGTH } from './fish-anatomy-base.js';

export function createFishMaterials() {
  const result = originalMaterials();
  result.skin.clearcoat = 0.035;
  result.skin.clearcoatRoughness = 0.48;
  result.skin.iridescence = 0.42;
  result.skin.envMapIntensity = 0.90;
  result.skin.roughness = 0.34;
  result.skin.metalness = 0.16;
  result.fins.roughness = 0.50;
  result.fins.metalness = 0.02;
  // Derivatives of the deformed surface keep highlights on a moving veil.
  // The dense membrane mesh makes faceting subpixel at desktop scale.
  result.fins.flatShading = true;
  return result;
}

export function makeAnatomy() {
  const geometry = originalAnatomy();
  for (const mesh of Object.values(geometry)) {
    const p = mesh.getAttribute('position'), parts = mesh.getAttribute('aPart');
    const uv = mesh.getAttribute('uv'), progress = mesh.getAttribute('aFinProgress');
    for (let i = 0; i < p.count; i++) {
      const part = parts.getX(i), span = progress.getX(i), u = uv.getX(i);
      let x = p.getX(i), y = p.getY(i), z = p.getZ(i);
      if (part === 1) {
        // Delta tail with a slightly convex, uneven free edge, not a circular fan.
        // It starts inside the peduncle and the membrane opens gradually from it.
        const ray = u * 18;
        const scallop = 1 - 0.004 * Math.pow(0.5 - 0.5 * Math.cos(ray * Math.PI * 2), 1.3)
          + 0.002 * Math.sin(ray * 5.3) + 0.001 * Math.sin(ray * 11.7);
        const across = (0.5 - u) * 2;
        const rootX = -0.291 + 0.006 * across * across;
        const edgeX = -0.616 + 0.155 * Math.pow(Math.abs(across), 2.2)
          + 0.006 * Math.sin(u * 17.3);
        const edgeY = across * (0.207 + 0.009 * Math.sin(u * 3.1 + 0.4));
        x = THREE.MathUtils.lerp(rootX, edgeX, span * scallop);
        y = THREE.MathUtils.lerp(0.025 + 0.017 * across, edgeY, span * scallop);
        z = Math.pow(span, 1.45) * (0.008 * Math.sin(u * 8.1 + 0.5) + 0.003 * Math.sin(u * 19 - span * 2));
      } else if (part === 2) {
        // Long, low dorsal veil: its free edge trails behind the insertion.
        const rootX = 0.038 - u * 0.118;
        const rootY = 0.083 - 0.021 * u;
        const edgeX = 0.025 - 0.27 * u;
        const edgeY = 0.085 + 0.109 * Math.sin(Math.PI * u);
        x = THREE.MathUtils.lerp(rootX, edgeX, span);
        y = THREE.MathUtils.lerp(rootY, edgeY, span);
        z += span * span * 0.010 * Math.sin(u * 7.3);
      } else if (part === 3) {
        // Male guppy's narrow gonopodium, rather than the tetra's broad anal skirt.
        x = 0.052 - 0.013 * u - span * 0.133;
        y = -0.049 + 0.005 * u - span * 0.035;
        z *= 0.55;
      }
      p.setXYZ(i, x, y, z);
    }
    const old = mesh.getIndex(), indices = [];
    for (let i = 0; i < old.count; i += 3) {
      if (parts.getX(old.getX(i)) !== 12)
        indices.push(old.getX(i), old.getX(i + 1), old.getX(i + 2));
    }
    mesh.setIndex(indices);
    p.needsUpdate = true;
    // Keep the base's analytic body/eye normals; only the remodeled fins need these.
    if (mesh === geometry.fins) mesh.computeVertexNormals();
    // Preserve the old skin coordinates, including fin roots, for pigment mapping.
    mesh.setAttribute('aPigmentPoint', p.clone());
    mesh.computeBoundingBox(); mesh.computeBoundingSphere();
  }
  return geometry;
}

export function applySkin(shader) {
  originalSkin(shader);
  shader.vertexShader = shader.vertexShader
    .replace('#include <common>', `#include <common>
      varying float vGuppyVariant;
      varying float vGuppySeed;
      attribute vec3 aPigmentPoint;`)
    .replace('void main() {', `void main() {
      vGuppyVariant = aGuppyVariant;
      vGuppySeed = aGuppySeed;`)
    .replace("vSkinPoint = position;", "vSkinPoint = aPigmentPoint;");
  shader.fragmentShader = shader.fragmentShader
    .replace('#include <common>', /* glsl */ `#include <common>
      varying float vGuppyVariant;
      varying float vGuppySeed;
      ${GUPPY_PALETTE_GLSL}
      float gHash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
      vec2 gHash2(vec2 p) { return vec2(gHash(p), gHash(p + vec2(39.7, 81.3))); }
      float gNoise(vec2 p) {
        vec2 c = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
        return mix(mix(gHash(c),gHash(c+vec2(1,0)),f.x),
          mix(gHash(c+vec2(0,1)),gHash(c+vec2(1,1)),f.x),f.y);
      }
      float gMottle(vec2 p) {
        return 0.58*gNoise(p) + 0.28*gNoise(p*2.07+vec2(3.2,8.6))
          + 0.14*gNoise(p*4.13+vec2(7.3,2.8));
      }
      // Irregular chromatophore islands. Jittered cells avoid a printed dot grid.
      float gIslands(vec2 p) {
        vec2 cell = floor(p), f = fract(p);
        float nearest = 3.0;
        for (int j=-1;j<=1;j++) for (int i=-1;i<=1;i++) {
          vec2 offset=vec2(float(i),float(j));
          vec2 h=gHash2(cell+offset+vGuppySeed*91.0);
          vec2 delta=offset+0.15+0.7*h-f;
          delta.x *= 0.70+0.65*h.y;
          nearest=min(nearest,length(delta)/(0.63+0.55*h.x));
        }
        return 1.0-smoothstep(0.18,0.36,nearest);
      }
      vec3 gBodyPigment() { return guppyBodyColor()*.80; }
      vec3 gTailColor(float detail, float reach) {
        return mix(guppyBodyColor(),guppyFinColor(),smoothstep(.08,.72,reach))
          * (.64+.52*detail);
      }
    `)
    .replace('#include <alphamap_fragment>', /* glsl */ `
      float seed = vGuppySeed * 37.0;
      if (vFishPart < 0.5) {
        vec2 point = vec2(fishX * 23.0, fishBand * 7.0);
        float detail = gMottle(point + seed);
        float rear = 1.0 - smoothstep(vGuppyVariant>0.5 && vGuppyVariant<1.5 ? 0.01 : 0.11, 0.25,
          fishX + (gNoise(vec2(fishBand*8.0,seed))-0.5)*0.055);
        float side = smoothstep(0.13,0.28,fishBand)
          * (1.0-smoothstep(0.66,0.91,fishBand));
        // Pearl, champagne and cool slate bodies; hue variation reaches the shoulder so
        // the fish do not read as grey models carrying colour only in their tails.
        vec3 dorsal = vec3(.20,.25,.23);
        vec3 natural = mix(dorsal,vec3(.52,.57,.55),smoothstep(0.12,0.50,fishBand));
        natural = mix(natural,vec3(.64,.62,.53),smoothstep(0.63,0.98,fishBand));
        natural *= 0.88+0.23*detail;
        vec3 cheek = mix(dorsal,vec3(.56,.58,.53),
          smoothstep(0.14,0.54,fishBand));
        float gillWarm=exp(-pow((fishX-0.183)/0.031,2.0)-pow((fishBand-0.64)/0.18,2.0));
        cheek=mix(cheek,vec3(0.22,0.13,0.085),gillWarm*0.38);
        natural=mix(natural,cheek,smoothstep(0.12,0.24,fishX)*0.82);
        vec3 coat = guppyBodyColor()*.84;
        coat *= 0.65 + 0.80 * detail;
        // Blue grass and golden snakeskin have broken, interlocking markings.
        vec2 warped = point + vec2(gNoise(point*0.6+seed),gNoise(point*0.63-seed))*1.8;
        float laceNoise = gMottle(warped*2.4);
        float lace = 1.0-smoothstep(0.032,0.095,abs(laceNoise-0.49));
        coat = mix(coat, vec3(0.008,0.013,0.011),lace*(vGuppyVariant<0.5?0.3:0.70));
        float iridBand = exp(-pow((fishBand-0.35)/0.19,2.0));
        coat += vec3(0.012,0.063,0.060) * iridBand * (0.4+detail);
        natural = mix(natural,coat,rear * (0.55+0.45*side));
        float shoulder = exp(-pow((fishX-0.105)/0.060,2.0));
        natural = mix(natural,coat*0.76,shoulder*side*0.42);
        float opercleSeam = exp(-pow((fishX-fishOpercleX(fishY))/0.0035,2.0));
        natural *= 1.0-0.14*opercleSeam*(1.0-smoothstep(0.80,1.0,fishBand));
        // Small orange chromatophore patches, not a uniform painted body.
        float orange = exp(-pow((fishX-0.056+vGuppySeed*0.038)/0.041,2.0)
          -pow((fishBand-0.50)/0.16,2.0)) * smoothstep(0.25,0.52,detail);
        natural = mix(natural,vec3(0.43,0.095,0.012),orange*0.50);
        // The original scale relief and gill/eye geometry remain; pigment follows scales.
        vec2 grid = fishScaleGrid();
        vec2 scaleCell = fract(grid)-0.5;
        float scaleEdge = smoothstep(0.33,0.50,length(scaleCell*vec2(0.88,1.0)));
        float scaleDetail = fishScaleMask();
        natural *= 1.0 - 0.07*scaleEdge*scaleDetail;
        natural += vec3(0.008,0.012,0.010)*pow(1.0-scaleEdge,5.0)
          * (0.2+gHash(floor(grid)+seed))*scaleDetail*side;
        // Preserve the anatomical mouth and orbit after replacing tetra pigment.
        float cleft=exp(-pow((fishY-fishCleftY(fishX))/0.0018,2.0))
          *smoothstep(0.311,0.326,fishX);
        natural=mix(natural,vec3(0.023,0.020,0.016),cleft*0.70);
        float orbit=fishOrbit();
        float ring=(1.0-smoothstep(1.0,1.17,orbit))*smoothstep(0.89,1.0,orbit);
        natural=mix(natural,vec3(0.24,0.21,0.105),ring*0.55);
        diffuseColor.rgb = natural;
        gFishThrough *= 0.75;
      } else if (vFishPart < 6.5) {
        float broad = 1.0-step(2.5,vFishPart);
        float u=clamp(vFishUV.x,0.0,1.0), reach=clamp(vFishUV.y,0.0,1.0);
        // Pigment lives on the membrane in physical coordinates, not fan UVs:
        // a mosaic patch keeps its proportions instead of becoming a radial stripe.
        vec2 point=vec2((vSkinPoint.x+0.29)*-36.0,vSkinPoint.y*30.0);
        point += vec2(seed,seed*0.73);
        float detail=gMottle(point*0.9);
        vec2 warped=point+vec2(gNoise(point*1.3),gNoise(point*1.3+12.0))*0.85;
        float grass=gIslands(warped*1.35);
        float cob=gMottle(warped*1.8);
        float aa=max(0.025,fwidth(cob)*1.5);
        float cobra=1.0-smoothstep(0.035-aa,0.09+aa,abs(cob-0.49));
        float mosaic=smoothstep(0.44-aa,0.51+aa,gMottle(warped*1.4+vec2(3.7,1.4)));
        float markings=vGuppyVariant < 0.5 ? grass
          : (vGuppyVariant < 1.5 ? mix(grass,mosaic,0.35) : (vGuppyVariant < 2.5 ? cobra
          : (vGuppyVariant < 3.5 ? mosaic : mix(grass,cobra,0.15))));
        markings *= smoothstep(0.04,0.21,reach);
        vec3 pigment=gTailColor(detail,reach);
        pigment=mix(pigment,vec3(0.008,0.012,0.018),markings*(vGuppyVariant>3.5?0.45:0.90));
        // Fine branching rays and a clear fringe. No thick, uniform outline.
        float rayPhase=u*18.0 + 0.035*sin(reach*9.0+u*22.0);
        float primary=pow(0.5+0.5*cos(rayPhase*PI2),18.0);
        float branched=pow(0.5+0.5*cos((rayPhase*2.0+0.5)*PI2),20.0)
          *smoothstep(0.42,0.80,reach);
        float ribs=clamp(primary+branched,0.0,1.0)*fishFade(vec2(u*36.0,reach));
        pigment *= 1.0-0.085*ribs;
        float clearEdge=smoothstep(0.90+0.035*sin(u*38.0),1.0,reach);
        pigment*=1.0-0.08*clearEdge;
        diffuseColor.rgb=mix(vec3(0.16,0.20,0.17),pigment,broad);
        // Light passing through the sheet is tinted by its pigment, with dark rays.
        gFishThrough = mix(vec3(0.065,0.085,0.07),pigment*0.15,broad)
          *(1.0-0.85*markings)*(1.0-0.45*ribs);
        #ifdef FISH_MEMBRANE
          float opacity=mix(0.60,0.78,detail)+0.19*markings+0.02*ribs;
          opacity *= (1.0-0.40*clearEdge)*smoothstep(0.0,0.10,reach);
          diffuseColor.a=mix(0.22+0.15*ribs,opacity,broad);
        #endif
      } else if (vFishPart < 7.5) {
        diffuseColor.rgb=vec3(0.43,0.43,0.32);
      } else if (vFishPart < 8.5) {
        // A black pupil gets its tiny highlight from the actual scene lights.
        diffuseColor.rgb=vec3(0.003,0.004,0.0045);
      }
      #include <alphamap_fragment>
    `)
    .replace('#include <normal_fragment_maps>', /* glsl */ `
      #include <normal_fragment_maps>
      #ifdef FISH_MEMBRANE
        vec3 membraneNormal = normalize(cross(dFdx(vViewPosition), dFdy(vViewPosition)));
        normal = membraneNormal;
      #endif
    `)
    .replace('#include <lights_physical_fragment>', /* glsl */ `
      if (vFishPart<0.5) {
        roughnessFactor=clamp(roughnessFactor,0.20,0.45);
        metalnessFactor=min(metalnessFactor*1.30,0.55);
      } else if (vFishPart<6.5) {
        roughnessFactor=0.50;
        metalnessFactor=0.02;
      }
      #include <lights_physical_fragment>
    `);
  applyPhotographicPigment(shader);
}
