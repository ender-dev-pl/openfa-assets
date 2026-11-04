"""Build explicit low-resolution interpretations preserving the special missile IDs."""
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene
from build_refined_terran import export_glb_to,render_to,save_blend_to
from build_terran_missiles import VIEWS,sha
from catalogue_rendering import evaluated_points,fit_camera
from special_missile_parts import palette,bug_hunter,meat_eater
from terran_light_ship_parts import orient_and_chamfer

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/missiles/terran'


def main():
    refs=json.loads((REPO/'docs/reconstruction/models/missile-reference-index.json').read_text())['missiles']
    for name,builder in [('bug-hunter',bug_hunter),('meat-eater',meat_eater)]:
        output=ROOT/name;output.mkdir(parents=True,exist_ok=True)
        scene=setup_scene(768,64)
        collection=bpy.data.collections.new(name+' editable interpretation');scene.collection.children.link(collection)
        bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
        builder(palette())
        meshes=[obj for obj in collection.objects if obj.type=='MESH'];orient_and_chamfer(meshes)
        collection.asset_mark();collection.asset_data.description='Independent low-resolution interpretation; no bound management preview'
        points=evaluated_points(meshes)
        for view,direction in VIEWS:
            fit_camera(scene,points,direction);render_to(scene,output/(view+'.png'))
        fit_camera(scene,points,VIEWS[1][1])
        bpy.ops.object.select_all(action='DESELECT')
        for obj in meshes: obj.select_set(True)
        bpy.context.view_layer.objects.active=meshes[0]
        export_glb_to(output/'model.glb');save_blend_to(output/'model.blend')
        ref=next(r for r in refs if r['id']=='openfa:missile/terran/'+name)
        meta=dict(id=ref['id'],issue=968,revision=2,blender=bpy.app.version_string,
            blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),
            generator_sha256=sha(Path(__file__)),parts_sha256=sha(Path(__file__).with_name('special_missile_parts.py')),
            dependency_sha256={name:sha(Path(__file__).with_name(name)) for name in ['terran_missile_parts.py','build_terran_missiles.py']},
            mesh_objects=len(meshes),views=[view for view,_ in VIEWS],axis='+Z nose; authored canonical launch-frame-9 alignment; uncalibrated',
            references=dict(management=None,surface=ref['surface']['source_sha256'],frames=[0,1,2,3,4,5,6,9]),
            observed=['Small silver/blue/red elongated silhouette',
                      'Gold end and yellow ring before silver shaft' if name=='bug-hunter' else 'Gray bulb, red neck, blue middle, pale lower band and red end'],
            inferred=['All fine manufactured detail','Fourfold blue open-frame construction','Nozzle and mounting interiors',
                      'Hidden geometry, true dimensions and precise silhouette between pixels'],
            imported_geometry_or_textures=[],unresolved=['No bound high-resolution management reference','Gameplay axes/scale/socket transforms','Final artistic acceptance'],
            acceptance='interpretation study; reference fidelity and final integration acceptance open')
        (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n')
        print('SPECIAL_MISSILE_MODEL_OK',name,len(meshes),flush=True)


if __name__=='__main__': main()
