"""Increase gem volume absorption while preserving geometry and the scalar GLB fallback."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import bpy

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--repo',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
a=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
ident=a.out.parent.name
assert ident.startswith('TI') and ident[2:].isdigit(),ident
source=a.repo/'sources/docs/assets/reconstruction/trading-goods-refined'/ident/(ident+'.blend')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior_sha=sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source))
used={m for o in bpy.context.scene.objects if o.type in ['MESH','CURVE','FONT'] for m in o.data.materials}
changes=[]
for m in used:
 if m.get('physical_surface_role')!='gem':continue
 density=.8 if ident=='TI025' or 'diamond' in m.name.lower() else .5 if ident=='TI031' else 2 if ident in ['TI032','TI034'] or 'raw opal' in m.name.lower() else 3
 for node in m.node_tree.nodes:
  if node.type=='VOLUME_ABSORPTION':
   before=node.inputs['Density'].default_value;node.inputs['Density'].default_value=density
   changes.append(dict(material=m.name,prior_density=before,density=density))
assert changes,ident
a.out.mkdir(parents=True,exist_ok=True)
native=a.out/(ident+'.blend')
bpy.context.preferences.filepaths.save_version=0
bpy.context.scene.render.filepath='//renders/'
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
# Absorption remains a native volume shader. The published scalar GLB is identical,
# and is independently reopened/compared to the revised native by verify.py.
glb=a.out/(ident+'.glb');shutil.copyfile(source.with_suffix('.glb'),glb)
record=json.loads((source.parent/'refinement.json').read_text())
record.update(refined_native_sha256=sha(native),glb_sha256=sha(glb),revision_builder='sources/tools/trading-goods/refining/tint_gems.py',revision_builder_sha256=sha(Path(__file__)),prior_refined_native=source.relative_to(a.repo).as_posix(),prior_refined_native_sha256=prior_sha,optical_revision=changes,glb_materials='Unchanged scalar/base-colour fallback; native absorption is not baked or exported as texture maps')
(a.out/'refinement.json').write_text(json.dumps(record,indent=2)+'\n')
assert sha(source)==prior_sha
print('GEM_COLOUR_REFINED',ident,flush=True)
