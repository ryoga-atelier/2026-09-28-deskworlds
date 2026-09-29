import * as THREE from 'three';
import { SURFACE_Y, waterTime } from './water.js';

export function backboardGradient(localY) {
  return THREE.MathUtils.smoothstep(localY, -10, 8);
}

function addCylinder(scene, name, radius, length, color, position, direction = new THREE.Vector3(0, 1, 0), materialOptions = {}) {
  const material = new THREE.MeshStandardMaterial({ color, roughness: 0.54, ...materialOptions });
  const mesh = new THREE.Mesh(new THREE.CylinderGeometry(radius * 0.92, radius, length, 10, 1), material);
  mesh.name = name;
  mesh.position.copy(position);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.clone().normalize());
  mesh.castShadow = mesh.receiveShadow = true;
  scene.add(mesh);
  return mesh;
}

function addCurve(scene, name, points, radius, material) {
  const curve = new THREE.CatmullRomCurve3(points);
  const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, Math.max(8, points.length * 5), radius, 5, false), material);
  mesh.name = name; mesh.castShadow = false; mesh.receiveShadow = true;
  scene.add(mesh);
  return mesh;
}

function addFilter(scene, group) {
  const x = 6.86, z = -5.45;
  const returnBottom = 2.35, returnTop = SURFACE_Y - 1.25;
  const returnLength = returnTop - returnBottom;
  const returnCentre = (returnTop + returnBottom) / 2;
  const graphite = new THREE.MeshStandardMaterial({ color: 0x819087, roughness: 0.62, metalness: 0.015 });
  const glass = new THREE.MeshPhysicalMaterial({ color: 0x9eafa7, roughness: 0.2, metalness: 0.08, transparent: true, opacity: 0.38, clearcoat: 0.7 });
  const returnPipe = new THREE.Mesh(new THREE.CylinderGeometry(0.019, 0.024, returnLength, 10), graphite);
  returnPipe.name = 'Aquarium filter return';
  returnPipe.position.set(x, returnCentre, z); returnPipe.castShadow = true; returnPipe.receiveShadow = true;
  group.add(returnPipe);
  const strainer = new THREE.Mesh(new THREE.CylinderGeometry(0.077, 0.055, 0.28, 12, 1), graphite);
  strainer.name = 'Submerged filter strainer'; strainer.position.set(x, 2.18, z); group.add(strainer);
  const lowerCap = new THREE.Mesh(new THREE.SphereGeometry(0.056, 10, 8), graphite);
  lowerCap.scale.set(1, 0.58, 1); lowerCap.position.set(x, 2.02, z); group.add(lowerCap);

  const hood = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.15, 0.12), graphite);
  hood.name = 'Filter outlet hood'; hood.position.set(x, returnTop + 0.015, z + 0.01); hood.castShadow = true; group.add(hood);
  addCylinder(group, 'Filter outflow lip', 0.037, 0.39, 0x56635d,
    new THREE.Vector3(x - 0.23, returnTop - 0.035, z + 0.04), new THREE.Vector3(-1, -0.08, 0), { metalness: 0.11 });

  const clip = new THREE.Mesh(new THREE.CylinderGeometry(0.074, 0.074, 0.045, 12), graphite);
  clip.name = 'Filter suction cup'; clip.position.set(x, returnTop - 1.1, z + 0.06); clip.rotation.x = Math.PI / 2; group.add(clip);
  const returnGlow = new THREE.MeshStandardMaterial({ color: 0xabc4b9, roughness: 0.22, transparent: true, opacity: 0.15, emissive: 0x283d35 });
  const highlightLength = returnLength * 0.82;
  const highlight = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, highlightLength, 5), returnGlow);
  highlight.name = 'Filter glass reflection'; highlight.position.set(x - 0.018, returnCentre, z + 0.03); group.add(highlight);

  // A single subdued heater at the opposite pane, with one faint status lamp.
  const heaterX = -5.75, heaterZ = -5.0;
  const heater = new THREE.Mesh(new THREE.CylinderGeometry(0.049, 0.049, 2.55, 12), glass);
  heater.name = 'Submerged aquarium heater'; heater.position.set(heaterX, 4.25, heaterZ); group.add(heater);
  for (const y of [3.37, 5.02]) {
    const suction = new THREE.Mesh(new THREE.SphereGeometry(0.062, 10, 8), graphite);
    suction.name = 'Heater suction cup'; suction.scale.set(1, 0.64, 0.46); suction.position.set(heaterX, y, heaterZ + 0.035); group.add(suction);
  }
  const foot = new THREE.Mesh(new THREE.CylinderGeometry(0.046, 0.04, 0.17, 10), graphite);
  foot.position.set(heaterX, 2.95, heaterZ); group.add(foot);
  const indicator = new THREE.Mesh(new THREE.SphereGeometry(0.012, 8, 6), new THREE.MeshBasicMaterial({ color: 0x92a77c }));
  indicator.name = 'Heater indicator'; indicator.position.set(heaterX, 4.85, heaterZ + 0.047); group.add(indicator);
  return { x, z };
}

function addGlassEdges(scene, group) {
  const reflection = new THREE.MeshBasicMaterial({ color: 0xd7e7de, transparent: true, opacity: 0.13, depthWrite: false, side: THREE.DoubleSide });
  const dimReflection = reflection.clone(); dimReflection.opacity = 0.065;
  const top = SURFACE_Y - 0.14;
  // Thin silicone seams and faint front-pane glints give the scene a glass tank boundary
  // without drawing a bright picture-frame around the whole desktop.
  for (const side of [-1, 1]) {
  const x = side * 6.32;
    addCurve(group, `Aquarium front glass highlights ${side}`, [
      new THREE.Vector3(x, 0.32, 5.7), new THREE.Vector3(x + side * 0.035, 2.4, 5.7),
      new THREE.Vector3(x, 5.9, 5.7), new THREE.Vector3(x - side * 0.018, top, 5.7),
  ], 0.012, reflection);
    addCurve(group, `Aquarium side-glass seam ${side}`, [
      new THREE.Vector3(x + side * 0.16, 0.3, 5.68), new THREE.Vector3(x + side * 0.16, 3.8, 5.68),
      new THREE.Vector3(x + side * 0.16, top, 5.68),
    ], 0.009, dimReflection);
  }
  addCurve(group, 'Aquarium top glass reflection', [
    new THREE.Vector3(-7.02, top, 5.69), new THREE.Vector3(-3.7, top + 0.015, 5.70),
    new THREE.Vector3(0, top, 5.70), new THREE.Vector3(3.9, top + 0.02, 5.70),
    new THREE.Vector3(7.02, top, 5.69),
  ], 0.012, dimReflection);
}

export function createAquariumDetails(scene) {
  const group = new THREE.Group();
  group.name = 'Aquarium glass, surface and equipment';
  scene.add(group);
  const outlet = addFilter(scene, group);
  addGlassEdges(scene, group);

  const surfaceGeometry = new THREE.PlaneGeometry(22, 7.6, 72, 16);
  const surfaceMaterial = new THREE.MeshPhysicalMaterial({
    color: 0x789b96, roughness: 0.28, metalness: 0.012,
    clearcoat: 0.52, clearcoatRoughness: 0.16,
    transparent: true, opacity: 0.07, depthWrite: false, side: THREE.DoubleSide,
  });
  const surface = new THREE.Mesh(surfaceGeometry, surfaceMaterial);
  surface.name = 'Water surface ripple';
  surface.rotation.x = -Math.PI / 2;
  surface.position.set(0, SURFACE_Y - 0.04, -1.7);
  surface.renderOrder = 3;
  surface.castShadow = false; surface.receiveShadow = false;
  scene.add(surface);
  const base = surfaceGeometry.attributes.position.array.slice();

  const rippleMaterial = new THREE.MeshBasicMaterial({
    color: 0xd9e8df, transparent: true, opacity: 0.20,
    depthWrite: false, side: THREE.DoubleSide,
  });
  const rippleGeometry = new THREE.TorusGeometry(1, 0.014, 4, 48);
  const ripples = Array.from({ length: 4 }, (_, i) => {
    const ring = new THREE.Mesh(rippleGeometry, rippleMaterial.clone());
    ring.name = 'Filter return surface ring'; ring.rotation.x = Math.PI / 2;
    ring.position.set(outlet.x - 0.49, SURFACE_Y - 0.055, outlet.z + 0.05);
    scene.add(ring);
    return { ring, phase: i / 4 };
  });

  const jetMaterial = new THREE.MeshBasicMaterial({ color: 0xb8d0c5, transparent: true, opacity: 0.11, depthWrite: false });
  const jet = addCurve(scene, 'Subtle filter return current', [
    new THREE.Vector3(outlet.x - 0.38, SURFACE_Y - 0.09, outlet.z + 0.05),
    new THREE.Vector3(outlet.x - 0.70, SURFACE_Y - 0.12, outlet.z + 0.06),
    new THREE.Vector3(outlet.x - 1.08, SURFACE_Y - 0.17, outlet.z + 0.08),
  ], 0.008, jetMaterial);
  jet.material.depthWrite = false;

  const update = (time) => {
    waterTime.value = time;
    const position = surfaceGeometry.attributes.position;
    for (let i = 0; i < position.count; i++) {
      const x = base[i * 3], v = base[i * 3 + 1];
      const z = surface.position.z - v;
      const nearReturn = Math.exp(-((x - (outlet.x - 0.55)) ** 2 / 1.2 + (z - outlet.z) ** 2 / 0.9));
      const broad = 0.008 * Math.sin(x * 0.43 + time * 0.48 + z * 0.16);
      const eddy = nearReturn * 0.018 * Math.sin(x * 2.2 - time * 1.1 + z * 1.4);
      position.setZ(i, broad + eddy);
    }
    position.needsUpdate = true;
    surfaceGeometry.computeVertexNormals();
    for (const { ring, phase } of ripples) {
      const travel = ((time * 0.11 + phase) % 1 + 1) % 1;
      const radius = 0.075 + travel * 0.34;
      ring.scale.set(radius, radius, radius);
      ring.updateMatrix();
      ring.material.opacity = 0.18 * (1 - travel);
      ring.visible = ring.material.opacity > 0.012;
    }
  };
  update(0);
  return { update, surface, ripples };
}
