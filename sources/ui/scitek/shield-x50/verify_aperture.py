"""Prove the PH15 service opening exists in native/evaluated and imported geometry."""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();base=Path(sys.argv[sys.argv.index('--')+2]).resolve()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def measure():
    bpy.context.view_layer.update();ob=bpy.data.objects['Tapered connector pressure shell'].evaluated_get(bpy.context.evaluated_depsgraph_get())
    root=bpy.data.objects.get('ShieldX50Root');world=root.matrix_world if root else Matrix.Identity(4);inverse=ob.matrix_world.inverted();result={}
    for label,angle in [('opening',3*math.pi/4),('intact',7*math.pi/4)]:
        radial=Vector((math.cos(angle),0,math.sin(angle)));origin=world@(radial*.95+Vector((0,.82,0)));direction=world.to_3x3()@(-radial)
        hit,point,_,_=ob.ray_cast(inverse@origin,inverse.to_3x3()@direction)
        assert hit,(label,'ray unexpectedly escaped both sides')
        point=world.inverted()@ob.matrix_world@point;result[label]=float(point.dot(radial))
    mesh=ob.to_mesh();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.normal_update()
    result['nonmanifold_edges']=sum(not e.is_manifold for e in bm.edges);result['signed_volume']=bm.calc_volume(signed=True);bm.free();ob.to_mesh_clear()
    return result

bpy.ops.wm.open_mainfile(filepath=str(base));original=measure();assert original['opening']>.45
bpy.ops.wm.open_mainfile(filepath=str(out/'shield-x50.blend'));bpy.context.scene.frame_set(1);native=measure()
assert native['opening']<.30 and native['intact']>.45,native
assert native['nonmanifold_edges']==0 and native['signed_volume']>0,native
for ob in list(bpy.context.scene.objects):
    if ob.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'shield-x50.glb'));bpy.context.scene.frame_set(1);imported=measure()
assert not any('Authoring connector' in ob.name for ob in bpy.context.scene.objects)
assert imported['opening']<.30 and imported['intact']>.45 and imported['nonmanifold_edges']==0,imported
assert max(abs(native[k]-imported[k]) for k in ['opening','intact'])<2e-5
(out/'aperture-verification.json').write_text(json.dumps(dict(native=native,independent_import=imported,original_closed_control=original,real_geometry_opening=True,authoring_cutter_excluded_from_export=True,source_sha256=sha(out/'shield-x50.blend'),glb_sha256=sha(out/'shield-x50.glb'),base_sha256=sha(base),verifier_sha256=sha(__file__)),indent=2)+'\n')
print('X50_APERTURE_NATIVE_IMPORT_VERIFIED',native)
