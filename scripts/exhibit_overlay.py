"""Local v15 candidate overlay; run after apply_guppy, never against upstream."""
from pathlib import Path
import shutil,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
FILES=['fish-anatomy-base.js','fish-anatomy.js','photo-material.js','guppy-palette.js','guppy-swimming.js','environment.js','main.js','water.js','living-water.js','exhibit-water.js']
def apply_exhibit(scene_root, version="v15"):
 source=ROOT/"custom"/("realism-"+version)
 target=Path(scene_root).resolve();up=(ROOT/'upstream').resolve()
 if target==up or up in target.parents:raise ValueError('Upstream is immutable')
 folder=target/'scenes/riverscape/src'
 files=FILES+(['photo-habitat.js','water-optics.js'] if version in ('v18','v19','v20','v21','v22','v23','v24','v25','v26','v27','v28','v29') else [])
 for name in files:shutil.copy2(source/name,folder/name)
 shutil.copy2(source/'CAUSTIC-LICENSE.txt',folder.parent/'assets/CAUSTIC-LICENSE.txt')
 metadata=json.loads((target/'guppy-customization.json').read_text())
 metadata.update(revision={'v15':'exhibit-guppy-v15-r3','v16':'veiled-guppy-v16','v17':'mixed-guppy-v17','v18':'layered-guppy-v18','v19':'moderate-guppy-v19-candidate','v20':'photo-reference-guppy-v20-candidate','v21':'mixed-reference-guppy-v21-candidate','v22':'layered-reference-guppy-v22','v23':'warm-scale-guppy-v23','v24':'rounded-gradient-guppy-v24','v25':'oval-profile-guppy-v25','v26':'slender-pearl-guppy-v26','v27':'pearl-scale-guppy-v27','v28':'bronze-scale-guppy-v28','v29':'bronze-gradient-guppy-v29-r16'}[version],status='candidate, not visually accepted on native Mac yet',
  source_hashes={name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in files},
  water_reference={'url':'https://github.com/ScottieFox/caustic-volume','commit':'d87351bff19831aa9d11c0679605fad6797b133f','license':'MIT'},
  scope='Reference-led guppy profile; silver skin and localized pigment; rooted 3D plants; shared water height and slopes for surface view/refraction and four caustic receiver levels; shared current for fish, leaves, bubbles and sand. Screen-space optical approximation, not full ray tracing.')
 if version=='v16':
  metadata.update(scope='User-selected v14 planted photographic-depth habitat; reference-led silver/pigmented guppies with enlarged tail and dorsal veils, readable paired fins and phase-lagged membrane motion.',water_reference_status='CAUSTIC prototype preserved in v15; inactive in v16 photographic habitat',population='24 in 8 colour families; deep and pastel colours coexist')
 if version in ('v17','v18'):
  metadata.update(scope='User-selected planted habitat; pet-shop mixed guppy reference: fuller posterior body, modest rounded caudal and dorsal fins, pale silver/tan body with localized colour and varied membrane markings.',water_reference_status='CAUSTIC prototype preserved in v15; inactive in photographic habitat',population='24 in 8 colour families; blue, yellow, purple and warm colours',selected_reference='https://www.petballoon.net/product/65143')
 if version in ('v18','v19','v20','v21','v22','v23','v24','v25','v26','v27','v28'):
  metadata.update(scope='Explicit user refinement: rounded pale belly, tapered peduncle, large matching flowing fins, localized vivid posterior pigment and separate scale/fin microstructure. Selected planted plate retained with a wider central corridor; shared spectral water, projected caustics, reflection and soft shafts.',water_reference_status='MIT spectral-wave idea adapted; fixed-camera depth approximation, not full ray tracing')
 if version=='v19':
  metadata.update(scope='User-selected moderated form: v17 body and peduncle, subtly fuller belly, rounded tail with 1.4004x v17 mesh area, short soft pelvic membranes and slightly longer dorsal. V18 layered pigment and shared-water optics retained.',status='selected by user for Mac installation and native verification')
 if version=='v20':
  metadata.update(scope='Latest user-attached reference: silver/bronze/rose skin, restricted local body pigment, rounded abdomen extending backward, rounded translucent blue-family caudal fins. V19 water and planting unchanged.',status='uninstalled photo-reference comparison candidate')
 if version=='v21':
  metadata.update(scope='User-requested blend: v20 rounded abdomen and softer fan outline, localized return of v19 colour, silver-bronze/rose substrate and fuller snout profile. V19 water, habitat, motion and 24-fish palette retained.',status='user-requested v19/v20 blend, selected for installation and native verification; no claim of final visual acceptance')
 if version=='v22':
  metadata.update(scope='V21 geometry and V19 habitat retained. User photo layers: dark dorsum/eye surround over pale belly; pale dorsal/anal tissue with clear tips; absorbing black caudal root, coloured middle and clear edge.',status='user-requested material-layer refinement; requires rendered and native verification, not final visual acceptance')
 if version=='v23':
  metadata.update(scope='Corrected interpretation of user photo: bronze/rose/lilac ground, thin scale margins rather than a dark dorsal field, compact pearl abdomen, small orbital accent and rounded caudal root. V21 anatomy and V19 water retained.',status='user-requested correction of V22 black-white division, undergoing verification; not final visual acceptance')
 if version=='v24':
  metadata.update(scope='User refinement: pale head to richer tailward skin gradient, broader pearl belly and rounded ventral profile, tapered face, clear distal zones of tail/dorsal/anal fins. V19 water, motion, 24 fish and 8 families retained.',status='user-requested refinement undergoing visual and native verification, not final acceptance')
 if version=='v25':
  metadata.update(scope='User-requested continuous convex back/head outline and elliptical pearl abdominal patch, including its upper edge; V24 head-to-tail pigment gradient and transparent distal fin zones retained.',status='user-requested curved-body refinement undergoing verification, not final acceptance')
 if version=='v26':
  metadata.update(scope='Photo-led slender continuous body profile, flattened elliptical pearl abdomen, silver/grey-lilac head-to-tail gradient rather than a red-brown body, readable fine scale margins. Transparent distal fin zones and V19 habitat retained.',status='user-requested correction of V25 excessive fullness, undergoing verification; not final acceptance')
 if version=='v27':
  metadata.update(scope='Photo-led refinement of V26: coloured-but-translucent fin edges with radial rays and fine cross-veins; a soft mottled grey-brown accent at the pale ventral root; clearer, gently raised overlapping scale margins across the body and into the pale abdomen. Fish scales remain on body tissue; translucent fins show membrane structure. V26 profile, palette, and planted water retained.',status='user-requested visual refinement undergoing comparison; not final acceptance')
 if version=='v28':
  metadata.update(scope='Photo-led colour and microstructure correction of V27: warm bronze dorsal pigment into a rose-silver flank and pale softly irregular abdomen; individually varied overlapping scale arcs in warm pigment, a subtle blue-ray lift in blue-family tails, and brighter readable fin veils. Slim convex body, population, water, and motion retained.',status='user-requested photo comparison candidate undergoing native visual verification; not final acceptance')
 if version=='v29':
  metadata.update(scope='User-requested photographic refinement: the shared curved ivory abdomen now contains a distinct charcoal rear marking; stronger light-head to rich-tail tonal separation, with tail-linked colour on the rear dorsum and upper flank across all eight families; r11 scale edges, inward ivory curve and cheek guanine are retained; the anterior abdomen follows a sickle-shaped rose/sage-silver operculum below the eye. Eyes and matching sockets are 15% smaller, and the small mouth turns upward. The nested silver/ivory belly, head-to-tail gradient, fine scale arcs, finite fin-root derivatives, slim body, palette, fins and planted living water remain.',status='user-requested belly and facial refinement undergoing WebGL and native verification; not final acceptance')
 (target/'guppy-customization.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
 return metadata
