import bpy,sys,json,hashlib,bmesh
from pathlib import Path
o=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.open_mainfile(filepath=str(o/'mk2-mine.blend'))
m=json.loads((o/'model.json').read_text());assert list(m['components'])==['chassis','slurry-recovery-ports','drill-assemblies','coolant-connectors']
objects=list(bpy.context.scene.objects);meshes=[x for x in objects if x.type=='MESH'];count=0
for ob in meshes:
 bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),ob.name;bm.free();count+=1
for prefix,n in [('Independent multi-head drill ',4),('Carbon cutting crown ',4),('Carbon drill cutting tip',16),('Coolant through-connector annulus ',2),('Slurry recovery flared manifold',2),('Pale pressure chamber brace',6)]:assert len([x for x in objects if x.name.startswith(prefix)])==n,prefix
assert [x['component'] for x in m['phases']]==['slurry-recovery-ports','drill-assemblies','coolant-connectors']
root=bpy.data.objects['MineRotor'];assert abs(root.scale.x-1.06)<1e-5
for ob in meshes:assert ob.parent==root
bores=[x for x in objects if x.name.startswith('Coolant through-connector recessed bore')]
from mathutils import Vector
a,b=[x.location.copy() for x in bores];assert abs(a.z-b.z)<1e-5 and Vector((a.x,a.y)).normalized().dot(Vector((b.x,b.y)).normalized())<-.99
(o/'geometry-verification.json').write_text(json.dumps(dict(closed_meshes=count,drills=4,carbon_tips=16,slurry_ports=2,coolant_connectors=2,pressure_braces=6,root_scale=list(root.scale),blend_sha256=hashlib.sha256((o/'mk2-mine.blend').read_bytes()).hexdigest()),indent=2)+'\n')
print('MINE_GEOMETRY_VERIFIED',count)
