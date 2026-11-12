"""Refine the shared lower engine, then derive diagrams from evaluated edges."""
import bpy,bmesh,json,sys,shutil
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];src,out=map(lambda p:Path(p).resolve(),args);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(src/'mega-missile.blend'));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();root=bpy.data.objects['MegaResearchRoot'];model=json.loads((src/'model.json').read_text());deps=bpy.context.evaluated_depsgraph_get();inverse=root.matrix_world.inverted();counts={}
removed=[]
for names in model['components'].values():
 for name in list(names):
  if any(token in name for token in ['thick copper lower panel','hollow lower casing','hollow copper nozzle','annular nozzle support','recessed throat']):
   removed.append(name);names.remove(name);bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
assert len(removed)==7,removed
body=bpy.data.objects['Mega cylindrical pressure casing']
profile=[(.65,.53*1.15,.34),(.95,.54*1.15,.36),(1.20,.47*1.15,.47*1.15)]
for vertex in body.data.vertices:
 z=vertex.co.z
 if z>=1.20-1e-7:continue
 if z<=.65:before,after=profile[0][1:]
 else:
  for a,b in zip(profile,profile[1:]):
   if a[0]<=z<=b[0]:
    weight=(z-a[0])/(b[0]-a[0]);before=a[1]+weight*(b[1]-a[1]);after=a[2]+weight*(b[2]-a[2]);break
 vertex.co.x*=after/before;vertex.co.y*=after/before
body.data.update()
if body.data.has_custom_normals:body.data.normals_split_custom_set([(0,0,0)]*len(body.data.loops))
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
model['removed_inferred_lower_parts']=removed;model['preserved_source_meshes']=56;model['retained_base_meshes']=57;model['refined_source_meshes']=[body.name];model['lower_neck_profile']=profile
model['limitations']=['Threefold fin interpretation retained. Seven inferred lower covers/nozzle parts removed to expose four chambers; lower neck narrowed using the clearer ST13 diagram. Exact dimensions, hidden construction, poses and camera remain authored approximations.']
for role,names in model['components'].items():
 ob=bpy.data.objects[role+' technical wire'];old=ob.data;curve=bpy.data.curves.new(role+' evaluated solid-edge diagram','CURVE');curve.dimensions='3D';curve.bevel_depth=.004;curve.bevel_resolution=0
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
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'mega-missile.blend'));(out/'model.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8');shutil.copy2(src/'material-clock.json',out/'material-clock.json')
(out/'wire-rebuild.json').write_text(json.dumps(dict(components=counts,solid_glb_unchanged=False,reason='Replace omitted lower parts and analytic chamber curves with actual evaluated edges of the shared refined solid.'),indent=2)+'\n',encoding='utf-8');print('MEGA_EVALUATED_WIRES_READY',sum(counts.values()))

bpy.ops.wm.open_mainfile(filepath=str(out/'mega-missile.blend'));s=bpy.context.scene;s.frame_set(1);s.cycles.samples=16;s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True)
newmats=set(m for n in model['new_presentation_meshes'] for m in bpy.data.objects[n].data.materials)
for mat in newmats:
 bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color
 for slot in ['Base Color','Normal']:
  for link in list(bs.inputs[slot].links):mat.node_tree.links.remove(link)
bpy.ops.object.select_all(action='DESELECT');root=bpy.data.objects['MegaResearchRoot'];root.select_set(True)
for names in model['components'].values():
 for name in names:bpy.data.objects[name].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'mega-missile.glb'),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB');print('MEGA_SHARED_DRAFT_READY',sum(len(x) for x in model['components'].values()))
