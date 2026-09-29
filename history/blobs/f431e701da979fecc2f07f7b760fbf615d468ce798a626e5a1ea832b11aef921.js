import * as THREE from 'three';
import { SURFACE_Y, waterTime } from './water.js';

export function backboardGradient(localY) {
  return THREE.MathUtils.smoothstep(localY, -5, 4);
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
  // A small internal corner filter: grille → pump housing → riser → submerged outlet.
  // Its rear standoffs end at the back pane rather than floating in open water.
  const x = 8.15, z = -6.72, returnTop = SURFACE_Y - 0.19;
  const graphite = new THREE.MeshStandardMaterial({color:0x354442,roughness:0.72});
  const housing = new THREE.Mesh(new THREE.BoxGeometry(0.43,1.05,0.30),graphite);
  housing.name='Submerged filter pump and strainer';housing.position.set(x,1.05,z);
  housing.castShadow=housing.receiveShadow=true;group.add(housing);
  const slots = new THREE.InstancedMesh(new THREE.BoxGeometry(0.30,0.017,0.007),
    new THREE.MeshStandardMaterial({color:0x101a19,roughness:1}),7);
  slots.name='Filter intake slots';const transform=new THREE.Object3D();
  for(let i=0;i<7;i++){transform.position.set(x,0.76+i*0.08,z+0.154);transform.updateMatrix();slots.setMatrixAt(i,transform.matrix);}
  group.add(slots);
  addCylinder(group,'Aquarium filter return',0.058,returnTop-1.48,0x61716b,
    new THREE.Vector3(x,(returnTop+1.48)/2,z));
  const elbow=new THREE.Mesh(new THREE.SphereGeometry(0.063,12,8),graphite);
  elbow.name='Filter return elbow';elbow.position.set(x,returnTop,z);group.add(elbow);
  addCylinder(group,'Filter outflow lip',0.062,0.43,0x475853,
    new THREE.Vector3(x-0.205,returnTop-0.017,z),new THREE.Vector3(-1,-0.08,0));
  for(const y of [2.0,6.2,8.6]) {
    addCylinder(group,'Filter mount to rear glass',0.025,0.42,0x34423e,
      new THREE.Vector3(x,y,-6.94),new THREE.Vector3(0,0,1));
    const cup=new THREE.Mesh(new THREE.CylinderGeometry(0.085,0.085,0.036,12),graphite);
    cup.name='Filter suction cup on rear pane';cup.rotation.x=Math.PI/2;cup.position.set(x,y,-7.155);group.add(cup);
  }
  const heaterMat=new THREE.MeshPhysicalMaterial({color:0x71837b,roughness:0.25,transparent:true,opacity:0.40});
  const heater=new THREE.Mesh(new THREE.CylinderGeometry(0.049,0.049,2.55,12),heaterMat);
  heater.name='Submerged aquarium heater';heater.position.set(-8.0,3.0,-6.92);group.add(heater);
  for(const y of [2.1,3.9]) {
    addCylinder(group,'Heater mount to rear glass',0.042,0.22,0x34423e,new THREE.Vector3(-8,y,-7.05),new THREE.Vector3(0,0,1));
  }
  return {x,y:returnTop,z};
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
  // Vertex waves and analytic surface normals avoid uploading/recomputing geometry
  // twice per frame on the CPU. The physical surface remains on the same shared clock.
  surfaceMaterial.onBeforeCompile=shader=>{
    shader.uniforms.waterTime=waterTime;
    shader.vertexShader=`uniform float waterTime;
      float surfaceHeight(vec2 q){
        float x=q.x,z=-1.7-q.y;
        float nearReturn=exp(-((x-${(outlet.x-0.55).toFixed(5)})*(x-${(outlet.x-0.55).toFixed(5)})/1.2+(z-${outlet.z.toFixed(5)})*(z-${outlet.z.toFixed(5)})/0.9));
        return .008*sin(x*.43+waterTime*.48+z*.16)+nearReturn*.018*sin(x*2.2-waterTime*1.1+z*1.4);
      }
    `+shader.vertexShader;
    shader.vertexShader=shader.vertexShader.replace('#include <beginnormal_vertex>',`
      float dx=(surfaceHeight(position.xy+vec2(.002,0))-surfaceHeight(position.xy-vec2(.002,0)))/.004;
      float dy=(surfaceHeight(position.xy+vec2(0,.002))-surfaceHeight(position.xy-vec2(0,.002)))/.004;
      vec3 objectNormal=normalize(vec3(-dx,-dy,1.0));
    `).replace('#include <begin_vertex>',`vec3 transformed=position;transformed.z+=surfaceHeight(position.xy);`);
  };
  surfaceMaterial.customProgramCacheKey=()=>"guppy-surface-v7";

  const rippleMaterial = new THREE.MeshBasicMaterial({
    color: 0xd9e8df, transparent: true, opacity: 0.09,
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
    new THREE.Vector3(outlet.x - 0.38, outlet.y - 0.017, outlet.z),
    new THREE.Vector3(outlet.x - 0.70, outlet.y + 0.025, outlet.z + 0.06),
    new THREE.Vector3(outlet.x - 1.08, outlet.y + 0.050, outlet.z + 0.08),
  ], 0.008, jetMaterial);
  jet.material.depthWrite = false;

  const update = (time) => {
    waterTime.value = time;
    for (const { ring, phase } of ripples) {
      const travel = ((time * 0.11 + phase) % 1 + 1) % 1;
      const radius = 0.075 + travel * 0.34;
      ring.scale.set(radius, radius, radius);
      ring.updateMatrix();
      ring.material.opacity = 0.075 * (1 - travel);
      ring.visible = ring.material.opacity > 0.012;
    }
  };
  update(0);
  return { update, surface, ripples };
}
