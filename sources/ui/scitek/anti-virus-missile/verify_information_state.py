import bpy,sys,json,struct
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(out/'anti-virus-missile-information.blend'));s=bpy.context.scene
for frame in [1,61,121,229,423]:
 s.frame_set(frame);visible=[ob.name for ob in s.objects if ob.type in ['MESH','CURVE'] and not ob.hide_render];assert len(visible)==4 and all(n.endswith(' technical wire') for n in visible),(frame,visible)
raw=(out/'anti-virus-missile-information.glb').read_bytes();size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);assert all(n.get('name','').endswith(' technical wire') for n in doc['nodes'] if 'mesh' in n);assert len(doc['animations'])==1
assert not any(n.get('name','').startswith(('Wear ','Small casing fastener')) for n in doc['nodes'])
(out/'information-state-verification.json').write_text(json.dumps(dict(visible_technical_groups=4,sampled_frames=[1,61,121,229,423],solid_geometry_hidden=True,solid_wear_and_fine_fasteners_absent_from_information_glb=True,single_merged_information_clip=True),indent=2)+'\n',newline='\n');print('ANTI_VIRUS_TECHNICAL_STATE_VERIFIED')
