import bpy,bmesh,sys,json
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(out/'mega-missile.blend'));model=json.loads((out/'model.json').read_text());new=[bpy.data.objects[n] for n in model['new_presentation_meshes']];assert len(new)==8;pods=[o for o in new if o.name.startswith('Research directional thrust chamber ')];assert len(pods)==4
volumes={}
for ob in new:
 bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),ob.name;v=bm.calc_volume(signed=True);assert v>0,(ob.name,v);volumes[ob.name]=v;bm.free()
def inside(ob,p):
 inv=ob.matrix_world.inverted();start=inv@Vector(p);direction=Vector((1,.137,.293)).normalized();hits=0
 for _ in range(100):
  ok,point,normal,index=ob.ray_cast(start,direction)
  if not ok:return hits%2==1
  hits+=1;start=point+direction*1e-5
 raise AssertionError('Ray did not terminate')
checks=[]
for ob in pods:
 p=(ob.location.x,ob.location.y,.70);assert inside(ob,p) and inside(bpy.data.objects['Mega cylindrical pressure casing'],p);checks.append(dict(chamber=ob.name,shared_casing_point=p))
for a,b in [(pods[0],pods[2]),(pods[1],pods[3])]:assert (a.location+b.location-Vector((0,0,.90))).length<1e-5
(out/'research-additions-verification.json').write_text(json.dumps(dict(closed_positive_added_meshes=volumes,directional_thrust_chambers=4,opposing_pairs_verified=True,shared_casing_witnesses=checks,limitations=['Scoped interior attachment witnesses; chamber shapes and hidden construction are authored approximations.']),indent=2)+'\n',encoding='utf-8');print('MEGA_ADDITIONS_VERIFIED',len(new),len(checks))
