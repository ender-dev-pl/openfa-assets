"""Refine the source-observed small tracking sensor and derive physical diagrams."""
import bpy,bmesh,json,sys,shutil
from mathutils import Vector
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];src,out=map(lambda p:Path(p).resolve(),args);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(src/'photon-turret.blend'));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();root=bpy.data.objects['PhotonResearchRoot'];model=json.loads((src/'model.json').read_text());deps=bpy.context.evaluated_depsgraph_get();inverse=root.matrix_world.inverted();counts={}
old_receiver=list(model['components']['armoured-tracking-receiver']);handle='Pedestal systems hatch locking handle';lid=bpy.data.objects['Pedestal systems hatch lid']
assert handle in old_receiver;model['components']['elastoplastic-fixed-base'].extend(n for n in old_receiver if n!=handle);model['components']['armoured-tracking-receiver']=[]
bpy.data.objects.remove(bpy.data.objects[handle],do_unlink=True)
for name in [handle,lid.name]:model['preserved_source_meshes'].remove(name)
body_material=bpy.data.objects['Research rounded elastoplastic armour'].data.materials[0];lid.data=lid.data.copy();lid.data.materials.clear();lid.data.materials.append(body_material)
xs=[v.co.x for v in lid.data.vertices];ys=[v.co.y for v in lid.data.vertices];zs=[v.co.z for v in lid.data.vertices]
origin=Vector(((min(xs)+max(xs))*.5,(min(ys)+max(ys))*.5,max(zs)+1));ok,point,normal,index=lid.ray_cast(origin,Vector((0,0,-1)));assert ok
world_front=lid.matrix_world@point;world_normal=(lid.matrix_world.to_3x3().inverted().transposed()@normal).normalized();location=inverse@(world_front+world_normal*.009)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=.016,location=location);lens=bpy.context.object;lens.name='Research armoured tracking sensor lens';lens.parent=root
for p in lens.data.polygons:p.use_smooth=True
mat=body_material.copy();mat.name='Research worn red tracking sensor lens';mat.diffuse_color=(.45,.012,.006,1);bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=.05;bs.inputs['Roughness'].default_value=.32;bs.inputs['Emission Color'].default_value=(.60,.002,.001,1);bs.inputs['Emission Strength'].default_value=1.1
for node in mat.node_tree.nodes:
 if node.type=='VALTORGB':
  for i,e in enumerate(node.color_ramp.elements):e.color=tuple(v*(.65+.30*i) for v in mat.diffuse_color[:3])+(1,)
 if node.type=='BUMP':node.inputs['Distance'].default_value=.00015
lens.data.materials.append(mat);model['components']['armoured-tracking-receiver']=[lens.name];model['new_presentation_meshes'].append(lens.name)
for phase in model['phases']:
 if phase['component']=='armoured-tracking-receiver':phase['local_target']=list(location)
model['receiver_refinement']=dict(removed_handle=handle,recoloured_plate=lid.name,new_lens=lens.name,lens_local_radius=.016,lens_root_location=list(location),surface_world_point=list(world_front),surface_world_normal=list(world_normal),shared_interior_witness=list(world_front-world_normal*.002),source_evidence='PB18 colour dot and ST18 decoded150/157/175 show a small sphere inside a green circular housing, not an entirely selected hatch.')
model['recoloured_source_meshes']=[lid.name];model['removed_source_meshes']=[handle];model['limitations']=['Four original PB18 hardware meshes retain geometry/UV/material slots. Plate geometry/UV/bind retained with armour finish. Small red tracking lens replaces the inferred hatch handle and is the sole receiver highlight; exact hidden construction and authored camera remain approximate.']
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
for role,names in model['components'].items():
 ob=bpy.data.objects[role+' technical wire'];old=ob.data;curve=bpy.data.curves.new(role+' evaluated solid-edge diagram','CURVE');curve.dimensions='3D';curve.bevel_depth=.0006 if role=='armoured-tracking-receiver' else .002;curve.bevel_resolution=0
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
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'photon-turret.blend'));(out/'model.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8');shutil.copy2(src/'material-clock.json',out/'material-clock.json')
export_module=src if (src/'export_solid.py').is_file() else Path(__file__).resolve().parent;assert (export_module/'export_solid.py').is_file();sys.path.insert(0,str(export_module));from export_solid import export_solid
export_solid(root,[bpy.data.objects[n] for names in model['components'].values() for n in names],out/'photon-turret.glb')
(out/'wire-rebuild.json').write_text(json.dumps(dict(components=counts,solid_glb_unchanged=False,reason='Replace inferred hatch-handle receiver with small source-observed lens; derive diagrams from actual evaluated geometry.'),indent=2)+'\n',encoding='utf-8');print('PHOTON_EVALUATED_WIRES_READY',sum(counts.values()))

import hashlib
rig=json.loads((src/'solid-animation-timeline.json').read_text());rig['source_blend_sha256']=hashlib.sha256((out/'photon-turret.blend').read_bytes()).hexdigest();rig['source_glb_sha256']=hashlib.sha256((out/'photon-turret.glb').read_bytes()).hexdigest();(out/'solid-animation-timeline.json').write_text(json.dumps(rig,separators=(',',':'))+'\n',encoding='utf-8')
