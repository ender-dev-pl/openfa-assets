"""Verify the declared local edit against the pre-refinement research model."""
import bpy, json, sys
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:]
old,new,out=map(Path,args)
def snapshot(ob):
    return dict(vertices=[tuple(v.co) for v in ob.data.vertices],faces=[tuple(p.vertices) for p in ob.data.polygons],uv={u.name:[tuple(v.uv) for v in u.data] for u in ob.data.uv_layers},materials=[m.name for m in ob.data.materials],matrix=[tuple(r) for r in ob.matrix_basis])
bpy.ops.wm.open_mainfile(filepath=str(old/'mega-missile.blend'))
model=json.loads((old/'model.json').read_text())
names=[n for group in model['components'].values() for n in group]
before={n:snapshot(bpy.data.objects[n]) for n in names}
bpy.ops.wm.open_mainfile(filepath=str(new/'mega-missile.blend'))
updated=json.loads((new/'model.json').read_text())
removed=updated['removed_inferred_lower_parts']
assert len(removed)==7 and all(n not in bpy.data.objects for n in removed)
body='Mega cylindrical pressure casing'
retained=[n for n in names if n not in removed and n!=body]
assert len(retained)==64
assert all(snapshot(bpy.data.objects[n])==before[n] for n in retained)
a=before[body];b=snapshot(bpy.data.objects[body])
assert {k:v for k,v in a.items() if k!='vertices'}=={k:v for k,v in b.items() if k!='vertices'}
profile=updated['lower_neck_profile'];upper=lower=0;maximum=0
for p,q in zip(a['vertices'],b['vertices']):
    x,y,z=p
    if z>=1.20-1e-7:
        assert p==q;upper+=1;continue
    if z<=.65: oldr,newr=profile[0][1:]
    else:
        for lo,hi in zip(profile,profile[1:]):
            if lo[0]<=z<=hi[0]:
                t=(z-lo[0])/(hi[0]-lo[0]);oldr=lo[1]+t*(hi[1]-lo[1]);newr=lo[2]+t*(hi[2]-lo[2]);break
    error=(Vector(q)-Vector((x*newr/oldr,y*newr/oldr,z))).length
    assert error<1e-6;maximum=max(maximum,error);lower+=1
assert upper and lower
out.mkdir(parents=True,exist_ok=True)
(out/'refined-profile-verification.json').write_text(json.dumps(dict(unchanged_research_meshes=len(retained),removed_parts=removed,unchanged_upper_vertices=upper,refined_lower_vertices=lower,maximum_profile_error=maximum,faces_uv_materials_bind_preserved=True,limitation='Lower profile dimensions are authored from the clearer ST13 reference, not recovered original 3D dimensions.'),indent=2)+'\n',encoding='utf-8')
print('MEGA_PROFILE_VERIFIED',len(retained),upper,lower,maximum)
