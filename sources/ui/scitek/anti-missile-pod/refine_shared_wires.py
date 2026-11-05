"""Regenerate diagram curves from evaluated physical edges; preserve the solid."""
import bpy,bmesh,json,sys,shutil
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];src,out=map(lambda p:Path(p).resolve(),args);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(src/'anti-missile-pod.blend'));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();root=bpy.data.objects['PodResearchRoot'];model=json.loads((src/'model.json').read_text());deps=bpy.context.evaluated_depsgraph_get();inverse=root.matrix_world.inverted();counts={}
for role,names in model['components'].items():
 ob=bpy.data.objects[role+' technical wire'];old=ob.data;curve=bpy.data.curves.new(role+' evaluated solid-edge diagram','CURVE');curve.dimensions='3D';curve.bevel_depth=.002;curve.bevel_resolution=0
 for mat in old.materials:curve.materials.append(mat)
 for name in names:
  if name.startswith('Wear '):continue
  physical=bpy.data.objects[name];ev=physical.evaluated_get(deps);mesh=ev.to_mesh();bm=bmesh.new();bm.from_mesh(mesh);bm.normal_update()
  for edge in bm.edges:
   if edge.calc_length()<1e-5:continue
   if len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
   a,b=[inverse@physical.matrix_world@v.co for v in edge.verts];sp=curve.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
  bm.free();ev.to_mesh_clear()
 ob.data=curve;bpy.data.curves.remove(old);counts[role]=len(curve.splines)
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'anti-missile-pod.blend'));shutil.copy2(src/'anti-missile-pod.glb',out/'anti-missile-pod.glb');shutil.copy2(src/'model.json',out/'model.json');shutil.copy2(src/'material-clock.json',out/'material-clock.json')
(out/'wire-rebuild.json').write_text(json.dumps(dict(components=counts,solid_glb_unchanged=True,reason='Previous raw pre-modifier wire edges failed evaluated-solid correspondence.'),indent=2)+'\n',encoding='utf-8');print('POD_EVALUATED_WIRES_READY',sum(counts.values()))
