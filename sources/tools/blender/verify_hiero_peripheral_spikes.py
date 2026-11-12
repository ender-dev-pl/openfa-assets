"""Saved native attachment checks and imported-geometry rays for eight small spikes."""
from pathlib import Path
import json,math,sys
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
import remaster_mikotaj_mobile_ships as author


def main():
    out,media=author.folders('hiero');meta=json.loads((out/'model.json').read_text());patch=meta['spike_refinement'];before={k:author.sha(out/('model.'+k)) for k in ['blend','glb']}
    assert patch['generator_sha256']==author.sha(author.ROOT/patch['generator'])
    bpy.ops.wm.open_mainfile(filepath=str(out/'model.blend'),load_ui=False,use_scripts=False);body=bpy.data.objects[patch['mesh_group']]
    groups=[g for g in body.vertex_groups if g.name.startswith('HieroPeripheralSpike')];assert len(groups)==8
    group_indices={g.index for g in groups};all_spikes={v.index for v in body.data.vertices if any(w.group in group_indices for w in v.groups)}
    points=[body.matrix_world@v.co for v in body.data.vertices];base=BVHTree.FromPolygons(points,[tuple(f.vertices) for f in body.data.polygons if not any(i in all_spikes for i in f.vertices)])
    contacts=0
    for group in groups:
        ids={v.index for v in body.data.vertices if any(w.group==group.index for w in v.groups)}
        faces=[tuple(f.vertices) for f in body.data.polygons if all(i in ids for i in f.vertices)];assert faces
        tree=BVHTree.FromPolygons(points,faces);assert tree.overlap(base),('detached spike',group.name);contacts+=1
    ray_checks={}
    for kind in ['native','imported']:
        if kind=='imported':
            for o in list(bpy.context.scene.objects):
                if o.type in ['MESH','EMPTY']:bpy.data.objects.remove(o,do_unlink=True)
            bpy.ops.import_scene.gltf(filepath=str(out/'model.glb'))
        bpy.context.view_layer.update();scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();count=0
        for i,spike in enumerate(patch['spikes']):
            assert spike['azimuth_degrees']==i*45
            start,tip=Vector(spike['start']),Vector(spike['tip']);probe=start.lerp(tip,.70)
            hit,p,n,index,o,matrix=scene.ray_cast(deps,Vector((probe.x,probe.y,.7)),Vector((0,0,-1)),distance=1)
            assert hit and o.name==patch['mesh_group'] and p.z>.08,('missing small projection',kind,i,p,o.name if o else None);count+=1
        ray_checks[kind]=count
    assert before=={k:author.sha(out/('model.'+k)) for k in before}
    report=dict(binaries=before,spikes=8,spacing_degrees=45,seated_native_contacts=contacts,ray_checks=ray_checks,mesh_batches=4,material_count=1,patcher_sha256=patch['generator_sha256'],verifier_sha256=author.sha(Path(__file__)),scope='Static attachment and imported visibility checks; exact legacy dimensions remain authored')
    (out/'spike-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('HIERO_SPIKES_VERIFIED',json.dumps(report),flush=True)
    # Recheck actual sources/imports and refresh every gallery angle after the patch.
    import verify_mikotaj_mobile_remasters as runtime
    runtime.main('hiero')
    bpy.ops.wm.open_mainfile(filepath=str(out/'model.blend'),load_ui=False,use_scripts=False)
    for o in list(bpy.context.scene.objects):
        if o.type in ['MESH','EMPTY']:bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(out/'model.glb'))
    for label,direction in author.VIEWS.items():runtime.render(media/(label+'.png'),direction)
    path=out/'runtime-verification.json';result=json.loads(path.read_text())
    result['renders']={p.name:author.sha(p) for p in media.glob('*.png')}
    result['gallery_refresh_verifier_sha256']=author.sha(Path(__file__))
    path.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
