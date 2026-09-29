// Natural fancy-guppy appearance, based on observed ornamental-guppy photographs.
// The adjacent base retains the upstream surface, gill, eye and tissue-light models.
import * as THREE from 'three';
import {
  makeAnatomy as originalAnatomy,
  applySkin as originalSkin,
  createFishMaterials as originalMaterials,
} from './fish-anatomy-base.js';
export { SNOUT_X, STANDARD_LENGTH } from './fish-anatomy-base.js';

export function createFishMaterials() {
  const result = originalMaterials();
  result.skin.clearcoat = 0.045;
  result.skin.clearcoatRoughness = 0.36;
  result.skin.iridescence = 0.38;
  result.skin.envMapIntensity = 0.70;
  result.fins.roughness = 0.48;
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
        const scallop = 1 - 0.018 * Math.pow(0.5 - 0.5 * Math.cos(ray * Math.PI * 2), 1.3)
          + 0.012 * Math.sin(ray * 5.3) + 0.007 * Math.sin(ray * 11.7);
        const across = (0.5 - u) * 2;
        const rootX = -0.288 + 0.010 * across * across;
        const edgeX = -0.680 + 0.067 * Math.pow(Math.abs(across), 2.8)
          + 0.006 * Math.sin(u * 17.3);
        const edgeY = across * (0.264 + 0.012 * Math.sin(u * 3.1 + 0.4));
        x = THREE.MathUtils.lerp(rootX, edgeX, span * scallop);
        y = THREE.MathUtils.lerp(0.031 * across, edgeY, span * scallop);
        z = Math.pow(span, 1.4) * (0.010 * Math.sin(u * 13 + 0.5)
          + 0.005 * Math.sin(u * 31 - span * 2));
      } else if (part === 2) {
        // Long, low dorsal veil: its free edge trails behind the insertion.
        const rootX = -0.020 - u * 0.075;
        const rootY = 0.067 - 0.011 * u;
        const edgeX = -0.016 - 0.24 * u;
        const edgeY = 0.082 + 0.090 * Math.sin(Math.PI * u);
        x = THREE.MathUtils.lerp(rootX, edgeX, span);
        y = THREE.MathUtils.lerp(rootY, edgeY, span);
        z += span * span * 0.010 * Math.sin(u * 7.3);
      } else if (part === 3) {
        // Male guppy's narrow gonopodium, rather than the tetra's broad anal skirt.
        x = -0.035 - 0.065 * u - span * 0.11;
        y = -0.075 - 0.014 * u - span * 0.024;
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
    mesh.computeBoundingBox(); mesh.computeBoundingSphere();
  }
  return geometry;
}

export function applySkin(shader) {
  originalSkin(shader);
  shader.vertexShader = shader.vertexShader
    .replace('#include <common>', `#include <common>
      varying float vGuppyVariant;
      varying float vGuppySeed;`)
    .replace('void main() {', `void main() {
      vGuppyVariant = aGuppyVariant;
      vGuppySeed = aGuppySeed;`);
  shader.fragmentShader = shader.fragmentShader
    .replace('#include <common>', /* glsl */ `#include <common>
      varying float vGuppyVariant;
      varying float vGuppySeed;
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
      vec3 gTailColor(float detail, float reach) {
        if (vGuppyVariant < 0.5)
          return mix(vec3(0.27,0.010,0.0025),vec3(0.72,0.14,0.014),detail);
        if (vGuppyVariant < 1.5)
          return mix(vec3(0.14,0.10,0.008),vec3(0.61,0.40,0.065),detail);
        return mix(vec3(0.009,0.033,0.16),vec3(0.050,0.37,0.53),detail);
      }
    `)
    .replace('#include <alphamap_fragment>', /* glsl */ `
      float seed = vGuppySeed * 37.0;
      if (vFishPart < 0.5) {
        vec2 point = vec2(fishX * 31.0, fishBand * 9.0);
        float detail = gMottle(point + seed);
        float rear = 1.0 - smoothstep(-0.06, 0.16,
          fishX + (gNoise(vec2(fishBand*8.0,seed))-0.5)*0.055);
        float side = smoothstep(0.13,0.28,fishBand)
          * (1.0-smoothstep(0.66,0.91,fishBand));
        // Olive skull and silver belly; pigment extends over the entire rear body.
        vec3 natural = diffuseColor.rgb * vec3(0.61,0.67,0.61);
        vec3 cheek = mix(vec3(0.024,0.034,0.022),vec3(0.23,0.24,0.16),
          smoothstep(0.14,0.54,fishBand));
        float gillWarm=exp(-pow((fishX-0.183)/0.031,2.0)-pow((fishBand-0.64)/0.18,2.0));
        cheek=mix(cheek,vec3(0.22,0.13,0.085),gillWarm*0.38);
        natural=mix(natural,cheek,smoothstep(0.12,0.24,fishX)*0.82);
        vec3 coat = vGuppyVariant < 0.5 ? vec3(0.009,0.022,0.026)
          : (vGuppyVariant < 1.5 ? vec3(0.22,0.21,0.048) : vec3(0.012,0.085,0.155));
        coat *= 0.65 + 0.80 * detail;
        // Blue grass and golden snakeskin have broken, interlocking markings.
        vec2 warped = point + vec2(gNoise(point*0.6+seed),gNoise(point*0.63-seed))*1.8;
        float lace = smoothstep(0.42,0.54,gMottle(warped*2.4));
        coat = mix(coat, vec3(0.008,0.013,0.011),lace*(vGuppyVariant<0.5?0.3:0.70));
        float iridBand = exp(-pow((fishBand-0.35)/0.19,2.0));
        coat += vec3(0.012,0.063,0.060) * iridBand * (0.4+detail);
        natural = mix(natural,coat,rear * (0.25+0.75*side));
        // Small orange chromatophore patches, not a uniform painted body.
        float orange = exp(-pow((fishX-0.056+vGuppySeed*0.038)/0.041,2.0)
          -pow((fishBand-0.50)/0.16,2.0)) * smoothstep(0.25,0.52,detail);
        natural = mix(natural,vec3(0.43,0.095,0.012),orange*0.50);
        // The original scale relief and gill/eye geometry remain; pigment follows scales.
        vec2 grid = fishScaleGrid();
        vec2 scaleCell = fract(grid)-0.5;
        float scaleEdge = smoothstep(0.33,0.50,length(scaleCell*vec2(0.88,1.0)));
        float scaleDetail = fishScaleMask();
        natural *= 1.0 - 0.08*scaleEdge*scaleDetail;
        natural += vec3(0.010,0.016,0.012)*pow(1.0-scaleEdge,5.0)
          * (0.2+gHash(floor(grid)+seed))*scaleDetail*side;
        diffuseColor.rgb = natural;
        gFishThrough *= 0.42;
      } else if (vFishPart < 6.5) {
        float broad = 1.0-step(2.5,vFishPart);
        float u=clamp(vFishUV.x,0.0,1.0), reach=clamp(vFishUV.y,0.0,1.0);
        vec2 point=vec2(u*(6.0+5.0*reach),reach*5.5);
        point += vec2(seed,seed*0.73);
        float detail=gMottle(point*1.9);
        vec2 warped=point+vec2(gNoise(point*1.3),gNoise(point*1.3+12.0))*0.85;
        float grass=gIslands(warped*1.7);
        float cobra=smoothstep(0.40,0.57,gMottle(warped*2.1));
        float markings=mix(grass,cobra,step(0.5,vGuppyVariant)*(1.0-step(1.5,vGuppyVariant)));
        markings *= smoothstep(0.04,0.21,reach);
        vec3 pigment=gTailColor(detail,reach);
        pigment=mix(pigment,vec3(0.003,0.007,0.010),markings*0.93);
        // Fine branching rays and a clear fringe. No thick, uniform outline.
        float rayPhase=u*18.0 + 0.035*sin(reach*9.0+u*22.0);
        float primary=pow(0.5+0.5*cos(rayPhase*PI2),18.0);
        float branched=pow(0.5+0.5*cos((rayPhase*2.0+0.5)*PI2),20.0)
          *smoothstep(0.42,0.80,reach);
        float ribs=clamp(primary+branched,0.0,1.0)*fishFade(vec2(u*36.0,reach));
        pigment *= 1.0-0.30*ribs;
        float clearEdge=smoothstep(0.90+0.035*sin(u*38.0),1.0,reach);
        pigment=mix(pigment,vec3(0.19,0.24,0.21),clearEdge*0.35);
        diffuseColor.rgb=mix(vec3(0.16,0.20,0.17),pigment,broad);
        // Light passing through the sheet is tinted by its pigment, with dark rays.
        gFishThrough = mix(vec3(0.065,0.085,0.07),pigment*0.25,broad)
          *(1.0-0.85*markings)*(1.0-0.45*ribs);
        #ifdef FISH_MEMBRANE
          float opacity=mix(0.45,0.76,detail)+0.15*markings+0.06*ribs;
          opacity *= (1.0-0.57*clearEdge)*smoothstep(0.0,0.10,reach);
          diffuseColor.a=mix(0.22+0.15*ribs,opacity,broad);
        #endif
      } else if (vFishPart < 7.5) {
        diffuseColor.rgb *= vec3(0.58,0.65,0.64);
      } else if (vFishPart < 8.5) {
        // A black pupil gets its tiny highlight from the actual scene lights.
        diffuseColor.rgb=vec3(0.003,0.004,0.0045);
      }
      #include <alphamap_fragment>
    `)
    .replace('#include <lights_physical_fragment>', /* glsl */ `
      if (vFishPart<0.5) {
        roughnessFactor=max(roughnessFactor,0.36);
        metalnessFactor=min(metalnessFactor,0.23);
      } else if (vFishPart<6.5) {
        roughnessFactor=0.46;
        metalnessFactor=0.02;
      }
      #include <lights_physical_fragment>
    `);
}
