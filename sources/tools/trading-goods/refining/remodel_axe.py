"""TI064: substantial crescent blades, tapered cutting bevels and a turned wooden haft.

The fan-shaped stepped outline follows the local legacy reference. Restrained lunar
inlays are an authored interpretation of the Cyreni description, not recovered glyphs.
"""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);sys.path.insert(0,str(a.repo/'sources/tools/trading-goods'));import modelling as M
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=a.repo/'sources/docs/assets/reconstruction/trading-goods-refined/TI064/TI064.blend';prior=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;M.ID='TI064';M.COL=s.collection
bronze=next(m for m in bpy.data.materials if 'ceremonial gold' in m.name).copy();bronze.name='TI064 / hand-forged aged bronze'
wood=next(m for m in bpy.data.materials if 'reddish antique wood' in m.name).copy();wood.name='TI064 / carved reddish hardwood'
def adjust(m,c,rough):
 bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=rough
 for n in m.node_tree.nodes:
  if n.type=='VALTORGB':n.color_ramp.elements[0].color=(*[v*.73 for v in c],1);n.color_ramp.elements[-1].color=(*[v*1.13 for v in c],1)
  if n.type=='MAP_RANGE':n.inputs['To Min'].default_value=rough*.80;n.inputs['To Max'].default_value=min(1,rough*1.20)
adjust(bronze,(.30,.205,.065),.42);adjust(wood,(.16,.043,.014),.43)
wood.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value=.12
wood.node_tree.nodes['Principled BSDF'].inputs['Coat Roughness'].default_value=.34
for node in wood.node_tree.nodes:
 if node.type=='VECT_MATH' and node.operation=='MULTIPLY':node.inputs[1].default_value=(6,6,.22)
for n in bronze.node_tree.nodes:
 if n.type=='VECT_MATH' and n.operation=='MULTIPLY':n.inputs[1].default_value=(2,2,2)
 if n.type=='BUMP':n.inputs['Distance'].default_value=.0014;n.inputs['Strength'].default_value=.22
edge=bronze.copy();edge.name='TI064 / burnished bronze cutting bevel';adjust(edge,(.52,.37,.13),.24)
for n in edge.node_tree.nodes:
 if n.type=='BUMP':n.inputs['Distance'].default_value=.00015;n.inputs['Strength'].default_value=.12
inlay=bronze.copy();inlay.name='TI064 / pale bronze lunar inlay';adjust(inlay,(.44,.32,.12),.34)
dark=bronze.copy();dark.name='TI064 / dark recess patina';adjust(dark,(.035,.023,.009),.67)
for o in list(s.objects):bpy.data.objects.remove(o,do_unlink=True)
root=M.root('Artemian ritual double axe')
# Turned wood retains the narrow neck and fuller central grip of the reference.
profile=[(.105,.00),(.12,.04),(.105,.10),(.065,.17),(.062,.30),(.067,.55),(.084,.82),(.105,1.13),(.108,1.28),(.094,1.47),(.073,1.77),(.062,2.06),(.062,2.35),(.068,2.62),(.10,2.71),(.105,2.77),(.075,2.82),(.015,2.83)]
haft=M.lathe('turned hardwood haft with tapered grip',profile,wood,root,segments=80)
sub=haft.modifiers.new('Smooth turned transitions','SUBSURF');sub.levels=2;sub.render_levels=2
socket=M.lathe('solid bronze head socket',[(.145,2.34),(.162,2.37),(.155,2.43),(.151,2.63),(.16,2.68),(.14,2.71)],bronze,root,segments=64)
bevel=socket.modifiers.new('Forged socket edge radii','BEVEL');bevel.width=.008;bevel.segments=3
for z in [2.38,2.66]:M.ring('burnished socket binding',(0,0,z),.156,.009,edge,root)
for z in [2.46,2.59]:
 for side in [-1,1]:M.ball('peened socket pin',(0,side*.153,z),(.026,.012,.026),edge,root,2)
# Smooth convex cutting arc, with stepped inboard notches as in the original icon.
arc=[(.53,2.98),(.78,2.96),(1.04,2.86),(1.25,2.70),(1.36,2.51),(1.30,2.30),(1.13,2.12),(.91,1.99)]
def catmull(p0,p1,p2,p3,t):return .5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
curve=[]
for i in range(len(arc)-1):
 p0=Vector(arc[max(0,i-1)]);p1=Vector(arc[i]);p2=Vector(arc[i+1]);p3=Vector(arc[min(len(arc)-1,i+2)])
 for k in range(6):curve.append(tuple(catmull(p0,p1,p2,p3,k/6)))
curve.append(arc[-1]);outline=curve+[(.88,2.10),(.76,2.10),(.77,2.24),(.61,2.19),(.62,2.31),(.38,2.39),(.09,2.42),(.09,2.56),(.39,2.58),(.59,2.71),(.47,2.75),(.61,2.86)]
center=Vector((.76,2.51));N=len(outline)
for side in [-1,1]:
 verts=[];faces=[];mats=[]
 # Separate front/back bevel rings produce actual section thickness, not flat polygons.
 for front in [-1,1]:
  for shrink,height in [(0,.008),(.045,.030),(.13,.067)]:
   for x,z in outline:
    q=Vector((x,z)).lerp(center,shrink);bulge=.008*math.sin((q.x-.1)*math.pi/1.4) if shrink>.1 else 0;verts.append((side*q.x,front*(height+bulge),q.y))
 for front_index in range(2):
  base=front_index*3*N
  for ring in range(2):
   for i in range(N):faces.append((base+ring*N+i,base+ring*N+(i+1)%N,base+(ring+1)*N+(i+1)%N,base+(ring+1)*N+i));mats.append(1 if ring==0 else 0)
  points=[Vector((verts[base+2*N+i][0],0,verts[base+2*N+i][2])) for i in range(N)];lookup={tuple(round(v,6) for v in p):i for i,p in enumerate(points)}
  for tri in tessellate_polygon([points]):faces.append(tuple(base+2*N+(p if isinstance(p,int) else lookup[tuple(round(v,6) for v in p)]) for p in tri));mats.append(0)
 for i in range(N):faces.append((i,(i+1)%N,3*N+(i+1)%N,3*N+i));mats.append(1)
 blade=M.mesh('solid profiled crescent blade '+str(side),verts,faces,bronze,root);blade.data.materials.append(edge)
 for f,mi in zip(blade.data.polygons,mats):f.material_index=mi;f.use_smooth=True
 bm=bmesh.new();bm.from_mesh(blade.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(blade.data);bm.free()
 split=blade.modifiers.new('Keep stepped corners and cutting bevels defined','EDGE_SPLIT');split.split_angle=math.radians(36)
 # Fine front/back inlays stay within the substantial forged face.
 for front in [-1,1]:
  y=front*.078
  for radius in [.155,.184]:
   points=[(side*(.80+radius*math.cos(math.radians(55+250*k/50))),y,2.52+radius*math.sin(math.radians(55+250*k/50))) for k in range(51)]
   M.polyline('restrained crescent inlay',points,.0045,inlay,root)
  for z in [2.36,2.69]:M.ball('small inlaid star point',(side*.72,y,z),(.013,.006,.013),inlay,root,2)
  # Short recessed-looking patina scores give each blade a hand-worked character.
  for j in range(7):
   x=.96+j*.023;z=2.39+(j%3)*.026;M.polyline('fine forging score',[(side*x,y*.99,z),(side*(x+.025),y*.99,z+.045)],.0022,dark,root)
# Restrained ferrules, not a modern wrapped combat grip.
for radius,z in [(.066,.26),(.074,1.70)]:M.ring('fine haft collar',(0,0,z),radius,.007,edge,root)
bpy.context.view_layer.update();M.setup_camera();s.render.filepath='//renders/';s['refinement']='TI064 rebuilt solid stepped crescent head and turned haft';bpy.context.preferences.filepaths.save_version=0;a.out.mkdir(parents=True,exist_ok=True);native=a.out/'TI064.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
used={m for o in s.objects if o.type in ['MESH','CURVE','FONT'] for m in o.data.materials}
for m in used:
 bs=m.node_tree.nodes.get('Principled BSDF')
 for key in ['Base Color','Roughness','Normal']:
  for link in list(bs.inputs[key].links):m.node_tree.links.remove(link)
for o in list(s.objects):
 if o.type in ['CURVE','FONT']:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
bpy.ops.export_scene.gltf(filepath=str(a.out/'TI064.glb'),export_format='GLB',export_apply=True,export_animations=False,export_cameras=False,export_lights=False)
r=json.loads((source.parent/'refinement.json').read_text());r.update(refined_native_sha256=sha(native),glb_sha256=sha(a.out/'TI064.glb'),geometry_builder='sources/tools/trading-goods/refining/remodel_axe.py',geometry_builder_sha256=sha(Path(__file__)),prior_refined_native=source.relative_to(a.repo).as_posix(),prior_refined_native_sha256=prior,model_geometry='Separately editable solid crescent blades with stepped inboard notches, convex cutting arcs, tapered thickness and burnished bevels; forged socket and peened pins; turned tapered hardwood haft. Lunar inlays are authored interpretation of the Cyreni description, not recovered glyphs.',materials=[dict(name=m.name,role=m.get('physical_surface_role','metal'),base_colour=list(m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value),roughness=m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value) for m in sorted(used,key=lambda m:m.name)]);(a.out/'refinement.json').write_text(json.dumps(r,indent=2)+'\n');assert sha(source)==prior;print('TI064_GEOMETRY_REBUILT',flush=True)
