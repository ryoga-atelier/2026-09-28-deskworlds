// Mixed pet-shop guppy appearance, based on observed ornamental-guppy photographs.
// The adjacent base retains the upstream surface, gill, eye and tissue-light models.
import * as THREE from 'three';
import { applyPhotographicPigment } from './photo-material.js';
import { GUPPY_PALETTE_GLSL } from './guppy-palette.js';
import {
  makeAnatomy as originalAnatomy,
  profile, surfacePoint,
  applySkin as originalSkin,
  createFishMaterials as originalMaterials,
} from './fish-anatomy-base.js';
export { SNOUT_X, STANDARD_LENGTH } from './fish-anatomy-base.js';

export function createFishMaterials() {
  const result = originalMaterials();
  result.skin.clearcoat = 0.08;
  result.skin.clearcoatRoughness = 0.32;
  result.skin.iridescence = 0.30;
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
        // Modest rounded tail observed in the selected mixed-guppy photograph.
        // It starts inside the peduncle and the membrane opens gradually from it.
        const ray = u * 18;
        const scallop = 1 - 0.004 * Math.pow(0.5 - 0.5 * Math.cos(ray * Math.PI * 2), 1.3)
          + 0.002 * Math.sin(ray * 5.3) + 0.001 * Math.sin(ray * 11.7);
        const across = (0.5 - u) * 2;
        const rootX = -0.291 + 0.006 * across * across;
        const edgeX = -0.546 + 0.071 * Math.pow(Math.abs(across), 2.2)
          + 0.001 * Math.sin(u * 17.3);
        const edgeY = 0.016 + 0.140 * Math.sin(across*1.28)/Math.sin(1.28);
        x = THREE.MathUtils.lerp(rootX, edgeX, span * scallop);
        y = THREE.MathUtils.lerp(0.0165 + 0.0455 * across, edgeY, Math.sin(span*Math.PI*.5) * scallop);
        z = Math.pow(span, 1.45) * (0.008 * Math.sin(u * 8.1 + 0.5) + 0.003 * Math.sin(u * 19 - span * 2));
      } else if (part === 2) {
        // Small trailing dorsal on the posterior half of the body.
        const rootX = -0.025 - u * 0.115;
        const rootY = profile(rootX).top - 0.003;
        const edgeX = -0.020 - 0.220 * u;
        const edgeY = rootY + 0.073 * Math.sin(Math.PI * u);
        x = THREE.MathUtils.lerp(rootX, edgeX, span);
        y = THREE.MathUtils.lerp(rootY, edgeY, span);
        z += span * span * 0.010 * Math.sin(u * 7.3);
      } else if (part === 3) {
        // Small triangular anal membrane, as visible in the selected blue specimen.
        x = THREE.MathUtils.lerp(0.020 - 0.054*u, -0.072 - 0.087*u, span);
        y = THREE.MathUtils.lerp(-0.062 + 0.009*u, -0.065 - 0.070*Math.sin(Math.PI*u), span);
        z *= 0.55;
      }
      if (part === 4 || part === 5) {
        x += span * (x - .162) * .10;
        y += span * (y + .048) * .10;
        z *= 1 + span * .16;
      } else if (part === 6) {
        const side=z<0?-1:1;
        const root=surfacePoint(.080-.030*u,-.87,side);
        const leaf=Math.sin(Math.PI*u);
        x=THREE.MathUtils.lerp(root.x,-.050-.060*leaf,span);
        y=THREE.MathUtils.lerp(root.y,-.101-.030*leaf,span);
        z=THREE.MathUtils.lerp(root.z,side*(.031+.024*leaf),span);

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
    .replace('vSkinPoint = position;', 'vSkinPoint = aPigmentPoint;');
  shader.fragmentShader = shader.fragmentShader.replace('#include <common>', `#include <common>
    varying float vGuppyVariant;
    varying float vGuppySeed;
    ${GUPPY_PALETTE_GLSL}`);
  applyPhotographicPigment(shader);
}
