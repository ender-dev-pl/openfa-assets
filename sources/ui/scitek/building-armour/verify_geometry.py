import bpy,sys,json,bmesh,hashlib,struct
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(out/'building-armour.blend'));s=bpy.context.scene
model=json.loads((out/'model.json').read_text());root=bpy.data.objects['ArmourRotor'];roles=['chassis','ionisers','thermal-transducers','damage-monitor'];assert list(model['components'])==roles
obs=list(s.objects);meshes=[ob for ob in obs if ob.type=='MESH']
for ob in meshes:
 bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),ob.name;bm.free();assert ob.parent==root
for prefix,n in [('Armour ioniser capsule',4),('Ioniser metal collar',4),('Rounded side carry handle',2),('Rear thermal transducer panel',2),('Damage control monitoring face',1),('Solid only blue ionisation field',12)]:assert len([ob for ob in obs if ob.name.startswith(prefix)])==n,prefix
assert len(model['solid_only_effect_nodes'])==12 and not any(n in sum(model['components'].values(),[]) for n in model['solid_only_effect_nodes'])
for n in model['solid_only_effect_nodes']:
 ob=bpy.data.objects[n];assert ob.type=='CURVE' and ob.data.use_fill_caps and ob['scitek_solid_only_effect'] and not ob.hide_render
assert len(model['components']['ionisers'])==4
assert [x['component'] for x in model['phases']]==roles[1:]
assert abs(model['phases'][1]['closeup_rotation_euler'][2]-3.141592653589793)<1e-5
assert all(abs(a-1)<1e-5 for a in root.scale)
def glb_names(p):
 raw=p.read_bytes();length=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+length]);return [n.get('name','') for n in doc['nodes']]
names=glb_names(out/'building-armour.glb');assert all(n in names for n in model['solid_only_effect_nodes'])
for p in out.glob('building-armour-*.glb'):assert not any('Solid only blue ionisation field' in n for n in glb_names(p)),p
assert s.camera.data.type=='ORTHO' and abs(s.camera.data.ortho_scale-3.65)<1e-5
camera=dict(position=list(s.camera.location),rotation_euler=list(s.camera.rotation_euler),ortho_scale=s.camera.data.ortho_scale,resolution=[s.render.resolution_x,s.render.resolution_y],framing='Fixed authored source-inspired canvas; blue fields intentionally extend beyond this view')
(out/'geometry-verification.json').write_text(json.dumps(dict(closed_meshes=len(meshes),ionisers=4,carry_handles=2,rear_thermal_panels=2,front_monitor=1,solid_only_effect_strands=12,effects_absent_from_technical_glbs=True,root_scale=list(root.scale),solid_camera=camera,blend_sha256=hashlib.sha256((out/'building-armour.blend').read_bytes()).hexdigest()),indent=2)+'\n',newline='\n');print('ARMOUR_GEOMETRY_VERIFIED',len(meshes))
