from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
p=root/'custom/realism-v15'
s=(p/'fish-anatomy.js').read_text().replace('result.skin.envMapIntensity = 0.48','result.skin.envMapIntensity = 0.90').replace('result.skin.iridescence = 0.30','result.skin.iridescence = 0.42').replace('roughnessFactor=clamp(roughnessFactor,0.34,0.48);','roughnessFactor=clamp(roughnessFactor,0.20,0.45);').replace('metalnessFactor=min(metalnessFactor,0.16);','metalnessFactor=min(metalnessFactor*1.30,0.55);')
(p/'fish-anatomy.js').write_text(s)
s=(p/'photo-material.js').read_text().replace('silver*=.78+.36*detail;','silver*=.94+.08*detail;').replace('vec3(.67,.64,.54)','vec3(.57,.63,.62)').replace('vec3(.44,.51,.50)','vec3(.31,.40,.41)').replace('vec3(.18,.25,.23)','vec3(.14,.20,.19)')
s=s.replace('float rear=1.-smoothstep(-.12,.10,fishX+(broken-.5)*.10);','float rear=1.-smoothstep(.04,.23,fishX+(broken-.5)*.055);').replace('float mid=exp(-pow((fishBand-.38)/.26,2.));','float mid=1.-smoothstep(.44,.74,fishBand);').replace('(.5+.5*smoothstep(.38,.64,broken))','(.82+.18*smoothstep(.38,.64,broken))').replace('guppyFinColor()*mix(.28,.82,detail)','guppyFinColor()*mix(.65,1.03,detail)')
s=s.replace('diffuseColor.rgb=mix(diffuseColor.rgb,bodyPigment,sideMask*.97);','''float cheek=exp(-pow((fishX-.20)/.054,2.))*smoothstep(.25,.50,fishBand);
      bodyPigment=mix(bodyPigment,vec3(.40,.50,.50),cheek*.35);
      diffuseColor.rgb=mix(diffuseColor.rgb,bodyPigment,sideMask*.97);''')
s=s.replace('vec3 fin=guppyVariety(plate.rgb,true);','''// One reference red specimen: solid pigment with ray structure; other families
      // retain fine mosaic/grass markings and share the same translucent tissue.
      vec3 fin=guppyVariety(plate.rgb,true);
      if(abs(vGuppyVariant-1.)<.25) fin=guppyFinColor()*(.80+.18*gMottle(vSkinPoint.xy*96.));''')
s=s.replace('mix(.75,.52,smoothstep(.25,1.0,vFishUV.y))+.17*ink','mix(.87,.70,smoothstep(.25,1.0,vFishUV.y))+.08*ink')
(p/'photo-material.js').write_text(s)
shutil.copy2(root/'custom/guppy/guppy-palette.js',p/'guppy-palette.js')
s=(p/'guppy-palette.js').read_text().replace("body:'#d8a597', fin:'#e77c77'","body:'#dca68b', fin:'#ed743d'")
(p/'guppy-palette.js').write_text(s)
# Preserve the canonical reference study; future previews copy these exact files.
(root/'scripts/prepare-v15.py').write_text('''"""Isolated reference study. Canonical local source; never installs or edits upstream."""
from pathlib import Path
import argparse, subprocess, shutil
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('name'); a=p.parse_args()
subprocess.run(['python3',str(ROOT/'scripts/prepare-preview.py'),a.name],check=True)
f=ROOT/'preview'/a.name/'scenes/riverscape/src'
for source in (ROOT/'custom/realism-v15').glob('*.js'): shutil.copy2(source,f/source.name)
print('Isolated v15 prototype:',f)
''')
# Existing r1 is the editable test copy. Production/accepted v14 is untouched.
for source in p.glob('*.js'):shutil.copy2(source,root/'preview/anatomy-study-v15-r1/scenes/riverscape/src'/source.name)
q=root/'review/realism-v15.html';s=q.read_text().replace('const boosted=index>=2;','const boosted=true;').replace('<span>v14 補助光</span>','<span>v14 同じ照明</span>')
s=s.replace('<option value="turn">一周</option>','<option value="turn">一周</option><option value="swim">泳ぎ・静止・旋回</option>')
s=s.replace('p.bodies.geometry.attributes.aSwim.setXYZW(0,0,0,0,0);','const effort=angle===\'swim\'?(Math.sin(t*.65)>.25?.60:.10):0;\n   p.bodies.geometry.attributes.aSwim.setXYZW(0,angle===\'swim\'?t*12:0,effort,angle===\'swim\'?Math.sin(t*.35)*.60:0,angle===\'swim\'&&effort<.2?.8:0);').replace('setX(0,.75)','setX(0,angle===\'swim\'?t*15:.75)').replace("angle==='turn'?t*.65:0","angle==='turn'?t*.65:angle==='swim'?Math.sin(t*.25)*.80:0")
q.write_text(s)
for name in ['INTENT.md','VISUAL-REVIEW.md']:
 with (root/name).open('a') as f:f.write('\n## 展示水槽としての完成条件（追加共有）\n\n水族館の展示水槽をガラス越しに眺める景色。澄んだ青い水を維持し、手前・中央・奥で距離の見え方を変える。展示照明で銀色の肌が角度に応じて光る。根付いた立体葉の間へ魚が出入りする。遊泳・停止・ついばみ・旋回に個体ごとの間がある。水面・ガラスは控えめで、水中像・底・魚・植物に同じ光と流れを用いる。黒い背景・海水槽への変更は不要。単体の精密さだけで完成とせず、水槽全体の距離・光・構図・時間を実写参照と比較する。\n')
