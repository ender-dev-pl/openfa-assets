import bpy,sys,json,struct
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(out/'construction-droids-information.blend'));s=bpy.context.scene
for frame in [1,61,121,511,705]:
 s.frame_set(frame);visible=[ob.name for ob in s.objects if ob.type in ['MESH','CURVE'] and not ob.hide_render];assert len(visible)==6 and all(n.endswith(' technical wire') for n in visible),(frame,visible)
raw=(out/'construction-droids-information.glb').read_bytes();size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);assert not any(n.get('name','').startswith('Welding spark ') or n.get('name')=='Spot welding arc' for n in doc['nodes']);assert len(doc['animations'])==1
(out/'information-state-verification.json').write_text(json.dumps(dict(visible_technical_groups=6,sampled_frames=[1,61,121,511,705],solid_effects_hidden=True,effects_absent_from_information_glb=True,single_merged_information_clip=True),indent=2)+'\n',newline='\n');print('DROID_TECHNICAL_STATE_VERIFIED')
