"""Editable geometric vocabulary for coloured trade goods. No legacy bitmap textures."""
import bpy,math,random
from mathutils import Vector
ID='';COL=None

def begin(ident):
 global ID,COL
 bpy.ops.wm.read_factory_settings(use_empty=True);ID=ident;COL=bpy.context.scene.collection;bpy.context.scene.name=ident+' / coloured model';s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=480;s.render.resolution_y=360;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new(ident+' world');s.world.color=(.12,.12,.12);s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s['delivery']='coloured editable model; final images deferred';bpy.context.preferences.filepaths.save_version=0

def own(o,name,parent=None):
 o.name=ID+' / '+name
 if parent:o.parent=parent
 return o

def root(name,loc=(0,0,0)):
 o=bpy.data.objects.new(ID+' / '+name,None);COL.objects.link(o);o.location=loc;return o

def mat(name,c,metal=0,rough=.5,glass=0,emit=0):
 m=bpy.data.materials.new(ID+' / '+name);m.diffuse_color=(*c,1);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;b.inputs['Transmission Weight'].default_value=glass
 if emit:b.inputs['Emission Color'].default_value=(*c,1);b.inputs['Emission Strength'].default_value=emit
 t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=65;t.inputs['Detail'].default_value=3;bum=n.new('ShaderNodeBump');bum.inputs['Strength'].default_value=.12 if glass==0 else .035;bum.inputs['Distance'].default_value=.006;l.new(t.outputs['Fac'],bum.inputs['Height']);l.new(bum.outputs[0],b.inputs['Normal']);return m

def cube(name,loc,scale,material,parent=None,bevel=.025):
 bpy.ops.mesh.primitive_cube_add(size=2,location=loc);o=own(bpy.context.object,name,parent);o.scale=scale;o.data.materials.append(material)
 if bevel:q=o.modifiers.new('Small worn edges','BEVEL');q.width=bevel;q.segments=2
 return o

def ball(name,loc,scale,material,parent=None,sub=2):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=loc);o=own(bpy.context.object,name,parent);o.scale=scale;o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 return o

def lathe(name,profile,material,parent=None,segments=48):
 v=[];f=[]
 for r,z in profile:
  for i in range(segments):a=i*math.tau/segments;v.append((r*math.cos(a),r*math.sin(a),z))
 for j in range(len(profile)-1):
  for i in range(segments):a=j*segments+i;b=j*segments+(i+1)%segments;f.append((a,b,b+segments,a+segments))
 f.extend([tuple(range(segments-1,-1,-1)),tuple((len(profile)-1)*segments+i for i in range(segments))]);d=bpy.data.meshes.new(ID+' / '+name);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(ID+' / '+name,d);COL.objects.link(o);o.data.materials.append(material)
 if parent:o.parent=parent
 for p in d.polygons:p.use_smooth=True
 return o

def cylinder(name,loc,r,h,material,parent=None):
 o=lathe(name,[(r,0),(r,h)],material,parent);o.location=loc;return o

def ring(name,loc,r,thick,material,parent=None):
 bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=8,major_radius=r,minor_radius=thick,location=loc);o=own(bpy.context.object,name,parent);o.data.materials.append(material);return o

def rod(name,p,q,r,material,parent=None):
 p,q=Vector(p),Vector(q);o=cylinder(name,p,r,(q-p).length,material,parent);o.rotation_euler=(q-p).to_track_quat('Z','Y').to_euler();return o

def label(name,parent,r,z,w,h,material):
 # Curved paper/foil label: actual mesh following the vessel wall.
 v=[];f=[]
 for i in range(17):
  a=-math.pi/2+(i/16-.5)*w/r;x,y=(r+.008)*math.cos(a),(r+.008)*math.sin(a);v.extend([(x,y,z-h/2),(x,y,z+h/2)])
 for i in range(16):f.append((i*2,i*2+2,i*2+3,i*2+1))
 d=bpy.data.meshes.new(name);d.from_pydata(v,[],f);o=bpy.data.objects.new(ID+' / '+name,d);COL.objects.link(o);o.parent=parent;o.data.materials.append(material);return o

def bottle(name,loc,material,foil,labelmat=None,height=2.8,r=.38):
 o=root(name,loc);lathe('bottle body',[(r*.8,0),(r,.06),(r,height*.57),(r*.9,height*.66),(r*.25,height*.78),(r*.22,height*.97),(r*.28,height*.98),(r*.28,height),(r*.1,height)],material,o)
 cylinder('bottle neck foil',(0,0,height*.87),r*.24,height*.13,foil,o)
 if labelmat:label('curved bottle label',o,r,height*.38,r*1.6,height*.27,labelmat)
 return o

def text(name,body,loc,size,material,parent=None,rot=(math.pi/2,0,0)):
 d=bpy.data.curves.new(name,'FONT');d.body=body;d.align_x='CENTER';d.size=size;d.extrude=.001;o=bpy.data.objects.new(ID+' / '+name,d);COL.objects.link(o);o.location=loc;o.rotation_euler=rot;o.data.materials.append(material)
 if parent:o.parent=parent
 return o

def setup_camera():
 points=[o.matrix_world@Vector(v) for o in bpy.context.scene.objects if o.type in ['MESH','CURVE','FONT'] for v in o.bound_box];lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)));target=(lo+hi)/2;span=max(hi-lo);d=bpy.data.cameras.new(ID+' camera');o=bpy.data.objects.new(ID+' / inspection camera',d);COL.objects.link(o);o.location=target+Vector((.9,-1.6,1.0))*span;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';q=o.rotation_euler.to_quaternion().inverted();projected=[q@(p-target) for p in points];dx=max(p.x for p in projected)-min(p.x for p in projected);dy=max(p.y for p in projected)-min(p.y for p in projected);d.ortho_scale=max(dx,dy*480/360)*1.16;bpy.context.scene.camera=o
 for name,offset,power,color in [('key',(-2,-3,4),800,(1,.87,.72)),('fill',(3,-1,2),500,(.65,.8,1)),('rim',(0,3,4),900,(1,1,1))]:
  d=bpy.data.lights.new(name,'AREA');d.energy=power*max(1,span*.5);d.shape='DISK';d.size=span*1.5;ob=bpy.data.objects.new(ID+' / '+name,d);COL.objects.link(ob);ob.location=target+Vector(offset)*span;ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
 return o

def mesh(name,verts,faces,material,parent=None):
 d=bpy.data.meshes.new(ID+' / '+name);d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(ID+' / '+name,d);COL.objects.link(o);o.data.materials.append(material)
 if parent:o.parent=parent
 return o

def polyline(name,points,r,material,parent=None):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.bevel_depth=r;d.bevel_resolution=2;sp=d.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(ID+' / '+name,d);COL.objects.link(o);o.data.materials.append(material)
 if parent:o.parent=parent
 return o
