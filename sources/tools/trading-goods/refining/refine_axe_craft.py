"""TI064 craft pass: recessed lunar inlays, carved haft and restrained aged bronze.

The lunar ornament interprets the Cyreni lore; it is not claimed as recovered writing.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=a.repo/'sources/docs/assets/reconstruction/trading-goods-refined/TI064/remodelled/TI064.blend';prior=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
bronze=next(m for m in bpy.data.materials if 'hand-forged aged bronze' in m.name);bronze=bronze.copy();bronze.name='TI064 / seasoned forged bronze'
bs=bronze.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.235,.155,.047,1);bs.inputs['Roughness'].default_value=.47
for n in bronze.node_tree.nodes:
 if n.type=='VALTORGB':n.color_ramp.elements[0].color=(.12,.075,.020,1);n.color_ramp.elements[-1].color=(.29,.195,.065,1)
 if n.type=='MAP_RANGE':n.inputs['To Min'].default_value=.34;n.inputs['To Max'].default_value=.57
patina=bronze.copy();patina.name='TI064 / oxidised recessed engraving';bs=patina.node_tree.nodes['Principled BSDF'];bs.inputs['Metallic'].default_value=.18;bs.inputs['Base Color'].default_value=(.024,.031,.014,1);bs.inputs['Roughness'].default_value=.76;patina['physical_surface_role']='paint'
for n in patina.node_tree.nodes:
 if n.type=='VALTORGB':n.color_ramp.elements[0].color=(.012,.018,.008,1);n.color_ramp.elements[-1].color=(.046,.051,.024,1)
 if n.type=='MAP_RANGE':n.inputs['To Min'].default_value=.68;n.inputs['To Max'].default_value=.86
blades=[o for o in s.objects if 'solid profiled crescent blade' in o.name];assert len(blades)==2
# Remove raised scratch wires; the aged surface and incised channels carry the detail.
for o in list(s.objects):
 if 'fine forging score' in o.name:bpy.data.objects.remove(o,do_unlink=True)
curves=[o.name for o in s.objects if 'restrained crescent inlay' in o.name];assert len(curves)==8
records=[]
for blade in blades:
 side=1 if sum(v.co.x for v in blade.data.vertices)>0 else -1;blade.data=blade.data.copy();blade.data.materials[0]=bronze;blade.data.materials.append(patina);pi=len(blade.data.materials)-1
 splits=[m for m in blade.modifiers if m.type=='EDGE_SPLIT']
 for m in splits:m.show_viewport=False;m.show_render=False
 cutters=[]
 for name in curves:
  o=bpy.data.objects.get(name)
  if o is None:continue
  p=o.data.splines[0].points[0].co
  if (1 if p.x>0 else -1)!=side:continue
  o.data=o.data.copy();o.data.bevel_depth=.009;o.data.bevel_resolution=3;o.data.use_fill_caps=True
  for sp in o.data.splines:
   for point in sp.points:point.co.y=math.copysign(.071,point.co.y)
  cutters.append(o)
 # A fine inset border follows the stepped face; it is real recessed geometry.
 count=len(blade.data.vertices)//6;assert count*6==len(blade.data.vertices)
 for face in [0,1]:
  pts=[];center=Vector((side*.76,0,2.51));base=face*3*count+2*count
  for i in range(count):
   p=blade.data.vertices[base+i].co.copy();p.x+=(center.x-p.x)*.045;p.z+=(center.z-p.z)*.045;p.y=math.copysign(abs(p.y)-.0015,p.y);pts.append(p)
  d=bpy.data.curves.new('recessed stepped face border','CURVE');d.dimensions='3D';d.bevel_depth=.0035;d.bevel_resolution=2;d.use_fill_caps=True;sp=d.splines.new('POLY');sp.points.add(len(pts)-1);sp.use_cyclic_u=True
  for point,co in zip(sp.points,pts):point.co=(*co,1)
  o=bpy.data.objects.new('TI064 / engraving border cutter',d);s.collection.objects.link(o);cutters.append(o)
 for cutter in cutters:
  bpy.ops.object.select_all(action='DESELECT');cutter.select_set(True);bpy.context.view_layer.objects.active=cutter;bpy.ops.object.convert(target='MESH');cutter=bpy.context.object
  cutter.data.materials.clear()
  for m in blade.data.materials:cutter.data.materials.append(m)
  for p in cutter.data.polygons:p.material_index=pi
  bm=bmesh.new();bm.from_mesh(cutter.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cutter.data);bm.free()
  mod=blade.modifiers.new('True incised lunar metalwork','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
  bpy.context.view_layer.objects.active=blade;blade.select_set(True)
  while blade.modifiers.find(mod.name)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
  bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
 bm=bmesh.new();bm.from_mesh(blade.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);records.append(dict(blade=blade.name,raw_vertices=len(bm.verts),raw_faces=len(bm.faces),nonmanifold_edges=bad));assert bad==0,records;bm.to_mesh(blade.data);bm.free()
 for p in blade.data.polygons:p.use_smooth=True
 # Very shallow broad irregularity preserves the silhouette and polished edge.
 group=blade.vertex_groups.new(name='Forged face relief')
 for v in blade.data.vertices:
  weight=max(0,min(1,(abs(v.co.y)-.035)/.04));group.add([v.index],weight,'REPLACE')
 sub=blade.modifiers.new('Fine surface grid','SUBSURF');sub.subdivision_type='SIMPLE';sub.levels=1;sub.render_levels=1
 tex=bpy.data.textures.new('slow forged surface variation','CLOUDS');tex.noise_scale=.13;disp=blade.modifiers.new('Subtle forged face irregularity','DISPLACE');disp.texture=tex;disp.strength=.0018;disp.mid_level=.5;disp.vertex_group=group.name
 bpy.context.view_layer.objects.active=blade
 while blade.modifiers.find(sub.name)>0:bpy.ops.object.modifier_move_up(modifier=sub.name)
 while blade.modifiers.find(disp.name)>1:bpy.ops.object.modifier_move_up(modifier=disp.name)
 for m in splits:m.show_viewport=True;m.show_render=True
haft=next(o for o in s.objects if 'turned hardwood haft' in o.name);haft.data=haft.data.copy()
for v in haft.data.vertices:
 z=v.co.z;r=math.hypot(v.co.x,v.co.y)
 if .36<z<1.92 and r>.001:
  t=(z-.36)/1.56;theta=math.atan2(v.co.y,v.co.x);depth=.009*math.sin(math.pi*t)**2*(.5+.5*math.cos(8*theta+.5*math.sin(z*2)));v.co.x*=1-depth/r;v.co.y*=1-depth/r
s['refinement']='Artemian ceremonial craft: real recessed lunar metalwork, restrained patina and carved hardwood grip';s.render.filepath='//renders/';bpy.context.preferences.filepaths.save_version=0;a.out.mkdir(parents=True,exist_ok=True);native=a.out/'TI064.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
used={m for o in s.objects if o.type in ['MESH','CURVE','FONT'] for m in o.data.materials}
for m in used:
 bs=m.node_tree.nodes.get('Principled BSDF')
 for key in ['Base Color','Roughness','Normal']:
  for link in list(bs.inputs[key].links):m.node_tree.links.remove(link)
for o in list(s.objects):
 if o.type in ['CURVE','FONT']:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
bpy.ops.export_scene.gltf(filepath=str(a.out/'TI064.glb'),export_format='GLB',export_apply=True,export_animations=False,export_cameras=False,export_lights=False)
r=json.loads((source.parent/'refinement.json').read_text());r.update(refined_native_sha256=sha(native),glb_sha256=sha(a.out/'TI064.glb'),geometry_builder='sources/tools/trading-goods/refining/refine_axe_craft.py',geometry_builder_sha256=sha(Path(__file__)),prior_refined_native=source.relative_to(a.repo).as_posix(),prior_refined_native_sha256=prior,craft_revision='Real Boolean-recessed crescent/border channels, shallow forged-face relief and restrained bronze oxidation; eight tapered carved hardwood flutes. Lunar design remains an authored Cyreni-inspired interpretation.',blade_topology=records,materials=[dict(name=m.name,role=m.get('physical_surface_role','metal'),base_colour=list(m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value)) for m in sorted(used,key=lambda m:m.name)]);(a.out/'refinement.json').write_text(json.dumps(r,indent=2)+'\n');assert sha(source)==prior;print('ARTEMIAN_AXE_CRAFT_REFINED',flush=True)
