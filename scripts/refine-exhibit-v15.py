from pathlib import Path
import shutil
r=Path(__file__).resolve().parents[1];f=r/'preview/exhibit-guppy-v15-r2/scenes/riverscape/src';c=r/'custom/realism-v15'
p=f/'main.js';s=p.read_text().replace("color: '#91cce9'","color: '#45a9e9'")
s=s.replace('level:9.8','level:9.3,lightDirection:key.position.clone().sub(key.target.position).normalize()')
s=s.replace('  const aquarium = createAquariumDetails(scene);','''  const aquarium = createAquariumDetails(scene);
  aquarium.surface.visible=false;
  for(const {ring}of aquarium.ripples)ring.visible=false;
  const airStone=new THREE.Mesh(new THREE.CylinderGeometry(.17,.20,.12,14),new THREE.MeshStandardMaterial({color:0x777d73,roughness:1}));
  airStone.name='Rooted aeration stone';airStone.position.set(6.35,.32,-.15);airStone.receiveShadow=true;scene.add(airStone);
  const airTubePath=new THREE.CatmullRomCurve3([new THREE.Vector3(6.35,.30,-.15),new THREE.Vector3(7.0,.22,-1.3),new THREE.Vector3(9.45,.35,-6.80),new THREE.Vector3(9.45,9.5,-6.80)]);
  const airTube=new THREE.Mesh(new THREE.TubeGeometry(airTubePath,36,.018,6,false),new THREE.MeshPhysicalMaterial({color:0x94b9bc,transparent:true,opacity:.32,roughness:.18,depthWrite:false}));
  airTube.name='Clear aeration hose';scene.add(airTube);''')
s=s.replace('    aquarium.update(time);','    aquarium.update(time);\n    for(const {ring}of aquarium.ripples)ring.visible=false;')
p.write_text(s)
p=f/'water.js';s=p.read_text().replace('SURFACE_Y = 9.8','SURFACE_Y = 9.3');p.write_text(s)
p=f/'living-water.js';s=p.read_text().replace('const y=1.24+progress*8.3;','const y=.38+progress*8.87;');p.write_text(s)
p=c/'exhibit-water.js';s=p.read_text().replace('{width=10,depth=5,level=4}={}','{width=10,depth=5,level=4,lightDirection=new THREE.Vector3(-.26,.94,.22).normalize()}={}')
s=s.replace('level*.93','level').replace('new THREE.Vector3(-.26,.94,.22).normalize()}}','lightDirection}}')
s=s.replace('const screenU={...u,','const screenU={...u,waterLightDirection:{value:lightDirection},').replace('uniform mat4 viewProj;varying vec3 vWorld;','uniform mat4 viewProj;uniform vec3 waterLightDirection;varying vec3 vWorld;').replace('normalize(vec3(-.26,.94,.22))','waterLightDirection')
p.write_text(s);shutil.copy2(p,f/p.name)
for name in ['main.js','water.js','living-water.js']:shutil.copy2(f/name,c/name)
# Canonical production overlay is separate from test-only exhibit-study/plants modules.
(r/'scripts/prepare-exhibit-v15.py').write_text('''"""Create a full-scene candidate; no native install."""
from pathlib import Path
import sys,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1]
name=sys.argv[1]
subprocess.run(['python3',str(ROOT/'scripts/prepare-preview.py'),name],check=True)
f=ROOT/'preview'/name/'scenes/riverscape/src'
for name in ['fish-anatomy-base.js','fish-anatomy.js','photo-material.js','guppy-palette.js','guppy-swimming.js','environment.js','main.js','water.js','living-water.js','exhibit-water.js']:
 shutil.copy2(ROOT/'custom/realism-v15'/name,f/name)
shutil.copy2(ROOT/'custom/realism-v15/CAUSTIC-LICENSE.txt',f.parent/'assets/CAUSTIC-LICENSE.txt')
print('Full 3D candidate only:',f)
''')
