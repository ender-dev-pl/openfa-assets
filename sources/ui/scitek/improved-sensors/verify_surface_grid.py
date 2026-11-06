"""Verify display tessellation against the physical casing profile, without edits."""
import bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector,kdtree
source,out=map(lambda p:Path(p).resolve(),sys.argv[sys.argv.index('--')+1:]);out.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();root=bpy.data.objects['SensorsRotor'];inverse=root.matrix_world.inverted();meta=json.loads((source.parent/'model.json').read_text());edges=[]
for name in meta['components']['chassis']:
 ob=bpy.data.objects[name];matrix=inverse@ob.matrix_world
 edges.extend(tuple(matrix@ob.data.vertices[i].co for i in edge.vertices) for edge in ob.data.edges)
tree=kdtree.KDTree(len(edges))
for i,(a,b) in enumerate(edges):tree.insert((a+b)*.5,i)
tree.balance();wire=bpy.data.objects['chassis technical wire'];grid=[];exact=0
for sp in wire.data.splines:
 assert sp.type=='POLY' and len(sp.points)==2;a,b=[inverse@wire.matrix_world@Vector(p.co[:3]) for p in sp.points];matches=[]
 for _,i,_ in tree.find_range((a+b)*.5,2e-5):
  c,d=edges[i];matches.append(min(max((a-c).length,(b-d).length),max((a-d).length,(b-c).length)))
 if matches and min(matches)<2e-5:exact+=1
 else:grid.append((a,b))
assert exact==168 and len(grid)==11
case=bpy.data.objects['Arched sensor casing panel 0'];matrix=inverse@case.matrix_world;verts=[matrix@v.co for v in case.data.vertices];front=min(v.y for v in verts);outline=[(v.x,v.z) for v in verts if abs(v.y-front)<1e-6];assert len(outline)==12
# Actual source polygon, not a separately retyped approximation of the profile.
def on_segment(p,a,b):
 v=Vector((b[0]-a[0],b[1]-a[1]));w=Vector((p[0]-a[0],p[1]-a[1]));return abs(v.x*w.y-v.y*w.x)<2e-6 and -1e-6<=w.dot(v)<=v.length_squared+1e-6
def inside(p):
 if any(on_segment(p,a,b) for a,b in zip(outline,outline[1:]+outline[:1])):return True
 hit=False
 for a,b in zip(outline,outline[1:]+outline[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
samples=[]
for a,b in grid:
 assert abs(a.y-b.y)<1e-6 and abs(a.y-front+.015)<1e-6
 # Include every profile-height intersection, in addition to uniform samples.
 parameters={i/100 for i in range(101)}
 if abs(b.z-a.z)>1e-8:parameters.update((z-a.z)/(b.z-a.z) for x,z in outline if 0<=(z-a.z)/(b.z-a.z)<=1)
 for t in sorted(parameters):
  p=a.lerp(b,t);assert inside((p.x,p.z)),(list(p),'outside raw casing profile');samples.append(list(p))
report=dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),chassis_segments=179,exact_raw_skeleton_segments=168,display_tessellation_segments=11,physical_surface='Arched sensor casing panel 0 front polygon',profile_vertices=outline,front_plane_y=front,display_plane_offset=.015,projected_samples_inside_actual_profile=len(samples),all_projected_grid_samples_inside=True,physical_geometry_changed=False,interpretation='Eleven lines are display tessellation on the same physical front face, offset0.015 to avoid overlap; not extra hardware or a different casing silhouette. Evaluated bevels round the profile boundary, explaining small BVH offsets.',limitations=['This validates source geometry correspondence, not recovered legacy mesh topology or pixel fidelity.'])
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('SENSORS_SURFACE_GRID_VERIFIED',len(samples))
