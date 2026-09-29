import * as THREE from 'three';
import { groundHeight } from './math.js';
import { ROCKS, rockCenterY } from './environment.js';
import { woodPoint, WOOD_SCALE } from './aquascape-layout.js';

export const SHRIMP_COUNT = 3;
export const BODY_CLEARANCE = 0.022;
const SHRIMP_SCALE = 1.14;
const WOOD_RADIUS = 0.12 * WOOD_SCALE;
const WOOD_TRACK = [
  [1.95, 0.48, -0.06], [1.46, 0.14, 0.39], [0.74, 0.13, 0.55],
].map((p) => woodPoint(...p));
const ROCK = ROCKS[5];

const SITES = [
  {
    support: 'sand', delay: 0,
    home: { x: -0.45, z: -0.45 },
    probe: { x: -0.20, z: -0.62 },
    shelter: { x: -0.62, z: -0.29 },
    hue: 0xb82d37, yaw: 0.65,
  },
  {
    support: 'rock', delay: 9,
    home: { x: ROCK.x - 0.015, z: ROCK.z + 0.01 },
    probe: { x: ROCK.x + ROCK.rx * 0.20, z: ROCK.z - ROCK.rz * 0.12 },
    shelter: { x: ROCK.x - ROCK.rx * 0.12, z: ROCK.z - ROCK.rz * 0.08 },
    hue: 0xd96742, yaw: 1.2,
  },
  {
    support: 'wood', delay: 19,
    home: { x: 2.38, z: 0.086 },
    probe: { x: 2.20, z: 0.20 },
    shelter: { x: 2.50, z: -0.02 },
    hue: 0x934b42, yaw: -2.30,
  },
];

function woodTop(x, z) {
  let best = { distance: Infinity, y: groundHeight(x, z) };
  for (let i = 0; i < WOOD_TRACK.length - 1; i++) {
    const a = WOOD_TRACK[i], b = WOOD_TRACK[i + 1];
    const dx = b.x - a.x, dz = b.z - a.z;
    const u = THREE.MathUtils.clamp(((x - a.x) * dx + (z - a.z) * dz) / (dx * dx + dz * dz), 0, 1);
    const px = a.x + dx * u, pz = a.z + dz * u;
    const distance = Math.hypot(x - px, z - pz);
    if (distance < best.distance) {
      const centreY = THREE.MathUtils.lerp(a.y, b.y, u);
      const ground = groundHeight(x, z);
      const cross = Math.sqrt(Math.max(0, 1 - (distance / WOOD_RADIUS) ** 2));
      const edge = THREE.MathUtils.clamp((WOOD_RADIUS * 1.4 - distance) / (WOOD_RADIUS * 0.55), 0, 1);
      const blend = edge * edge * (3 - 2 * edge);
      const top = centreY + WOOD_RADIUS * cross;
      best = { distance, y: THREE.MathUtils.lerp(ground, top, blend) };
    }
  }
  return best.y;
}

export function shrimpSupportHeight(index, x, z) {
  const support = SITES[index].support;
  if (support === 'sand') return groundHeight(x, z);
  if (support === 'wood') return woodTop(x, z);
  const dx = (x - ROCK.x) / (ROCK.rx * 0.94);
  const dz = (z - ROCK.z) / (ROCK.rz * 0.94);
  return Math.max(groundHeight(x, z), rockCenterY(ROCK) + ROCK.ry * Math.sqrt(Math.max(0, 1 - dx * dx - dz * dz)));
}

const mixPoint = (a, b, t) => ({ x: THREE.MathUtils.lerp(a.x, b.x, t), z: THREE.MathUtils.lerp(a.z, b.z, t) });
const ease = (t) => { const x = THREE.MathUtils.clamp(t, 0, 1); return x * x * (3 - 2 * x); };

// A ground-bound stop-and-go forager: it walks to a patch, feeds with its front legs,
// backs under cover, then rests. The three offsets keep the animals from acting in unison.
export function shrimpPose(index, time) {
  const site = SITES[index];
  const phase = ((time + site.delay) % 30 + 30) % 30;
  let behaviour = 'rest', walk = 0, foraging = 0, target = site.home;
  if (phase < 5) {
    behaviour = 'walk'; walk = 0.7 + 0.3 * Math.sin(phase * 2.1);
    target = mixPoint(site.home, site.probe, ease(phase / 5));
  } else if (phase < 12) {
    behaviour = 'forage'; foraging = 0.75 + 0.25 * Math.sin((phase - 5) * 1.7);
    target = site.probe;
  } else if (phase < 16) {
    behaviour = 'walk'; walk = 0.65;
    target = mixPoint(site.probe, site.home, ease((phase - 12) / 4));
  } else if (phase < 21) {
    behaviour = 'hide'; target = mixPoint(site.home, site.shelter, ease((phase - 16) / 2));
  } else target = site.home;

  const tremor = behaviour === 'forage' ? 0.012 : behaviour === 'rest' ? 0.004 : 0;
  const x = target.x + tremor * Math.sin(time * 2.3 + index * 1.7);
  const z = target.z + tremor * Math.cos(time * 1.9 + index * 2.1);
  const pose = shrimpSupportHeight(index, x, z) + BODY_CLEARANCE;
  const dx = target.x - site.home.x, dz = target.z - site.home.z;
  const yaw = Math.hypot(dx, dz) > 0.012 ? Math.atan2(-dz, dx) : site.yaw;
  return { x, y: pose, z, yaw, walk, foraging, behaviour, support: site.support };
}

const sphere = new THREE.SphereGeometry(1, 12, 10);
const legGeometry = new THREE.CylinderGeometry(1, 0.82, 1, 5, 1);
const yAxis = new THREE.Vector3(0, 1, 0);
const scratch = new THREE.Vector3();

function makeShrimp(scene, index) {
  const site = SITES[index];
  const root = new THREE.Group();
  root.name = `Freshwater shrimp ${index + 1} (${site.support})`;
  root.scale.setScalar(SHRIMP_SCALE);
  const body = new THREE.Group();
  body.name = `Shrimp body ${index + 1}`;
  root.add(body);

  const shellColor = new THREE.Color(site.hue);
  const shell = new THREE.MeshPhysicalMaterial({
    color: shellColor, roughness: 0.30, metalness: 0.015,
    clearcoat: 0.48, clearcoatRoughness: 0.22,
  });
  const segment = (name, position, scale, tint = 1) => {
    const material = tint === 1 ? shell : shell.clone();
    if (tint !== 1) material.color.multiplyScalar(tint);
    const mesh = new THREE.Mesh(sphere, material);
    mesh.name = name;
    mesh.position.set(...position); mesh.scale.set(...scale);
    mesh.castShadow = true; mesh.receiveShadow = true;
    body.add(mesh);
    return mesh;
  };
  // Curved carapace and overlapping abdominal plates, with the tail fan kept short.
  segment('Shrimp carapace', [0.045, 0.121, 0], [0.096, 0.065, 0.066]);
  const abdomen = [
    [-0.036, 0.111, 0, 0.047, 0.051, 0.054],
    [-0.087, 0.097, 0, 0.043, 0.047, 0.049],
    [-0.133, 0.082, 0, 0.038, 0.041, 0.043],
    [-0.172, 0.067, 0, 0.032, 0.034, 0.037],
    [-0.205, 0.053, 0, 0.026, 0.027, 0.030],
  ];
  abdomen.forEach(([x, y, z, sx, sy, sz], i) => {
    const plate = segment(`Shrimp abdominal plate ${i + 1}`, [x, y, z], [sx, sy, sz], 0.94 + i * 0.018);
    plate.rotation.z = -0.16;
  });
  segment('Shrimp rostrum', [0.132, 0.14, 0], [0.045, 0.014, 0.017], 1.08).rotation.z = 0.18;
  segment('Shrimp tail fan', [-0.237, 0.044, 0], [0.027, 0.026, 0.046], 0.84);

  const eyeMaterial = new THREE.MeshPhysicalMaterial({ color: 0x151a17, roughness: 0.18, clearcoat: 0.5 });
  for (const side of [-1, 1]) {
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.010, 10, 8), eyeMaterial);
    eye.name = 'Shrimp eye'; eye.position.set(0.103, 0.151, side * 0.047); body.add(eye);
  }

  const appendageMaterial = new THREE.MeshStandardMaterial({ color: 0xe1b7a1, roughness: 0.42, transparent: true, opacity: 0.84 });
  const antennae = new THREE.Group(); antennae.name = 'Shrimp antennae'; body.add(antennae);
  for (const side of [-1, 1]) {
    const points = [
      new THREE.Vector3(0.112, 0.145, side * 0.028),
      new THREE.Vector3(0.165, 0.207, side * 0.045),
      new THREE.Vector3(0.236, 0.231, side * 0.074),
      new THREE.Vector3(0.315, 0.216, side * 0.10),
    ];
    const curve = new THREE.CatmullRomCurve3(points);
    const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, 10, 0.0022, 4, false), appendageMaterial);
    mesh.name = 'Fine shrimp antenna'; antennae.add(mesh);
    const second = points.map((p, i) => p.clone().add(new THREE.Vector3(0.015 * i, -0.018 * i, side * 0.012)));
    antennae.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(second), 8, 0.0014, 4, false), appendageMaterial));
  }

  const legs = [], contacts = [];
  for (let pair = 0; pair < 5; pair++) for (const side of [-1, 1]) {
    const hipX = 0.075 - pair * 0.046;
    const hip = new THREE.Vector3(hipX, 0.079 - pair * 0.003, side * (0.036 - pair * 0.002));
    const upper = new THREE.Mesh(legGeometry, appendageMaterial);
    const lower = new THREE.Mesh(legGeometry, appendageMaterial);
    upper.name = `Shrimp walking leg ${pair + 1}`; lower.name = `Shrimp walking foot ${pair + 1}`;
    for (const leg of [upper, lower]) { leg.castShadow = true; leg.receiveShadow = true; body.add(leg); }
    legs.push({ pair, side, hip, upper, lower });
    contacts.push(new THREE.Vector3());
  }

  // Four restrained swimmeret pairs are tucked under the abdomen, not fins borrowed from
  // the fish. Their alternating paddling is almost still while the shrimp rests.
  const swimmerets = [];
  for (let i = 0; i < 4; i++) for (const side of [-1, 1]) {
    const paddle = segment(`Shrimp swimmeret ${i + 1}`, [-0.055 - i * 0.034, 0.036 - i * 0.004, side * 0.023], [0.018, 0.008, 0.012], 1.12);
    swimmerets.push({ mesh: paddle, index: i, side });
  }
  scene.add(root);
  return { index, root, body, antennae, legs, contacts, swimmerets };
}

function placeBetween(mesh, a, b, radius) {
  scratch.subVectors(b, a);
  const length = scratch.length();
  mesh.position.copy(a).add(b).multiplyScalar(0.5);
  mesh.quaternion.setFromUnitVectors(yAxis, scratch.multiplyScalar(1 / Math.max(length, 1e-6)));
  mesh.scale.set(radius, length, radius);
  mesh.updateMatrix();
}

export function createShrimpGroup(scene) {
  const models = Array.from({ length: SHRIMP_COUNT }, (_, i) => makeShrimp(scene, i));
  const update = (time, dt = 1 / 30) => {
    for (const model of models) {
      const pose = shrimpPose(model.index, time);
      model.root.position.set(pose.x, pose.y, pose.z);
      model.root.rotation.y = pose.yaw;
      model.root.updateMatrix();
      const walk = pose.walk;
      const groundPitch = model.index === 2 ? 0.16 : 1;
      model.body.rotation.z = (-0.045 * pose.foraging + 0.009 * Math.sin(time * 1.3 + model.index)) * groundPitch;
      model.antennae.rotation.z = 0.025 * Math.sin(time * 2.1 + model.index * 1.8) + 0.022 * pose.foraging;
      model.antennae.rotation.x = 0.07 * Math.sin(time * 1.7 + model.index * 2.4);
      model.body.updateMatrix();
      model.antennae.updateMatrix();
      model.legs.forEach((leg, i) => {
        const cycle = time * (7.2 + 0.6 * model.index) + leg.pair * Math.PI + (leg.side > 0 ? Math.PI : 0);
        const stride = walk * Math.sin(cycle) * 0.016;
        const lift = walk * Math.max(0, Math.cos(cycle)) * 0.014 + pose.foraging * Math.max(0, Math.sin(time * 4 + i)) * 0.004;
        const localX = leg.hip.x - 0.012 + stride;
        const lateralReach = model.index === 2 ? 0.045 : 0.092;
        const localZ = leg.side * (lateralReach - leg.pair * 0.004);
        const c = Math.cos(pose.yaw), s = Math.sin(pose.yaw);
        const scaledX = localX * SHRIMP_SCALE, scaledZ = localZ * SHRIMP_SCALE;
        const worldX = pose.x + scaledX * c + scaledZ * s;
        const worldZ = pose.z - scaledX * s + scaledZ * c;
        const worldY = shrimpSupportHeight(model.index, worldX, worldZ) + lift;
        const toe = model.contacts[i];
        toe.set(localX, (worldY - pose.y) / SHRIMP_SCALE, localZ);
        const knee = new THREE.Vector3(leg.hip.x + 0.016 + stride * 0.42, 0.043 + lift * 0.65, leg.side * 0.076);
        placeBetween(leg.upper, leg.hip, knee, 0.0035);
        placeBetween(leg.lower, knee, toe, 0.0026);
      });
      for (const item of model.swimmerets) {
        const beat = Math.sin(time * 3.8 + item.index * 0.9 + item.side * 0.8);
        item.mesh.rotation.x = item.side * (0.28 + pose.foraging * 0.24 + walk * 0.06 * beat);
        item.mesh.rotation.z = 0.1 * beat;
        item.mesh.updateMatrix();
      }
    }
  };
  update(0, 0);
  return { models, update };
}
