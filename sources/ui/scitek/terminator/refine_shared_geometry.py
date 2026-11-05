"""Put display grid into real wing topology without changing surface or UV field."""
import bpy,bmesh,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from precise_triangle_distance import nearest,interpolate
args=sys.argv[sys.argv.index('--')+1:];src,out=map(lambda p:Path(p).resolve(),args);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(src/'terminator.blend'));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();root=bpy.data.objects['TerminatorResearchRotor'];model=json.loads((src/'model.json').read_text());wing_reports={}
def point(side,u,t):
 a=Vector((.48,-1.30,0)).lerp(Vector((.56,1.10,0)),t);b=Vector((1.55,-.45,0)).lerp(Vector((2.10,1.65,0)),t);p=a.lerp(b,u);return Vector((side*p.x,p.y,.09-.025*p.x))
for side in [-1,1]:
 ob=bpy.data.objects[f'Terminator swept outer wing {side}'];mesh=ob.data;old=mesh.copy();old.calc_loop_triangles();verts=[v.co.copy() for v in old.vertices];triangles=[tuple(t.vertices) for t in old.loop_triangles];bvh=BVHTree.FromPolygons(verts,triangles,all_triangles=True);uvs={uv.name:[tuple(x.uv) for x in uv.data] for uv in old.uv_layers}
 work=bpy.data.meshes.new(ob.name+' surface-preserving triangles');work.from_pydata(verts,[],triangles);work.update()
 for mat in mesh.materials:work.materials.append(mat)
 for name,values in uvs.items():
  layer=work.uv_layers.new(name=name)
  for face,triangle in zip(work.polygons,old.loop_triangles):
   face.material_index=old.polygons[triangle.polygon_index].material_index;face.use_smooth=old.polygons[triangle.polygon_index].use_smooth
   for li,original_li in zip(face.loop_indices,triangle.loops):layer.data[li].uv=values[original_li]
 ob.data=work;bpy.data.meshes.remove(mesh);mesh=work
 planes=[]
 for axis in [0,1]:
  for i in range(1,18):
   a=point(side,i/18,0) if axis==0 else point(side,0,i/18);b=point(side,i/18,1) if axis==0 else point(side,1,i/18);normal=(b-a).cross(Vector((side*.025,0,1))).normalized();planes.append((tuple(a),tuple(normal)))
 polygons=[[tuple(verts[i]) for i in triangle] for triangle in triangles]
 for origin,normal in planes:
  result=[]
  for poly in polygons:
   distances=[sum((v[i]-origin[i])*normal[i] for i in range(3)) for v in poly]
   if min(distances)>=-1e-10 or max(distances)<=1e-10:result.append(poly);continue
   for sign in [-1,1]:
    clipped=[]
    for j,a in enumerate(poly):
     b=poly[(j+1)%len(poly)];da=distances[j]*sign;db=distances[(j+1)%len(poly)]*sign
     if da>=-1e-10:clipped.append(a)
     if (da>1e-10 and db< -1e-10) or (da< -1e-10 and db>1e-10):
      weight=da/(da-db);clipped.append(tuple(a[i]+weight*(b[i]-a[i]) for i in range(3)))
    if len(clipped)>=3:result.append(clipped)
  polygons=result
 vertices=[];faces=[];lookup={}
 for poly in polygons:
  face=[]
  for v in poly:
   key=tuple(round(x,8) for x in v)
   if key not in lookup:lookup[key]=len(vertices);vertices.append(v)
   index=lookup[key]
   if not face or face[-1]!=index:face.append(index)
  if face and face[0]==face[-1]:face.pop()
  if len(set(face))>=3:faces.append(face)
 replacement=bpy.data.meshes.new(ob.name+' real eighteen-division grid');replacement.from_pydata(vertices,[],faces);replacement.update()
 for mat in mesh.materials:replacement.materials.append(mat)
 for name in uvs:replacement.uv_layers.new(name=name)
 ob.data=replacement;bpy.data.meshes.remove(mesh);mesh=replacement
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update();maximum=0
 for face in mesh.polygons:
  centre=sum((mesh.vertices[i].co for i in face.vertices),Vector())/len(face.vertices);index,distance=nearest(centre,verts,triangles);assert distance<2e-6,(ob.name,distance,list(centre),list(face.vertices));triangle=old.loop_triangles[index];face.use_smooth=old.polygons[triangle.polygon_index].use_smooth;a,b,c=[verts[i] for i in triangle.vertices]
  for name,values in uvs.items():
   uv=mesh.uv_layers[name];ta,tb,tc=[Vector((*values[li],0)) for li in triangle.loops]
   for li in face.loop_indices:
    v=mesh.vertices[mesh.loops[li].vertex_index].co;tex=interpolate(v,a,b,c,ta,tb,tc);uv.data[li].uv=tex
 for v in mesh.vertices:maximum=max(maximum,nearest(v.co,verts,triangles)[1])
 mesh.calc_loop_triangles();newverts=[v.co.copy() for v in mesh.vertices];newtriangles=[tuple(t.vertices) for t in mesh.loop_triangles]
 for v in verts:maximum=max(maximum,nearest(v,newverts,newtriangles)[1])
 assert maximum<2e-6
 wing_reports[ob.name]=dict(original_vertices=len(old.vertices),refined_vertices=len(mesh.vertices),original_faces=len(old.polygons),refined_faces=len(mesh.polygons),bidirectional_surface_max_error=maximum,uv_method='Original loop-triangle affine UV field interpolated per retained physical face; no texture change.')
 bpy.data.meshes.remove(old)
deps=bpy.context.evaluated_depsgraph_get();inverse=root.matrix_world.inverted();counts={}
for role,names in model['components'].items():
 ob=bpy.data.objects[role+' technical wire'];old=ob.data;curve=bpy.data.curves.new(role+' evaluated solid-edge diagram','CURVE');curve.dimensions='3D';curve.bevel_depth=.004 if role=='chassis' else .0025;curve.bevel_resolution=0
 for mat in old.materials:curve.materials.append(mat)
 for name in names:
  physical=bpy.data.objects[name]
  if name.startswith(('Wear ','Terminator cooling rib','Terminator crown vent fin')):continue
  ev=physical.evaluated_get(deps);data=ev.to_mesh();bm=bmesh.new();bm.from_mesh(data);bm.normal_update()
  for edge in bm.edges:
   if edge.calc_length()<1e-5:continue
   if not name.startswith('Terminator swept outer wing') and len(edge.link_faces)==2 and edge.calc_face_angle(0)<.012:continue
   a,b=[inverse@physical.matrix_world@v.co for v in edge.verts];sp=curve.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
  bm.free();ev.to_mesh_clear()
 ob.data=curve;bpy.data.curves.remove(old);counts[role]=len(curve.splines)
model.update(object_id='openfa:terminator',whole_information_local_target=[0,-.10,.10],whole_information_ortho_scale=6.0,wire_display_contract='Actual evaluated physical edges. Bilinear wing grid now belongs to real wing topology; surface/UV field preserved.',retessellated_wings=wing_reports)
(out/'model.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8');(out/'wing-refinement.json').write_text(json.dumps(dict(wings=wing_reports,diagram_segments=counts,input_blend_sha256=hashlib.sha256((src/'terminator.blend').read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8')
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'terminator.blend'))
flat=['Used research device graphite steel','Worn anterior titanium','Research thruster soot recess','Used blue lateral thruster casing','Heat stained anterior brass','Faded device alignment marking']
for name in flat:
 if name not in bpy.data.materials:continue
 mat=bpy.data.materials[name];bs=mat.node_tree.nodes.get('Principled BSDF')
 for slot in ['Base Color','Normal','Metallic','Roughness']:
  for link in list(bs.inputs[slot].links):mat.node_tree.links.remove(link)
 bs.inputs['Base Color'].default_value=mat.diffuse_color
bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
for names in model['components'].values():
 for name in names:bpy.data.objects[name].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'terminator.glb'),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_format='GLB');print('TERMINATOR_PHYSICAL_GRID_READY',sum(counts.values()))
