// Local fancy-guppy appearance. Upstream anatomy/lighting remain in the adjacent base file.
import * as THREE from 'three';
import {
  makeAnatomy as originalAnatomy,
  applySkin as originalSkin,
  createFishMaterials,
} from './fish-anatomy-base.js';
export { SNOUT_X, STANDARD_LENGTH, createFishMaterials } from './fish-anatomy-base.js';

export function makeAnatomy() {
  const geometry = originalAnatomy();
  for (const mesh of Object.values(geometry)) {
    const p = mesh.getAttribute('position');
    const parts = mesh.getAttribute('aPart');
    const uv = mesh.getAttribute('uv');
    const progress = mesh.getAttribute('aFinProgress');
    for (let i = 0; i < p.count; i++) {
      const part = parts.getX(i);
      const span = progress.getX(i);
      let x = p.getX(i), y = p.getY(i) * 1.06, z = p.getZ(i);
      if (part === 1) {
        // A broad, unbroken delta fan: a guppy's tail, instead of the tetra's fork.
        const u = uv.getX(i);
        const angle = (0.5 - u) * 1.95;
        const scallop = 1 - 0.012 * (0.5 - 0.5 * Math.cos(u * 18 * Math.PI * 2));
        const rootX = -0.287;
        const rootY = 0.032 * (1 - 2 * u);
        const edgeX = rootX - 0.405 * Math.cos(angle) * scallop;
        const edgeY = 0.325 * Math.sin(angle) * scallop;
        x = THREE.MathUtils.lerp(rootX, edgeX, span);
        y = THREE.MathUtils.lerp(rootY, edgeY, span);
        z = Math.sin(u * Math.PI * 4) * Math.sin(span * Math.PI) * 0.009;
      } else if (part === 2) {
        // A soft dorsal veil trailing toward the caudal peduncle.
        x -= span * (0.025 + 0.10 * uv.getX(i));
        y += span * 0.065;
      } else if (part === 3) {
        y += span * 0.034;
      } else if (part === 7 || part === 8) {
        // Slightly larger pupils, with a continuous join to the surrounding iris.
        const dx = x - 0.272, dy = y / 1.06 - 0.012;
        const radius = Math.hypot(dx / 0.0335, dy / 0.0325);
        if (radius > 1e-7) {
          const wanted = part === 8 ? radius * (0.69 / 0.60)
            : 0.69 + (radius - 0.60) * (0.93 - 0.69) / (0.93 - 0.60);
          const scale = wanted / radius;
          x = 0.272 + dx * scale;
          y = (0.012 + dy * scale) * 1.06;
        }
      }
      p.setXYZ(i, x, y, z);
    }
    // Guppies have no adipose fin. Drop its triangles while retaining other part IDs.
    const old = mesh.getIndex();
    const indices = [];
    for (let i = 0; i < old.count; i += 3) {
      if (parts.getX(old.getX(i)) !== 12)
        indices.push(old.getX(i), old.getX(i + 1), old.getX(i + 2));
    }
    mesh.setIndex(indices);
    p.needsUpdate = true;
    mesh.computeVertexNormals();
    mesh.computeBoundingBox();
    mesh.computeBoundingSphere();
  }
  return geometry;
}

export function applySkin(shader) {
  originalSkin(shader);
  shader.vertexShader = shader.vertexShader
    .replace('#include <common>', `#include <common>
      attribute float aGuppyVariant;
      varying float vGuppyVariant;`)
    .replace('void main() {', 'void main() {\n vGuppyVariant = aGuppyVariant;');
  shader.fragmentShader = shader.fragmentShader
    .replace('#include <common>', `#include <common>
      varying float vGuppyVariant;
      vec3 guppyColor() {
        if (vGuppyVariant < 0.5) return vec3(0.94, 0.085, 0.12);
        if (vGuppyVariant < 1.5) return vec3(1.0, 0.48, 0.045);
        return vec3(0.035, 0.43, 0.93);
      }`)
    .replace('#include <alphamap_fragment>', /* glsl */ `
      // Pigment stays tied to an individual instance, never its changing swim phase.
      vec3 guppyHue = guppyColor();
      if (vFishPart < 0.5) {
        float flank = smoothstep(0.12, 0.38, fishBand);
        vec3 pearl = mix(vec3(0.17, 0.24, 0.22), vec3(0.76, 0.79, 0.67), flank);
        float rear = 1.0 - smoothstep(-0.18, 0.19, fishX);
        pearl = mix(pearl, guppyHue * 0.72 + vec3(0.11), rear * flank * 0.72);
        float bodyMark = exp(-pow((fishX + 0.06) / 0.078, 2.0)
          - pow((fishBand - 0.43) / 0.16, 2.0));
        pearl = mix(pearl, guppyHue * 0.20 + vec3(0.02, 0.04, 0.06), bodyMark * 0.50);
        // A warm cheek and small soft mouth keep the face bright against the plants.
        pearl = mix(pearl, vec3(0.77, 0.70, 0.52), fishHead * 0.52);
        diffuseColor.rgb = mix(diffuseColor.rgb, pearl, 0.86);
      } else if (vFishPart < 6.5) {
        float fan = 1.0 - step(2.5, vFishPart);
        float u = clamp(vFishUV.x, 0.0, 1.0);
        float reach = clamp(vFishUV.y, 0.0, 1.0);
        vec3 fin = mix(guppyHue * 0.65 + vec3(0.08), guppyHue, smoothstep(0.05, 0.65, reach));
        // Sparse dark lace, with a fine contrasting hem and translucent fin rays.
        vec2 grid = vec2(u * 7.0, reach * 4.5);
        grid.x += mod(floor(grid.y), 2.0) * 0.45;
        vec2 local = fract(grid) - 0.5;
        float spots = (1.0 - smoothstep(0.11, 0.20, length(local)))
          * smoothstep(0.24, 0.42, reach) * (1.0 - smoothstep(0.84, 0.98, reach));
        fin = mix(fin, guppyHue * 0.12 + vec3(0.015, 0.025, 0.055), spots * 0.68);
        float hem = smoothstep(0.91, 0.98, reach);
        fin = mix(fin, mix(vec3(0.99, 0.69, 0.34), vec3(0.36, 0.85, 0.95), step(1.5, vGuppyVariant)), hem * 0.52);
        float rays = 0.5 + 0.5 * cos(u * PI2 * (vFishPart < 1.5 ? 18.0 : 10.0));
        fin *= 0.88 + 0.12 * rays;
        diffuseColor.rgb = mix(diffuseColor.rgb, fin, fan * 0.96 + (1.0 - fan) * 0.55);
        #ifdef FISH_MEMBRANE
          diffuseColor.a = mix(diffuseColor.a, 0.82 - 0.12 * hem, fan);
        #endif
      } else if (vFishPart > 7.5 && vFishPart < 8.5) {
        float glint = exp(-pow((vSkinPoint.x - 0.281) / 0.007, 2.0)
          - pow((vSkinPoint.y - 0.023) / 0.007, 2.0));
        diffuseColor.rgb = mix(vec3(0.008, 0.015, 0.022), vec3(0.87, 0.97, 1.0), glint);
      }
      #include <alphamap_fragment>
    `);
}
