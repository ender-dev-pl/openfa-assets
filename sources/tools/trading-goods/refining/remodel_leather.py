"""TI041 garment reconstruction: shaped leather shells, curved footwear and raised trim.

Original reference implies a decorated long coat, separate belt and paired boots.
Fine embroidery is an authored approximation, not a transcription of legacy pixels.
The first-pass native and the earlier material-only checkpoint remain preserved.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy
import bmesh
from mathutils import Vector

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--repo',type=Path,required=True)
ap.add_argument('--out',type=Path,required=True)
a=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
sys.path.insert(0,str(a.repo/'sources/tools/trading-goods'))
import modelling as M
source=a.repo/'sources/docs/assets/reconstruction/trading-goods-refined/TI041/TI041.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_hash=sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene
M.ID='TI041';M.COL=s.collection
leather=next(m for m in bpy.data.materials if 'worked leather' in m.name).copy()
gold=next(m for m in bpy.data.materials if 'aged brass' in m.name).copy()
leather.name='TI041 / grained chestnut leather'
gold.name='TI041 / antique gold embroidery'
def recolour(m,c,rough):
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=rough
 for n in m.node_tree.nodes:
  if n.type=='VALTORGB':
   n.color_ramp.elements[0].color=(*[v*.72 for v in c],1);n.color_ramp.elements[-1].color=(*[v*1.16 for v in c],1)
  if n.type=='MAP_RANGE':n.inputs['To Min'].default_value=rough*.83;n.inputs['To Max'].default_value=min(1,rough*1.17)
recolour(leather,(.115,.027,.010),.64)
for node in leather.node_tree.nodes:
 if node.type=='BUMP':node.inputs['Distance'].default_value=.002;node.inputs['Strength'].default_value=.30
recolour(gold,(.50,.28,.065),.48)
lining=leather.copy();lining.name='TI041 / dark leather lining';recolour(lining,(.025,.008,.004),.88)
sole=leather.copy();sole.name='TI041 / layered leather sole';recolour(sole,(.035,.012,.006),.77)
thread=gold.copy();thread.name='TI041 / ochre saddle stitching';recolour(thread,(.40,.22,.065),.72);thread.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=.25
for o in list(s.objects):bpy.data.objects.remove(o,do_unlink=True)


def mesh(name,verts,faces,mat,parent=None,sub=1,thickness=0):
 o=M.mesh(name,verts,faces,mat,parent)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 for f in o.data.polygons:f.use_smooth=True
 if sub:
  m=o.modifiers.new('Tailored smooth surface','SUBSURF');m.levels=sub;m.render_levels=sub
 if thickness:
  o.data.materials.append(lining);m=o.modifiers.new('Actual leather thickness and dark inner face','SOLIDIFY');m.thickness=thickness;m.offset=0;m.material_offset=1;m.material_offset_rim=1
 return o


def line(name,points,r=.007,mat=gold,parent=None):
 return M.polyline(name,points,r,mat,parent)


def interpolate(z,profile):
 for (z0,v0),(z1,v1) in zip(profile,profile[1:]):
  if z<=z1:return v0+(v1-v0)*(z-z0)/(z1-z0)
 return profile[-1][1]


coat=M.root('tailored long coat with open front',(-.30,.38,0))
rxprofile=[(.12,.67),(.35,.65),(.9,.58),(1.45,.45),(1.85,.43),(2.2,.51),(2.55,.64),(2.72,.66),(2.9,.51),(3.05,.29)]
ryprofile=[(.12,.32),(.9,.29),(1.65,.26),(2.25,.31),(2.65,.30),(2.9,.25),(3.05,.21)]
def body(z,t,offset=0):
 gap=.16+.38*max(0,(z-2.15)/.90)
 theta=gap+(math.tau-2*gap)*t
 rx=interpolate(z,rxprofile);ry=interpolate(z,ryprofile)
 # Broad hanging folds below the waist, small leather creases across the waist.
 fold=.014*math.sin(theta*10+.5*z)*max(0,(1.8-z)/1.8)+.009*math.sin(z*23+theta*5)*math.exp(-((z-1.72)/.25)**2)
 return Vector(((rx+fold+offset)*math.sin(theta),-(ry+fold+offset)*math.cos(theta),z+.009*math.cos(theta*9)*max(0,1-z/.5)))
rows,cols=49,80
verts=[body(.12+2.93*j/(rows-1),i/(cols-1)) for j in range(rows) for i in range(cols)]
faces=[(j*cols+i,j*cols+i+1,(j+1)*cols+i+1,(j+1)*cols+i) for j in range(rows-1) for i in range(cols-1)]
mesh('continuous fitted body, flared skirt and sculpted waist folds',verts,faces,leather,coat,1,.024)
for side,t in [(-1,1),(1,0)]:
 line('front embroidered piping '+str(side),[body(.13+2.91*j/70,t,.016) for j in range(71)],.014,gold,coat)
 line('parallel saddle seam '+str(side),[body(.15+2.86*j/110,t+(.014 if t==0 else -.014),.018) for j in range(111)],.004,thread,coat)
 for j in range(13):
  z=.26+j*.19
  # Small paired leaf scrolls follow the actual shaped leather surface.
  for leaf in [-1,1]:
   points=[]
   for k in range(25):
    phase=math.tau*k/24;tt=t+side*(.018+.012*(1-math.cos(phase)));zz=z+leaf*.075*math.sin(phase)
    points.append(body(zz,tt,.021))
   line('raised front leaf scroll',points,.0055,gold,coat)
# Broad neck binding and the hem follow the garment instead of floating rings.
for z,r in [(3.045,.022),(.135,.015)]:
 line('shaped gold collar' if z>3 else 'curved embroidered hem',[body(z,j/100,.014) for j in range(101)],r,gold,coat)
# Turned lapels have thickness and a curved fold, separate from the torso shell.
for side in [-1,1]:
 v=[];f=[]
 for j in range(17):
  u=j/16;z=2.10+.86*u;t=0 if side==1 else 1;base=body(z,t,.026)
  for i in range(5):
   q=i/4;v.append(base+Vector((side*.17*math.sin(math.pi*u)*q,-.09*math.sin(math.pi*q)*math.sin(math.pi*u),.025*q)))
 for j in range(16):
  for i in range(4):f.append((j*5+i,j*5+i+1,(j+1)*5+i+1,(j+1)*5+i))
 mesh('folded leather lapel',v,f,leather,coat,1,.018)
 line('lapel edge stitching',[v[j*5+4] for j in range(17)],.006,thread,coat)
# Curved open sleeves, with compressed elbow folds and a cuff lining.
for side in [-1,1]:
 centers=[];verts=[];faces=[];nr,nc=35,40
 for j in range(nr):
  t=j/(nr-1);center=Vector((side*(.54+.48*t+.04*math.sin(math.pi*t)),.01-.10*t,2.72-1.10*t));centers.append(center)
  axis=Vector((side*.48,-.1,-1.10)).normalized();u=Vector((0,1,0));v=axis.cross(u).normalized();radius=.235-.062*t+.016*math.sin(t*math.pi)
  for i in range(nc):
   th=i*math.tau/nc;wrinkle=.012*math.sin(t*28+th*1.7)*math.exp(-((t-.51)/.23)**2)+.003*math.sin(t*59+th*3)
   verts.append(center+(u*math.cos(th)+v*math.sin(th))*(radius+wrinkle))
 for j in range(nr-1):
  for i in range(nc):faces.append((j*nc+i,j*nc+(i+1)%nc,(j+1)*nc+(i+1)%nc,(j+1)*nc+i))
 # Rounded shoulder cap closes the upper sleeve; no disconnected open tube.
 pole=len(verts);verts.append(centers[0]+Vector((-side*.05,0,.16)))
 faces.extend((pole,(i+1)%nc,i) for i in range(nc))
 mesh('bent and wrinkled sleeve '+str(side),verts,faces,leather,coat,1,.023)
 for j in [nr-1,nr-4]:line('cuff gold binding',verts[j*nc:(j+1)*nc]+[verts[j*nc]],.013,gold,coat)
 line('sleeve longitudinal seam',[verts[j*nc+nc//2] for j in range(nr)],.005,thread,coat)
 for j in range(8):
  k=3+j*4;pos=verts[k*nc+nc//2]+Vector((0,-.012,0));M.ball('tiny sleeve seam stud',pos,(.011,.009,.011),gold,coat,1)

# Footwear uses rounded lasts and a thin sole, not cuboid toes.
for index,x in enumerate([1.35,1.94]):
 boot=M.root('separate shaped leather boot '+str(index),(x,-.08,0));verts=[];faces=[];nr,nc=32,48
 for j in range(nr):
  t=j/(nr-1);z=.20+1.13*t;rx=interpolate(z,[(.2,.145),(.4,.13),(.75,.17),(1.15,.20),(1.33,.19)]);ry=rx*.84
  for i in range(nc):
   th=i*math.tau/nc;fold=.012*math.sin(z*49+th*1.2)*math.exp(-((z-.40)/.18)**2)+.005*math.sin(z*33+th*2)
   verts.append(((rx+fold)*math.sin(th),-(ry+fold)*math.cos(th),z+.012*math.cos(th)))
 for j in range(nr-1):
  for i in range(nc):faces.append((j*nc+i,j*nc+(i+1)%nc,(j+1)*nc+(i+1)%nc,(j+1)*nc+i))
 mesh('tapered calf shaft with ankle creases',verts,faces,leather,boot,1,.020)
 for j in [nr-1,nr-3]:line('boot top binding',verts[j*nc:(j+1)*nc]+[verts[j*nc]],.009,gold,boot)
 # Curved vamp: closed elliptical cross sections along the foot's long axis.
 profile=[(.23,.035,.06,.16),(.19,.115,.10,.18),(.04,.17,.17,.19),(-.16,.19,.15,.18),(-.37,.18,.105,.15),(-.52,.13,.07,.13),(-.57,.035,.025,.125)]
 vv=[];ff=[]
 for y,rx,rz,cz in profile:
  for i in range(48):
   th=math.tau*i/48;vv.append((rx*math.sin(th),y,cz+rz*math.cos(th)))
 for j in range(len(profile)-1):
  for i in range(48):ff.append((j*48+i,j*48+(i+1)%48,(j+1)*48+(i+1)%48,(j+1)*48+i))
 ff.extend([tuple(range(47,-1,-1)),tuple((len(profile)-1)*48+i for i in range(48))])
 mesh('rounded toe, instep and heel counter',vv,ff,leather,boot,2)
 outline=[]
 for k in range(65):
  th=math.tau*k/64;y=-.17+.405*math.cos(th);width=.175*(.92+.08*math.sin(th));outline.append((width*math.sin(th),y,.075))
 # Three continuous stitched sole welts make thickness readable without block feet.
 for z in [.055,.077,.098]:line('layered stitched sole welt',[(p[0],p[1],z) for p in outline],.018,sole,boot)
 line('sole saddle stitch',[(p[0]*1.03,p[1],.107) for p in outline],.0045,thread,boot)
 heel=M.cube('rounded stacked heel',(0,.12,.073),(.13,.105,.065),sole,boot,bevel=.055)
 for side in [-1,1]:
  points=[]
  for k in range(50):
   z=.29+1.00*k/49;rx=interpolate(z,[(.2,.145),(.4,.13),(.75,.17),(1.15,.20),(1.33,.19)])
   points.append((side*.055,-rx*.84-.012,z))
  line('boot front seam',points,.005,thread,boot)
  for j in range(9):
   z=.37+j*.098;rx=interpolate(z,[(.2,.145),(.4,.13),(.75,.17),(1.15,.20),(1.33,.19)])
   line('boot ornamental crossing',[(side*.04,-rx*.84-.016,z-.027),(side*.073,-rx*.84-.018,z),(side*.04,-rx*.84-.016,z+.027)],.0055,gold,boot)

belt=M.root('separate flat worked belt',(-1.60,-.28,.075))
verts=[];faces=[]
for j in range(3):
 for i in range(80):
  th=math.tau*i/80;verts.append((.48*math.cos(th),.29*math.sin(th),j*.055))
for j in range(2):
 for i in range(80):faces.append((j*80+i,j*80+(i+1)%80,(j+1)*80+(i+1)%80,(j+1)*80+i))
mesh('flat oval leather belt strap',verts,faces,leather,belt,1,.025)
for z in [.012,.098]:line('belt edge saddle stitching',[(.496*math.cos(math.tau*k/100),.302*math.sin(math.tau*k/100),z) for k in range(101)],.005,thread,belt)
line('rounded rectangular gold belt buckle',[(.40,-.09,.12),(.55,-.09,.12),(.57,-.06,.12),(.57,.06,.12),(.55,.09,.12),(.40,.09,.12),(.38,.06,.12),(.38,-.06,.12),(.40,-.09,.12)],.014,gold,belt)
line('belt buckle tongue',[(.40,0,.128),(.56,0,.128)],.008,gold,belt)
for k in range(12):
 th=math.tau*(k+.5)/12;M.ball('belt ornament stud',(.498*math.cos(th),.307*math.sin(th),.056),(.012,.012,.012),gold,belt,1)

bpy.context.view_layer.update();M.setup_camera();s['refinement']='TI041 geometry correction: tailored shells, leather folds, rounded footwear and raised trim';s.render.filepath='//renders/';bpy.context.preferences.filepaths.save_version=0
a.out.mkdir(parents=True,exist_ok=True);native=a.out/'TI041.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
# Scalar GLB fallback is explicit; editable procedural graphs stay in the saved native.
for m in [leather,gold,lining,sole,thread]:
 bs=m.node_tree.nodes.get('Principled BSDF')
 for key in ['Base Color','Roughness','Normal']:
  for link in list(bs.inputs[key].links):m.node_tree.links.remove(link)
for o in list(s.objects):
 if o.type in ['CURVE','FONT']:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
bpy.ops.export_scene.gltf(filepath=str(a.out/'TI041.glb'),export_format='GLB',export_apply=True,export_animations=False,export_cameras=False,export_lights=False)
original=json.loads((source.parent/'refinement.json').read_text());original.update(refined_native_sha256=sha(native),glb_sha256=sha(a.out/'TI041.glb'),geometry_builder='sources/tools/trading-goods/refining/remodel_leather.py',geometry_builder_sha256=sha(Path(__file__)),prior_refined_native=source.relative_to(a.repo).as_posix(),prior_refined_native_sha256=source_hash,model_geometry='Rebuilt garment as continuous open-front fitted shell with thickness, lapels, bent hollow sleeves and shaped folds; boot calf shafts, rounded foot lasts, ankle creases, layered stitched soles; flat belt and shaped buckle; separately editable gold embroidery and saddle seams. Fine ornament is inferred, not traced.',materials=[dict(name=m.name,role=m.get('physical_surface_role','leather'),base_colour=list(m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value)) for m in [leather,gold,lining,sole,thread]])
(a.out/'refinement.json').write_text(json.dumps(original,indent=2)+'\n');assert sha(source)==source_hash
print('TI041_GEOMETRY_REBUILT',flush=True)
