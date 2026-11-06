"""PB28/ST27 shared solar matrix: all technical edges derive from this solid."""
import sys,math,json,hashlib,bpy,bmesh
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from export_solid import export_solid
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
base=Path(sys.argv[sys.argv.index('--')+2]).resolve()
digest=hashlib.sha256(base.read_bytes()).hexdigest()
assert digest=='dfee4f7a2e39f6493b4fdfe26ef917b981356c8d983d681a55febfea4cf5c1f4'
s=bpy.context.scene;s.cycles.samples=16
root=bpy.data.objects.new('SolarMatrixRoot',None);s.collection.objects.link(root)
roles=['chassis','solar-panels','storage-cells','laser-turret'];parts={r:[] for r in roles}
alloy=g.material('Research used matrix alloy',(.16,.19,.105),.40,.67)
purple=g.material('Research weathered violet matrix panels',(.09,.055,.15),.25,.68)
dark=g.material('Research recessed matrix joints',(.035,.033,.035),.25,.72)
edge=g.material('Research worn green cell ribs',(.19,.23,.09),.40,.62)
for mat in [alloy,purple,dark,edge]:
 for node in mat.node_tree.nodes:
  if node.type=='BUMP':node.inputs['Distance'].default_value=.001;node.inputs['Strength'].default_value=.14
  if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=90

def add(ob,role):
 ob.parent=root;parts[role].append(ob);return ob

def lathe(name,zr,material,role,xy=(0,0),segments=32):
 vs=[(xy[0]+r*math.cos(i*math.tau/segments),xy[1]+r*math.sin(i*math.tau/segments),z) for z,r in zr for i in range(segments)]
 fs=[tuple(reversed(range(segments)))]
 for j in range(len(zr)-1):
  for i in range(segments):
   a=j*segments+i;b=j*segments+(i+1)%segments;fs.append((a,b,b+segments,a+segments))
 fs.append(tuple((len(zr)-1)*segments+i for i in range(segments)))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update();ob=bpy.data.objects.new(name,mesh);s.collection.objects.link(ob);ob.data.materials.append(material);return add(ob,role)

lathe('Hexagonal equipment foundation',[(0,.38),(.035,.40),(.48,.40),(.52,.35)],purple,'chassis',segments=6)
lathe('Foundation upper gasket',[(.48,.35),(.51,.36),(.53,.36)],dark,'chassis',segments=6)
for i in range(3):
 a=-math.pi/2+i*math.tau/3;xy=(.22*math.cos(a),.22*math.sin(a))
 lathe(f'Storage cell {i+1} core',[(.5,.112),(2.32,.112)],alloy,'storage-cells',xy)
 for j in range(23):
  z=.55+j*.075
  lathe(f'Storage cell {i+1} rib {j+1:02}',[(z,.112),(z+.012,.135),(z+.032,.135),(z+.044,.112)],edge,'storage-cells',xy)
 lathe(f'Storage cell {i+1} upper cap',[(2.25,.135),(2.31,.135),(2.35,.10)],alloy,'storage-cells',xy)
# The side-view wire resolves a broad lower cone, narrow waist and flared cup.
lathe('Faceted central load-bearing pedestal',[(2.25,.36),(2.37,.36),(2.96,.19),(3.27,.34)],alloy,'chassis',segments=8)
add(g.box('Square panel hub platform',(0,0,3.265),(.70,.70,.035),alloy,.008),'solar-panels')
for k in range(4):
 a=k*math.pi/2;co,si=math.cos(a),math.sin(a)
 # PB28 frame8 resolves trapezoids: wide at hub, narrower at the outer ends.
 local=[(.34,-.33,3.28),(.84,-.14,3.03),(.84,.14,3.03),(.34,.33,3.28)]
 vs=[(x*co-y*si,x*si+y*co,z+dz) for dz in [-.025,0] for x,y,z in local]
 fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 mesh=bpy.data.meshes.new('Collector wing');mesh.from_pydata(vs,[],fs);mesh.update();ob=bpy.data.objects.new(f'Splayed collector panel {k+1}',mesh);s.collection.objects.link(ob);ob.data.materials.append(purple);add(ob,'solar-panels')
 # Fine cell seams follow the same sloped surface without changing its silhouette.
 for j in range(1,5):
  x=.34+j*.10;z=3.28-(x-.34)*.5+.002;half_width=.33-(x-.34)*.38-.01
  add(g.tube(f'Collector wing {k+1} cell seam {j}',(x*co+half_width*si,x*si-half_width*co,z),(x*co-half_width*si,x*si+half_width*co,z),.0018,dark),'solar-panels')
# Low hemispherical turret cap and short tapering angled laser seen in ST27.
lathe('Integrated turret underbody',[(3.13,.015),(3.16,.10),(3.23,.16),(3.28,.16)],alloy,'laser-turret')
lathe('Integrated turret dome',[(3.28,.30),(3.31,.29),(3.36,.25),(3.40,.18),(3.425,.07),(3.43,.008)],alloy,'laser-turret',segments=40)
add(g.tube('Laser tapered emitter',(0,0,3.40),(-.10,-.035,3.67),.073,alloy,.027),'laser-turret')
add(g.tube('Laser dark aperture',(-.10,-.035,3.67),(-.105,-.037,3.683),.021,dark),'laser-turret')
meshes=[ob for obs in parts.values() for ob in obs]
hinges=[];closed_delta=math.acos((.15-.34)/math.hypot(.5,.25))+math.atan2(.25,.5)
for k in range(4):
 a=k*math.pi/2;hinge=bpy.data.objects.new(f'Collector hinge {k+1}',None);s.collection.objects.link(hinge);hinge.parent=root;hinge.location=(.34*math.cos(a),.34*math.sin(a),3.28);hinge.rotation_euler.z=a
 bpy.context.view_layer.update()
 for ob in parts['solar-panels']:
  if ob.name==f'Splayed collector panel {k+1}' or ob.name.startswith(f'Collector wing {k+1} cell seam '):
   world=ob.matrix_world.copy();ob.parent=hinge;ob.matrix_world=world
 hinges.append(hinge)
 for clip,angles in [('PanelsClose',(0,-closed_delta)),('PanelsOpen',(-closed_delta,0))]:
  hinge.animation_data_create();action=bpy.data.actions.new(f'{clip} hinge{k+1}');hinge.animation_data.action=action
  for frame,angle in zip([1,31],angles):hinge.rotation_euler.y=angle;hinge.keyframe_insert(data_path='rotation_euler',frame=frame)
  for fc in action.fcurves:
   for key in fc.keyframe_points:key.interpolation='BEZIER'
  track=hinge.animation_data.nla_tracks.new();track.name=clip;track.strips.new(clip,1,action);track.mute=True
  hinge.animation_data.action=None
 hinge.rotation_euler.y=0
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
mat=bpy.data.materials.new('Technical green');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,.72,.005,1);output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],output.inputs[0])
wire_nodes={}
for role,role_obs in parts.items():
 wire_nodes[role]=[]
 for parent in dict.fromkeys(ob.parent for ob in role_obs):
  obs=[ob for ob in role_obs if ob.parent==parent]
  wire_name=role+('' if parent==root else ' '+parent.name)+' technical wire'
  wire_nodes[role].append(wire_name)
  inverse=parent.matrix_world.inverted()
  curve=bpy.data.curves.new(role+' technical wire','CURVE');curve.dimensions='3D';curve.bevel_depth=.0015;curve.bevel_resolution=0
  for ob in obs:
   ev=ob.evaluated_get(deps);mesh=ev.to_mesh();bm=bmesh.new();bm.from_mesh(mesh);bm.normal_update()
   for e in bm.edges:
    if e.calc_length()<.008:continue
    if len(e.link_faces)==2 and e.calc_face_angle(0)<.012:continue
    a,b=[inverse@ob.matrix_world@v.co for v in e.verts];sp=curve.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*a,1);sp.points[1].co=(*b,1)
   bm.free();ev.to_mesh_clear()
  ob=bpy.data.objects.new(wire_name,curve);s.collection.objects.link(ob);ob.parent=parent;ob.data.materials.append(mat);ob.hide_render=True
root.rotation_mode='XYZ';s.frame_start=1;s.frame_end=61;s.render.fps=15
for f in [1,16,31,46,61]:root.rotation_euler.z=-(f-1)*math.tau/60;root.keyframe_insert(data_path='rotation_euler',frame=f)
for fc in root.animation_data.action.fcurves:
 for key in fc.keyframe_points:key.interpolation='LINEAR'
root.animation_data.action.name='CatalogueTurn'
track=root.animation_data.nla_tracks.new();track.name='CatalogueTurn';track.strips.new('CatalogueTurn',1,root.animation_data.action);track.mute=True
s.frame_set(1);s.render.resolution_x=480;s.render.resolution_y=480;s.render.film_transparent=True
bpy.ops.object.camera_add(location=(5,-9,5));s.camera=bpy.context.object;target=Vector((0,0,1.80));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=4.3
for loc,power,size in [((3,-4,7),350,5),((-4,-2,4),200,4),((1,4,6),350,4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'solar-matrix.blend'))
# Render before NLA export samples the opening and closing actions.
s.render.filepath=str(out/'solid.png');bpy.ops.render.render(write_still=True)
export_solid(root,meshes,out/'solar-matrix.glb')
phases=[dict(component=r,first_legacy_frame=29+i*141,last_legacy_frame=139+i*141,local_target=t,closeup_rotation_euler=[0,0,0],ortho_scale=scale) for i,(r,t,scale) in enumerate(zip(roles[1:],[[0,0,3.20],[0,0,1.40],[0,0,3.40]],[1.9,2.3,.90]))]
d=dict(id='scitek:solar-matrix',object_id='terran:solar-matrix',legacy_index=27,components={k:[o.name for o in obs] for k,obs in parts.items()},phases=phases,whole_information_local_target=[0,0,1.8],whole_information_rotation_euler=[.08,0,.35],whole_information_ortho_scale=4.5,information_timeline_frames=423,base_source_sha256=digest,shared_root_scale=[1,1,1],limitations=['Authored replacement geometry based on actual PB28 colour and ST27 wire closeups. Exact dimensions, hidden anatomy and camera interpolation remain interpretations; client mounting/footprint requires validation. No pixel-exact claim.'])
d['technical_wires']=wire_nodes
d['articulation']=dict(hinges=[o.name for o in hinges],clips=['CatalogueTurn','PanelsClose','PanelsOpen'],panel_closed_delta_degrees=math.degrees(closed_delta),closed_shape='Nearly closed truncated square pyramid, open at the top; nominal side-edge gaps .02 model units.',operating_state_binding='User-authorized optional extension beyond observed legacy behaviour. May be bound to shutdown by the client; this binding is not a recovered legacy rule.')
(out/'model.json').write_text(json.dumps(d,indent=2)+'\n');print('SOLAR_MATRIX_READY',len(meshes))
