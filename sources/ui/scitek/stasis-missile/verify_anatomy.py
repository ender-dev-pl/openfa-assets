"""Six physical pods, four fins, unchanged casing profile and open main bell."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
def points(name):
 ob=bpy.data.objects[name];mapping=bpy.data.objects['StasisMissileRoot'].matrix_world.inverted()@ob.matrix_world;return [mapping@v.co for v in ob.data.vertices]
def tree(name):
 ob=bpy.data.objects[name];return BVHTree.FromPolygons(points(name),[list(p.vertices) for p in ob.data.polygons])
def check(imported=False):
 pods=[f'Tachyon dispersion pod {i+1}' for i in range(6)];fins=[f'Guidance fin {i+1}' for i in range(4)];centres=[]
 for name in pods:
  ps=points(name);centre=Vector([(min(v[k] for v in ps)+max(v[k] for v in ps))/2 for k in range(3)]);assert abs(centre.xy.length-.47)<1e-5 and abs(centre.z-1.35)<1e-5;centres.append(centre)
  spans=[max(v[k] for v in ps)-min(v[k] for v in ps) for k in range(3)];assert max(abs(a-b) for a,b in zip(spans,[.38,.38,.40]))<1e-5
 for i in range(6):
  assert abs((centres[i]-centres[(i+1)%6]).length-.47)<1e-5
  for j in range(i):assert not tree(pods[i]).overlap(tree(pods[j]))
 bell=tree('Stasis hollow red propulsion bell');assert bell.ray_cast(Vector((0,0,-.5)),Vector((0,0,1)))[0] is None
 hit=tree('Stasis recessed throat').ray_cast(Vector((0,0,-.5)),Vector((0,0,1)))[0];assert hit is not None and .94<hit.z<.98
 for i,name in enumerate(fins):
  assert not tree(name).overlap(bell),('fin intersects bell',name)
  for other in fins[:i]:assert not tree(name).overlap(tree(other))
 casing=points('Stasis straight green pressure casing');rings=sorted({round(v.z,5) for v in casing});assert any(abs(z-4.22)<1e-5 for z in rings)
 maximum=0
 for v in casing:
  if imported:
   # Runtime exports include the existing end-edge bevel. Compare them to the
   # actual evaluated native surface, not to the unbevelled authoring profile.
   distance=casing_surface.find_nearest(v)[3];assert distance<2e-5,distance;maximum=max(maximum,distance)
  else:
   expected=.5192+(v.z-1.04)/.11*(.5428-.5192) if v.z<1.15 else .5428
   assert abs(v.xy.length-expected)<2e-5,(list(v),expected)
 return dict(physical_pods=6,pod_adjacent_centre_distance=.47,guidance_fins=4,no_fin_bell_or_interpod_intersections=True,bell_central_ray_clear=True,recessed_throat_z=hit.z,casing_profile_preserved=True,casing_joint_ring=4.22,imported_casing_to_evaluated_native_surface_max_distance=maximum)
bpy.ops.wm.open_mainfile(filepath=str(out/'stasis-missile.blend'));bpy.context.scene.frame_set(1);native=check()
ob=bpy.data.objects['Stasis straight green pressure casing'].evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ob.to_mesh();mapping=bpy.data.objects['StasisMissileRoot'].matrix_world.inverted()@ob.matrix_world;casing_surface=BVHTree.FromPolygons([mapping@v.co for v in mesh.vertices],[list(p.vertices) for p in mesh.polygons]);ob.to_mesh_clear()
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=15;bpy.ops.import_scene.gltf(filepath=str(out/'stasis-missile.glb'));bpy.context.scene.frame_set(1);bpy.context.view_layer.update();imported=check(True)
(out/'anatomy-verification.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256((out/'stasis-missile.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((out/'stasis-missile.glb').read_bytes()).hexdigest(),verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),native=native,independent_import=imported),indent=2)+'\n',encoding='utf-8');print('STASIS_ANATOMY_VERIFIED')
