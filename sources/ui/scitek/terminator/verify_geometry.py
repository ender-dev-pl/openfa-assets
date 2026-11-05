"""Verify derivative geometry, bindings and exact reuse of the existing source."""
import bpy,sys,json,hashlib,bmesh,struct,math
from pathlib import Path
o=Path(sys.argv[sys.argv.index('--')+1]).resolve();base=Path(sys.argv[sys.argv.index('--base-blend')+1]).resolve() if '--base-blend' in sys.argv else next((a/r for a in Path(__file__).resolve().parents for r in ['sources/docs/assets/reconstruction/ships/terran/terminator/model.blend','docs/assets/reconstruction/ships/terran/terminator/model.blend'] if (a/r).is_file()),None)
assert base is not None
def record(ob):
 d=ob.data;return dict(vertices=[list(v.co) for v in d.vertices],faces=[list(f.vertices)+[f.material_index] for f in d.polygons],uv=[[list(x.uv) for x in layer.data] for layer in d.uv_layers],materials=[m.name for m in d.materials])
def digest(d):return hashlib.sha256(json.dumps(d,separators=(',',':')).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(o/'terminator.blend'));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();m=json.loads((o/'model.json').read_text());root=bpy.data.objects['TerminatorResearchRotor'];roles=['chassis','anterior-device-assembly','lateral-manoeuvring-thrusters','twin-main-engine-thrusters'];assert list(m['components'])==roles
native={};matrices={};closed=0
for name in sum(m['components'].values(),[]):
 ob=bpy.data.objects[name];assert ob.parent==root;bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),name;assert all(f.calc_area()>1e-12 for f in bm.faces),name;bm.free();closed+=1
 if name in m['base_mesh_signatures']:
  native[name]=record(ob);matrices[name]=[v for row in ob.matrix_basis for v in row];assert digest(dict(matrix=matrices[name],**native[name]))==m['base_mesh_signatures'][name],name
assert len(native)==45
assert m['solid_framing']['frame_count']==60 and len(m['solid_framing']['ndc_bounds'])==60
assert all(min(b)>.02 and max(b)<.98 for b in m['solid_framing']['ndc_bounds'])
assert abs(m['solid_framing']['ortho_scale']-s.camera.data.ortho_scale)<1e-6
assert [p['component'] for p in m['phases']]==roles[1:]
assert len([n for n in m['components']['anterior-device-assembly'] if n.startswith('Rotary cannon short barrel')])==5
assert len([n for n in m['components']['lateral-manoeuvring-thrusters'] if n.startswith('Lateral manoeuvring body')])==2
assert len([n for n in m['components']['twin-main-engine-thrusters'] if n.startswith('Terminator exhaust ') and not n.startswith('Terminator exhaust throat')])==2
assert not any(n.startswith('Terminator aft engine housing') for n in m['components']['twin-main-engine-thrusters'])
images={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file};assert images==m['base_packed_images'] and len(images)==4
s.frame_set(1);bpy.context.view_layer.update();start=root.matrix_world.copy();s.frame_set(61);bpy.context.view_layer.update();assert max(abs(start[i][j]-root.matrix_world[i][j]) for i in range(4) for j in range(4))<1e-5
s.frame_set(1);camera=dict(position=list(s.camera.location),rotation_euler=list(s.camera.rotation_euler),ortho_scale=s.camera.data.ortho_scale,resolution=[s.render.resolution_x,s.render.resolution_y])
raw=(o/'terminator.glb').read_bytes();size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);assert len(doc['animations'])==1 and len(doc.get('images',[]))==4
assert len([n for n in doc['nodes'] if n.get('name','').startswith('Wear ')])==4
assert hashlib.sha256(base.read_bytes()).hexdigest()==m['base_source']['sha256']
bpy.ops.wm.open_mainfile(filepath=str(base));errors={}
for name in native:
 ob=bpy.data.objects[name];assert digest(record(ob))==digest(native[name]),name
 errors[name]=max(abs(a-b) for a,b in zip(matrices[name],[v for row in ob.matrix_basis for v in row]));assert errors[name]<1e-5,(name,errors[name])
original_images={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file};assert original_images==images
(o/'geometry-verification.json').write_text(json.dumps(dict(closed_meshes=closed,reused_meshes=45,reused_geometry_uv_materials_exact=True,reused_bind_matrix_max_error=max(errors.values()),packed_images_preserved=images,glb_images=4,anterior_rotary_barrels=5,lateral_thrusters=2,main_exhausts=2,new_geometric_wear_nodes=4,loop_closes=True,solid_camera=camera,root_scale=[1,1,1],base_blend_sha256=m['base_source']['sha256'],blend_sha256=hashlib.sha256((o/'terminator.blend').read_bytes()).hexdigest()),indent=2)+'\n');print('SCITEK_TERMINATOR_GEOMETRY_VERIFIED',closed)
