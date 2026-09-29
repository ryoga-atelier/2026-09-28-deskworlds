from pathlib import Path
import hashlib,json,subprocess
r=Path(__file__).resolve().parents[1];p=r/'preview/oval-profile-guppy-v25-r2';app=Path('/Users/ryoga-atelier/Applications/Deskworlds.app/Contents/Resources/scene')
files=[x for d in ['src','assets'] for x in (p/'scenes/riverscape'/d).rglob('*') if x.is_file()]+[p/'scenes/riverscape/wallpaper.html',p/'vendor/three.module.js',p/'vendor/three.core.js']
files=[x for x in files if x.exists()]
mismatch=[str(x.relative_to(p)) for x in files if x.read_bytes()!=(app/x.relative_to(p)).read_bytes()]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=sha('/Users/ryoga-atelier/Library/Application Support/com.apple.wallpaper/Store/Index.plist');b=sha('/Users/ryoga-atelier/Library/Preferences/com.apple.universalaccess.plist');old=json.loads((r/'evidence/v21-integrity.json').read_text())
d={'variant':'guppy-v25','runtime_files_compared':len(files),'runtime_mismatches':mismatch,'wallpaper_sha256':a,'accessibility_sha256':b,'system_settings_unchanged':a==old['wallpaper_sha256'] and b==old['accessibility_sha256'],'upstream_commit':subprocess.check_output(['git','-C',str(r/'upstream/deskworlds'),'rev-parse','HEAD'],text=True).strip(),'upstream_status':subprocess.check_output(['git','-C',str(r/'upstream/deskworlds'),'status','--porcelain'],text=True).strip()}
assert not mismatch and d['system_settings_unchanged'] and not d['upstream_status'];(r/'evidence/v25-integrity.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
