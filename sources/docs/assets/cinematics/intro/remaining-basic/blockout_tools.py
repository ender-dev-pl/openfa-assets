"""Small editable modelling vocabulary for the basic pass; no reference pixels used as textures."""
import bpy,math,random
from mathutils import Vector
SCENE=None;PREFIX='';COL=None

def begin(info):
 global SCENE,PREFIX,COL
 bpy.ops.wm.read_factory_settings(use_empty=True);SCENE=bpy.context.scene;PREFIX=info['id'];SCENE.name=PREFIX+' — '+info['name'];SCENE.frame_start=info['frame_start'];SCENE.frame_end=info['frame_end'];SCENE.render.engine='CYCLES';SCENE.cycles.samples=8;SCENE.cycles.use_denoising=True;SCENE.cycles.use_adaptive_sampling=True;SCENE.cycles.adaptive_threshold=.15;SCENE.cycles.adaptive_min_samples=4;SCENE.render.fps=24;SCENE.render.resolution_x=640;SCENE.render.resolution_y=262;SCENE.render.resolution_percentage=100;SCENE.render.image_settings.file_format='PNG';SCENE.render.filepath='//renders/frame-';SCENE.view_settings.view_transform='AgX';SCENE.view_settings.look='AgX - Medium High Contrast';SCENE.world=bpy.data.worlds.new(PREFIX+' / world');SCENE.world.use_nodes=True;SCENE.world.node_tree.nodes['Background'].inputs[0].default_value=(.003,.004,.007,1);SCENE.world.node_tree.nodes['Background'].inputs[1].default_value=.15;SCENE['quality']='basic blockout; refining deferred';SCENE['source_range']=[info['source_start'],info['source_end']];COL=bpy.data.collections.new(PREFIX+' / editable basic geometry');SCENE.collection.children.link(COL)
 return SCENE

def own(o,name,parent=None):
 for c in list(o.users_collection):c.objects.unlink(o)
 COL.objects.link(o);o.name=PREFIX+' / '+name
 if parent:o.parent=parent
 return o

def empty(name,loc=(0,0,0),parent=None):
 o=bpy.data.objects.new(PREFIX+' / '+name,None);COL.objects.link(o);o.location=loc
 if parent:o.parent=parent
 return o

def material(name,color,metal=0,rough=.65,worn=True,emit=0):
 m=bpy.data.materials.new(PREFIX+' / '+name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 if emit:bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=emit
 if worn:
  tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=19;tex.inputs['Detail'].default_value=2;bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.012;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
 return m

def cube(name,loc,scale,mat,parent=None,bevel=.035):
 bpy.ops.mesh.primitive_cube_add(size=2);o=own(bpy.context.object,name,parent);o.location=loc;o.scale=scale
 if mat:o.data.materials.append(mat)
 if bevel:q=o.modifiers.new('Basic worn edge','BEVEL');q.width=bevel;q.segments=1
 return o

def ball(name,loc,scale,mat,parent=None,sub=2):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1);o=own(bpy.context.object,name,parent);o.location=loc;o.scale=scale;o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o

def tube(name,a,b,r,mat,parent=None,vertices=12):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=(b-a).length);o=own(bpy.context.object,name,parent);o.location=(a+b)*.5;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o

def torus(name,loc,major,minor,mat,parent=None,vertical=False):
 bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=6,major_radius=major,minor_radius=minor);o=own(bpy.context.object,name,parent);o.location=loc;o.data.materials.append(mat)
 if vertical:o.rotation_euler.x=math.pi/2
 return o

def polygon(name,verts,faces,mat,parent=None):
 d=bpy.data.meshes.new(PREFIX+' / '+name);d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(PREFIX+' / '+name,d);COL.objects.link(o);o.data.materials.append(mat)
 if parent:o.parent=parent
 return o

def panel(name,loc,w,h,mat,parent=None):
 x,y,z=loc;return polygon(name,[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2)],[(0,1,2,3)],mat,parent)

def camera(loc=(0,-12,4.5),target=(0,0,3),lens=45,ortho=None):
 d=bpy.data.cameras.new(PREFIX+' camera');d.lens=lens;d.sensor_fit='HORIZONTAL';d.clip_end=1800;o=bpy.data.objects.new(PREFIX+' / camera',d);COL.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 SCENE.camera=o;bpy.context.view_layer.update();return o

def light(name,loc,energy=700,color=(.75,.85,1),size=5,target=(0,0,3)):
 d=bpy.data.lights.new(PREFIX+' '+name,'AREA');d.energy=energy;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(PREFIX+' / '+name,d);COL.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o

def key(o,prop,n,value):
 setattr(o,prop,value);o.keyframe_insert(prop,frame=2*n+1)
 if o.animation_data:
  for fc in o.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'

def caption(text):
 d=bpy.data.curves.new(PREFIX+' caption','FONT');d.body=text;d.align_x='CENTER';d.size=.145;d.space_character=1.15;o=bpy.data.objects.new(PREFIX+' / caption',d);COL.objects.link(o);o.parent=SCENE.camera;o.location=(0,-1.17,-8);d.materials.append(material('caption white',(.85,.85,.85),worn=False,emit=1));return o

def background(kind='space'):
 palette={'space':[(.001,.002,.004),(.004,.012,.04),(.035,.006,.04),(.006,.045,.035)],'red':[(.002,.001,.003),(.03,.008,.014),(.13,.035,.045),(.012,.008,.012)],'sky':[(.025,.018,.03),(.13,.09,.105),(.27,.20,.18),(.065,.055,.075)]}[kind]
 m=material('procedural '+kind,palette[0],worn=False);n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF');tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3;tex.inputs['Detail'].default_value=3;r=n.new('ShaderNodeValToRGB')
 for j,color in enumerate(palette):
  e=r.color_ramp.elements[j] if j<2 else r.color_ramp.elements.new(j/3);e.position=j/3;e.color=(*color,1)
 l.new(tex.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],bs.inputs['Base Color']);l.new(r.outputs[0],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.7;return panel('procedural background',(0,7,4),35,17,m)

def stars(seed=7):
 rnd=random.Random(seed);m=material('stars',(.4,.5,.65),worn=False,emit=2);v=[];f=[]
 for i in range(180):
  x,z=rnd.uniform(-48,48),rnd.uniform(-14,24);r=rnd.uniform(.025,.10);k=len(v);v.extend([(x-r,100,z-r),(x+r,100,z-r),(x+r,100,z+r),(x-r,100,z+r)]);f.append((k,k+1,k+2,k+3))
 return polygon('star field',v,f,m)

def human(name='actor',loc=(0,0,0),scale=1,uniform=(.055,.085,.065),skin=(.33,.24,.19),hair=None,bronze=False,cape=None,hat=False):
 root=empty(name,loc);root.scale=(scale,)*3;cloth=material(name+' uniform',uniform,.08,.8);flesh=material(name+' skin',skin,.75 if bronze else 0,.4 if bronze else .7,worn=bronze);black=material(name+' dark',(.009,.012,.014),worn=False);white=material(name+' eyes',(.065,.075,.075),worn=False);metal=material(name+' trim',(.38,.23,.065),.65,.45)
 ball(name+' torso',(0,0,3.2),(1.0,.48,1.2),cloth,root);cube(name+' shoulders',(0,0,4.0),(1.14,.42,.24),cloth,root,.1);tube(name+' neck',(0,0,4),(0,0,4.65),.23,flesh,root)
 head=empty(name+' head',(0,0,5.15),root);ball(name+' skull',(0,0,0),(.64,.48,.85),flesh,head);ball(name+' cheek L',(-.28,-.22,-.22),(.30,.28,.34),flesh,head);ball(name+' cheek R',(.28,-.22,-.22),(.30,.28,.34),flesh,head)
 jaw=empty(name+' jaw',(0,-.05,-.40),head);ball(name+' lower jaw',(0,-.11,-.11),(.41,.32,.22),flesh,jaw);cube(name+' mouth cavity',(0,-.468,-.34),(.22,.018,.055),black,head,.01)
 polygon(name+' nose',[(-.13,-.40,.25),(.13,-.40,.25),(.13,-.43,-.18),(-.13,-.43,-.18),(0,-.76,-.10)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(0,3,2,1)],flesh,head)
 for side in [-1,1]:
  ball(name+' ear '+str(side),(side*.64,.02,-.02),(.11,.14,.22),flesh,head);ball(name+' eye '+str(side),(side*.235,-.454,.14),(.105,.025,.065),white,head);ball(name+' pupil '+str(side),(side*.235,-.485,.14),(.035,.012,.043),black,head);cube(name+' brow '+str(side),(side*.23,-.46,.29),(.17,.045,.035),flesh if hair is None else black,head,.01)
 if hair is not None:ball(name+' basic hair',(0,.07,.58),(.68,.49,.37),material(name+' hair',hair,worn=False),head)
 arms=[];legs=[]
 for side in [-1,1]:
  arm=empty(name+' arm '+str(side),(side*1.05,0,3.9),root);arms.append(arm);tube(name+' upper sleeve '+str(side),(0,0,0),(side*.3,0,-.85),.25,cloth,arm);tube(name+' forearm '+str(side),(side*.3,0,-.85),(side*.36,-.10,-1.62),.19,cloth,arm);ball(name+' hand '+str(side),(side*.36,-.10,-1.78),(.18,.14,.27),flesh,arm)
  leg=empty(name+' leg '+str(side),(side*.46,0,2.2),root);legs.append(leg);tube(name+' thigh '+str(side),(0,0,0),(0,0,-1.0),.27,cloth,leg);tube(name+' shin '+str(side),(0,0,-1.0),(0,0,-2),.21,cloth,leg);cube(name+' boot '+str(side),(0,-.16,-2.09),(.23,.40,.16),black,leg,.06)
 if cape:
  c=material(name+' mantle',cape,.05,.85);polygon(name+' cape',[(-1.15,.15,4.12),(1.15,.15,4.12),(1.5,.65,1.25),(-1.5,.65,1.25)],[(0,1,2,3)],c,root)
 torus(name+' chest medal',(0,-.5,3.65),.15,.04,metal,root,True)
 if hat:
  purple=material(name+' bicorn',(.045,.012,.075),.2,.7);polygon(name+' bicorn',[(-1.15,0,.78),(-.65,0,1.68),(0,0,1.15),(.65,0,1.68),(1.15,0,.78),(0,-.28,.80)],[(0,1,2,3,4,5)],purple,head);tube(name+' hat braid',(-1.1,-.02,.82),(1.1,-.02,.82),.035,metal,head)
 return dict(root=root,head=head,jaw=jaw,arms=arms,legs=legs,skin=flesh,cloth=cloth)

def talk(actor,a,b):
 for n in range(a,b+1,2):key(actor['jaw'],'rotation_euler',n,(.04+.15*(.5+.5*math.sin(n*1.71)),0,0))

def curtains(color=(.055,.006,.09)):
 m=material('curtain velvet',color,rough=.95);v=[];f=[]
 for i in range(81):
  x=-8+i*.2;y=3.8+.18*math.cos(i*.9);v.extend([(x,y,-1),(x,y,9)])
 for i in range(80):f.append((2*i,2*i+1,2*i+3,2*i+2))
 return polygon('curtain folds',v,f,m)

def signal(info,under=None):
 camera((0,-10,3),(0,0,3));m=material('generated interference',(.02,.02,.02),worn=False);n=m.node_tree.nodes;l=m.node_tree.links;bs=n.get('Principled BSDF');tex=n.new('ShaderNodeTexWhiteNoise');tex.noise_dimensions='4D';uv=n.new('ShaderNodeTexCoord');mul=n.new('ShaderNodeVectorMath');mul.operation='SCALE';mul.inputs[3].default_value=380;l.new(uv.outputs['Generated'],mul.inputs[0]);floor=n.new('ShaderNodeVectorMath');floor.operation='FLOOR';l.new(mul.outputs[0],floor.inputs[0]);l.new(floor.outputs[0],tex.inputs['Vector']);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.62;r.color_ramp.elements[0].color=(.001,.002,.004,1);r.color_ramp.elements[1].position=.91;r.color_ramp.elements[1].color=(.7,.65,.56,1);l.new(tex.outputs['Value'],r.inputs[0]);l.new(r.outputs[0],bs.inputs['Base Color']);l.new(r.outputs[0],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.8
 for f,w in [(info['frame_start'],0),(info['frame_end'],400)]:tex.inputs['W'].default_value=w;tex.inputs['W'].keyframe_insert('default_value',frame=f)
 panel('interference plane',(0,3,3),18,8,m);label=caption('Transmission Interrupted');label.data.size=.36;label.scale.y=262/560;SCENE.cycles.use_denoising=False;SCENE['preserve_signal_noise']=True

def apply_black_samples(info):
 if not info['black_samples']:return
 SCENE.use_nodes=True;n=SCENE.node_tree.nodes;l=SCENE.node_tree.links;rl=n.get('Render Layers');out=n.get('Composite');mix=n.new('CompositorNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;l.new(rl.outputs['Image'],mix.inputs[1]);l.new(mix.outputs[0],out.inputs['Image']);sock=mix.inputs[2];sock.default_value=(1,1,1,1);sock.keyframe_insert('default_value',frame=info['frame_start'])
 for original in info['black_samples']:
  for f,v in [(2*original,1),(2*original+1,0),(2*original+2,0),(2*original+3,1)]:sock.default_value=(v,v,v,1);sock.keyframe_insert('default_value',frame=f)
 for fc in SCENE.node_tree.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
