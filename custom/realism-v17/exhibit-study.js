import * as THREE from 'three';
import {createExhibitWater} from './exhibit-water.js';
import {createEnvironment} from '/preview/anatomy-study-v15-r1/scenes/riverscape/src/environment.js';
import {createPlants} from '/preview/anatomy-study-v15-r1/scenes/riverscape/src/plants.js';
import {loadLeafMaterial} from '/preview/anatomy-study-v15-r1/scenes/riverscape/src/leaf-material.js';
import {waterTime,currentVelocity} from '/preview/anatomy-study-v15-r1/scenes/riverscape/src/water.js';
import {createFishSchool} from '/preview/anatomy-study-v15-r1/scenes/riverscape/src/fish.js';
import {loadPhotoPigment} from '/preview/anatomy-study-v15-r1/scenes/riverscape/src/photo-material.js';
const canvas=document.querySelector('canvas'),status=document.querySelector('output'),clock={value:0};
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(1);renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.06;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
const scene=new THREE.Scene();scene.background=new THREE.Color('#91cce9');scene.fog=new THREE.FogExp2('#a6d7ed',.016);
const camera=new THREE.PerspectiveCamera(28,16/9,.1,60);camera.position.set(0,2.7,10.0);camera.lookAt(0,2.05,0);
scene.add(new THREE.HemisphereLight(0xf1faff,0xaaa283,.65));
const key=new THREE.DirectionalLight(0xfffaf0,2.5);key.position.set(-3,11,2.5);key.target.position.set(0,0,0);key.castShadow=true;key.shadow.mapSize.set(2048,2048);Object.assign(key.shadow.camera,{left:-7,right:7,top:7,bottom:-7,near:1,far:22});key.shadow.bias=-.0001;key.shadow.normalBias=.008;scene.add(key,key.target);
const fill=new THREE.DirectionalLight(0xe5f4ff,.7);fill.position.set(1,3,7);scene.add(fill);const back=new THREE.DirectionalLight(0xe5f4ff,.6);back.position.set(-1,5,-5);scene.add(back);
const env=new THREE.Scene();env.background=new THREE.Color('#798c94');for(const [x,y,z,w,h,power]of [[-2,6,0,8,1.5,5],[2,3,5,5,5,.8]]){const p=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({color:new THREE.Color(power,power,power),side:THREE.DoubleSide}));p.position.set(x,y,z);if(y===6)p.rotation.x=Math.PI/2;env.add(p);}const pm=new THREE.PMREMGenerator(renderer);scene.environment=pm.fromScene(env,.03,.1,30).texture;scene.environmentIntensity=.80;pm.dispose();
const water=createExhibitWater(renderer,scene,camera);
const habitat=new THREE.Group();habitat.scale.setScalar(.46);habitat.position.z=.40;scene.add(habitat);
await loadLeafMaterial();const environment=await createEnvironment(habitat);const plants=createPlants(habitat,{backgroundDensity:.65,backgroundRows:20,backgroundCols:3,animatedShadows:true});
habitat.traverse(o=>{if(o.material){for(const m of Array.isArray(o.material)?o.material:[o.material])water.receive(m);}});
const board=new THREE.Mesh(new THREE.PlaneGeometry(10,4),new THREE.MeshBasicMaterial({color:'#91cce9',toneMapped:false}));board.position.set(0,2,-2.48);board.receiveShadow=true;water.receive(board.material);scene.add(board);
await loadPhotoPigment();const school=createFishSchool(scene);const body=scene.getObjectByName('Silver-blue freshwater fish'),fins=scene.getObjectByName('Attached translucent fish fins');body.count=fins.count=1;for(const m of [body.material,fins.material])water.receive(m);
body.geometry.attributes.aGuppyVariant.setX(0,1);body.geometry.attributes.aGuppyVariant.needsUpdate=true;body.geometry.attributes.aGuppySeed.setX(0,.54);body.geometry.attributes.aGuppySeed.needsUpdate=true;
// Subtle glass edge and meniscus, no fullscreen distortion of the front pane.
const glassmat=new THREE.MeshPhysicalMaterial({color:'#c3e1df',transparent:true,opacity:.10,roughness:.06,metalness:.05,side:THREE.DoubleSide,depthWrite:false});
for(const x of [-5,5]){const pane=new THREE.Mesh(new THREE.PlaneGeometry(5,4.15),glassmat);pane.rotation.y=Math.PI/2;pane.position.set(x,2.05,0);scene.add(pane);}
const bubbleG=new THREE.SphereGeometry(1,9,6),bubbleM=new THREE.MeshPhysicalMaterial({color:'#d9f4ff',roughness:.10,metalness:.15,transparent:true,opacity:.24,depthWrite:false});const bubbles=new THREE.InstancedMesh(bubbleG,bubbleM,23);scene.add(bubbles);const temp=new THREE.Object3D();
let paused=false,angled=false,waterOn=true,recording=false,time=0,last=0,frames=0;const pos=new THREE.Vector3(-1.5,2.1,.2),prev=pos.clone(),pose=new THREE.Object3D();
function draw(dt){time+=dt;clock.value=time;waterTime.value=time;
 const cycle=time%11,active=cycle<3.3||cycle>8.9,effort=active?.45:.11;
 // Several strokes, a drifting hold, then a slow change of heading. Preview-only path.
 const phase=time*.28,pace=time*.20+.16*Math.sin(time*.65);prev.copy(pos);pos.set(2.25*Math.sin(pace),2.00+.32*Math.sin(time*.38),.4+1.40*Math.cos(pace));
 const heading=Math.atan2(-(pos.z-prev.z),(pos.x-prev.x));if(dt>0)pose.rotation.y=THREE.MathUtils.lerp(pose.rotation.y,heading,.07);
 pose.position.copy(pos);pose.rotation.z=.05*Math.sin(time*.8);pose.scale.setScalar(.60);pose.updateMatrix();for(const mesh of [body,fins]){mesh.setMatrixAt(0,pose.matrix);mesh.instanceMatrix.needsUpdate=true;}
 body.geometry.attributes.aSwim.setXYZW(0,time*12,effort,.3*Math.sin(time*.55),active?.15:.7);body.geometry.attributes.aSwim.needsUpdate=true;body.geometry.attributes.aFinPhase.setX(0,time*15);body.geometry.attributes.aFinPhase.needsUpdate=true;
 for(let i=0;i<23;i++){const age=(time*(.36+i%3*.05)+i*.174)%3.95,flow=currentVelocity(new THREE.Vector3(-9.67,3,-3.48),time,new THREE.Vector3()).multiplyScalar(.46);temp.position.set(-4.45+.05*Math.sin(i*4+time)+flow.x*age*3,.09+age,-1.6+.025*Math.sin(time+i));temp.scale.setScalar(.018+(i%4)*.004);temp.updateMatrix();bubbles.setMatrixAt(i,temp.matrix);}bubbles.instanceMatrix.needsUpdate=true;
 water.update(time);water.render();frames++;status.textContent=JSON.stringify({prototype:true,fish:1,frames,time:+time.toFixed(2),paused,...water.stats(),plants:plants.stats});status.dataset.frames=frames;status.dataset.time=time;
}
function resize(){const b=canvas.getBoundingClientRect();renderer.setSize(Math.round(b.width),Math.round(b.height),false);camera.aspect=b.width/b.height;camera.updateProjectionMatrix();water.resize(Math.round(b.width),Math.round(b.height));draw(0);}window.addEventListener('resize',resize);
document.querySelector('#pause').onclick=e=>{paused=!paused;e.target.textContent=paused?'再開':'一時停止';status.dataset.paused=paused;};
document.querySelector('#view').onclick=e=>{angled=!angled;camera.position.set(angled?3.4:0,angled?4.7:2.7,angled?11.5:10.0);camera.lookAt(0,2.05,0);e.target.textContent=angled?'正面から見る':'斜めから見る';draw(0);};document.querySelector('#water').onclick=e=>{waterOn=!waterOn;water.setEnabled(waterOn);e.target.textContent=waterOn?'水面なしと比較':'水面を戻す';draw(0);};
const stamp=()=>new Date().toISOString().replace(/[-:]/g,'').replace(/\.\d+Z/,'Z');async function save(blob,name){const r=await fetch('/capture/'+name,{method:'POST',body:blob});if(!r.ok)throw Error('保存失敗');return name;}
document.querySelector('#save').onclick=async()=>{await save(await new Promise(r=>canvas.toBlob(r)),`natural-v15-tank-${angled?'oblique':'front'}-${stamp()}.png`);};
document.querySelector('#record').onclick=()=>{if(recording)return;recording=true;const chunks=[],rec=new MediaRecorder(canvas.captureStream(30),{mimeType:'video/webm;codecs=vp9',videoBitsPerSecond:7500000});rec.ondataavailable=e=>chunks.push(e.data);rec.onstop=async()=>{await save(new Blob(chunks,{type:'video/webm'}),`natural-v15-tank-motion-${stamp()}.webm`);recording=false;};rec.start();setTimeout(()=>rec.stop(),65000);};
resize();function loop(now){requestAnimationFrame(loop);if(now-last<33)return;const dt=last?Math.min(.06,(now-last)/1000):0;last=now;if(!paused)draw(dt);}requestAnimationFrame(loop);
