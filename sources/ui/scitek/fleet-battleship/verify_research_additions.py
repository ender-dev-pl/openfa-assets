import bpy,bmesh,sys,json
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(out/'fleet-battleship.blend'));model=json.loads((out/'model.json').read_text());new=[bpy.data.objects[n] for n in model['new_presentation_meshes']];assert len(new)==10
volumes={}
for ob in new:
 bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),ob.name;v=bm.calc_volume(signed=True);assert v>0,(ob.name,v);volumes[ob.name]=v;bm.free()
def inside(name,p):
 ob=bpy.data.objects[name];inv=ob.matrix_world.inverted();start=inv@Vector(p);direction=Vector((1,.137,.293)).normalized();hits=0
 for _ in range(100):
  ok,point,normal,index=ob.ray_cast(start,direction)
  if not ok:return hits%2==1
  hits+=1;start=point+direction*1e-5
 raise AssertionError('Too many intersections')
probes=[('Fleet Battleship long central hull',(0,-2.25,-.08)),('Research field sensor mount',(0,-2.25,-.08)),('Research field sensor housing',(0,-2.50,-.23)),('Research field sensor mount',(0,-2.50,-.23)),('Research field sensor housing',(0,-2.76,-.23)),('Research field sensor probe',(0,-2.76,-.23)),('Research field sensor probe',(0,-3.10,-.23)),('Research field sensor probe bulb',(0,-3.10,-.23))]
for side in [-1,1]:
 probes.extend([('Fleet Battleship tip fairing '+str(side),(side*2.35,-.47,.225)),('Research wingtip housing '+str(side),(side*2.35,-.47,.225))])
# Endpoint caps are boundary surfaces. Test infinitesimally inside each finite tube.
probes=[(n,(p[0],p[1]-.0001,p[2]-.0001)) if n=='Research field sensor mount' and p[1]==-2.25 else (n,(p[0],p[1]+.0001,p[2]+.0001)) if n=='Research field sensor mount' else (n,(p[0],p[1]-.0001,p[2])) if n=='Research field sensor probe' and p[1]==-2.76 else (n,p) for n,p in probes]
for name,p in probes:assert inside(name,p),(name,p)
(out/'research-additions-verification.json').write_text(json.dumps(dict(new_closed_positive_meshes=volumes,scoped_attachment_probes=[dict(object=n,point=list(p)) for n,p in probes],wear_objects=[ob.name for ob in new if 'wear' in ob.name],limitations=['Scoped containment witnesses; not exhaustive mechanical or source-exact geometry acceptance.']),indent=2)+'\n',encoding='utf-8');print('BATTLESHIP_ADDITIONS_VERIFIED',len(new),len(probes))
