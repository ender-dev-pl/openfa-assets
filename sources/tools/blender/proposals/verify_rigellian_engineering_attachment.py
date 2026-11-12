"""Verify actual hull-skin proximity under scaled roots,including a negative control."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[4]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TARGETS=['broad fore formed skin','broad aft formed skin','panoramic crew visor','copper nacelle service collar','nacelle inspection slot']


def proximity():
    bpy.context.view_layer.update()
    body=bpy.data.objects['Rigellian smooth oval hull']
    tree=BVHTree.FromPolygons([body.matrix_world@v.co for v in body.data.vertices],[tuple(f.vertices) for f in body.data.polygons])
    targets=[o for o in bpy.context.scene.objects if o.type=='MESH' and any(t in o.name for t in TARGETS)]
    assert len(targets)==7
    worst=0
    for obj in targets:
        parents=[];node=obj.parent
        while node:parents.append(node);node=node.parent
        surface=body
        if 'nacelle' in obj.name:
            surface=next((p for p in parents if 'smooth side nacelle' in p.name),None)
            assert surface is not None,obj.name
            span=max(v.co.z for v in obj.data.vertices)-min(v.co.z for v in obj.data.vertices)
            assert span>.007,('Flat patch on curved nacelle',obj.name,span)
        assert surface in parents,('Skin does not inherit housing transform',obj.name)
        surface_tree=tree if surface==body else BVHTree.FromPolygons([surface.matrix_world@v.co for v in surface.data.vertices],[tuple(f.vertices) for f in surface.data.polygons])
        scale=max(surface.matrix_world.to_scale())
        error=max(surface_tree.find_nearest(obj.matrix_world@v.co)[3] for v in obj.data.vertices)
        assert error<.045*scale,('Lifted skin',obj.name,error,scale)
        worst=max(worst,error)
    return worst


def check(ext,folder):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if ext=='blend':bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'),load_ui=False,use_scripts=False)
    else:bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'))
    errors=[]
    for frame in [1,13,25,49,73,97]:
        bpy.context.scene.frame_set(frame);errors.append(proximity())
    obj=next(o for o in bpy.context.scene.objects if 'broad fore formed skin' in o.name)
    saved=obj.location.copy();obj.location.z+=.25
    rejected=False
    try:proximity()
    except AssertionError:rejected=True
    finally:obj.location=saved;bpy.context.view_layer.update()
    assert rejected,'Deliberately lifted panel was accepted'
    proximity()
    return dict(maximum_surface_distance=max(errors),frames=[1,13,25,49,73,97],lifted_panel_negative_control_rejected=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--role',choices=['terraform','repair'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);folder=ROOT/'sources/proposals/engineering-ships/rigellian'/a.role
    before={ext:sha(folder/('model.'+ext)) for ext in ['blend','glb']}
    result={ext:check(ext,folder) for ext in ['blend','glb']}
    assert before=={ext:sha(folder/('model.'+ext)) for ext in before}
    report=dict(binaries=before,verifier=Path(__file__).relative_to(ROOT).as_posix(),verifier_sha256=sha(Path(__file__)),results=result,scope='Stationary broad skins inherit the actual hull transform and remain near the hull surface in native/imported models. This does not certify swept mechanism clearance.')
    (folder/'attachment-review.json').write_text(json.dumps(report,indent=2)+'\n');print('RIGELLIAN_SKIN_ATTACHMENT_OK',a.role,result,flush=True)
if __name__=='__main__':main()
