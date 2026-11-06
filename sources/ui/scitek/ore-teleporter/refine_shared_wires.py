"""Close the inherited partial torus ends and derive physical-edge diagrams."""
import bpy,bmesh,json,sys,shutil
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];src,out=map(lambda p:Path(p).resolve(),args);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(src/'ore-teleporter.blend'));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();root=bpy.data.objects['OreResearchRoot'];model=json.loads((src/'model.json').read_text());deps=bpy.context.evaluated_depsgraph_get();inverse=root.matrix_world.inverted();counts={}
seam=bpy.data.objects['Tower seam.002'];bm=bmesh.new();bm.from_mesh(seam.data)
before=dict(vertices=len(bm.verts),faces=len(bm.faces),boundary_edges=sum(e.is_boundary for e in bm.edges))
assert before['boundary_edges']==16
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
caps=bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=8)['faces'];assert len(caps)==2 and all(len(f.verts)==8 for f in caps)
for face in caps:face.material_index=0;face.smooth=False
bm.normal_update();assert all(e.is_manifold and e.is_contiguous for e in bm.edges);assert bm.calc_volume(signed=True)>0
repair=dict(mesh=seam.name,before=before,after=dict(vertices=len(bm.verts),faces=len(bm.faces),boundary_edges=0),added_cap_faces=2,precision_weld_tolerance=1e-6)
model['preserved_source_meshes'].remove(seam.name);model['repaired_source_meshes']=[seam.name]
bm.to_mesh(seam.data);bm.free();seam.data.update();bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
for role,names in model['components'].items():
 ob=bpy.data.objects[role+' technical wire'];old=ob.data;curve=bpy.data.curves.new(role+' evaluated solid-edge diagram','CURVE');curve.dimensions='3D';curve.bevel_depth=.002;curve.bevel_resolution=0
 for mat in old.materials:curve.materials.append(mat)
 for name in names:
  if 'wear seam' in name:continue
  physical=bpy.data.objects[name];ev=physical.evaluated_get(deps);mesh=ev.to_mesh();bm=bmesh.new();bm.from_mesh(mesh);bm.normal_update()
  for edge in bm.edges:
   if edge.calc_length()<1e-5:continue
   if len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
   a,b=[inverse@physical.matrix_world@v.co for v in edge.verts];sp=curve.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
  bm.free();ev.to_mesh_clear()
 ob.data=curve;bpy.data.curves.remove(old);counts[role]=len(curve.splines)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'ore-teleporter.blend'));model['shared_topology_repair']=repair;(out/'model.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8');shutil.copy2(src/'material-clock.json',out/'material-clock.json')
export_module=src if (src/'export_solid.py').is_file() else Path(__file__).resolve().parent
assert (export_module/'export_solid.py').is_file()
sys.path.insert(0,str(export_module));from export_solid import export_solid
export_solid(root,[bpy.data.objects[n] for group in model['components'].values() for n in group],out/'ore-teleporter.glb')
(out/'wire-rebuild.json').write_text(json.dumps(dict(components=counts,solid_glb_unchanged=False,topology_repair=repair,reason='Close two inherited partial-torus ends; replace pre-modifier diagrams with actual evaluated physical edges.'),indent=2)+'\n',encoding='utf-8');print('ORE_EVALUATED_WIRES_READY',sum(counts.values()))
