import bpy,bmesh,sys,json
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(out/'nuclear-missile.blend'));s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();model=json.loads((out/'model.json').read_text());new=[bpy.data.objects[n] for n in model['new_presentation_meshes']];assert len(new)==2
pods=[o for o in s.objects if o.name.startswith('Nuclear swept red tail pod')];front=[o for o in s.objects if o.name.startswith('Nuclear upper silver side form')];assert len(pods)==4 and len(front)==2
volumes={}
for ob in new:
 data=bpy.data.meshes.new_from_object(ob.evaluated_get(deps));bm=bmesh.new();bm.from_mesh(data);assert all(e.is_manifold for e in bm.edges);v=bm.calc_volume(signed=True);assert v>0;volumes[ob.name]=v;bm.free();bpy.data.meshes.remove(data)
 mat=ob.data.materials[0];assert any(n.type=='TEX_NOISE' for n in mat.node_tree.nodes) and any(n.type=='BUMP' for n in mat.node_tree.nodes)
def inside(ob,p):
 ob=ob.evaluated_get(deps);start=ob.matrix_world.inverted()@Vector(p);direction=Vector((1,.137,.293)).normalized();hits=0
 for _ in range(100):
  ok,point,normal,index=ob.ray_cast(start,direction)
  if not ok:return hits%2==1
  hits+=1;start=point+direction*1e-5
 raise AssertionError('Ray did not terminate')
checks=[]
for ob in new:
 direction=ob.matrix_basis.to_3x3()@Vector((0,1,0));p=direction*.37+Vector((0,0,4.70));assert inside(ob,p) and inside(bpy.data.objects['Nuclear tapered dark pressure casing'],p);checks.append(dict(airbrake=ob.name,shared_casing_point=list(p)))
(out/'research-additions-verification.json').write_text(json.dumps(dict(closed_positive_rear_forms=volumes,delivery_thrusters=4,original_front_forms=2,new_rear_forms=2,total_manoeuvring_forms=4,material_grain_grime_bump_present=True,shared_casing_witnesses=checks,limitations=['Scoped containment witnesses; rear placement and physical construction are authored approximations of the observed layout.']),indent=2)+'\n',encoding='utf-8');print('NUCLEAR_ADDITIONS_VERIFIED')
