"""Build independently authored Explosive and Area Explosive missile studies."""
import hashlib
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene
from build_refined_terran import export_glb_to,render_to,save_blend_to
from catalogue_rendering import evaluated_points,fit_camera
from terran_light_ship_parts import orient_and_chamfer
from terran_missile_parts import build

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/missiles/terran'
VIEWS=[('front',(0,-15,1)),('front-quarter',(9,-15,6)),('rear-quarter',(-9,15,6)),
       ('side',(15,0,1)),('nose',(0,-1,20)),('nozzle',(0,-2,-20))]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    references=json.loads((REPO/'docs/reconstruction/models/missile-reference-index.json').read_text())['missiles']
    for name in ['explosive','area-explosive']:
        output=ROOT/name;output.mkdir(parents=True,exist_ok=True)
        scene=setup_scene(768,48)
        collection=bpy.data.collections.new(name+' editable source');scene.collection.children.link(collection)
        bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
        build(area=name=='area-explosive')
        meshes=[obj for obj in collection.objects if obj.type=='MESH']
        orient_and_chamfer(meshes)
        collection.asset_mark();collection.asset_data.description='Independent missile study; hidden pod count and dimensions authored'
        points=evaluated_points(meshes)
        for view,direction in VIEWS:
            fit_camera(scene,points,direction);render_to(scene,output/(view+'.png'))
        fit_camera(scene,points,VIEWS[1][1])
        bpy.ops.object.select_all(action='DESELECT')
        for obj in meshes: obj.select_set(True)
        bpy.context.view_layer.objects.active=meshes[0]
        export_glb_to(output/'model.glb');save_blend_to(output/'model.blend')
        ref=next(r for r in references if r['id']=='openfa:'+name)
        metadata=dict(id=ref['id'],issue=959,revision=2,blender=bpy.app.version_string,
            blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),
            generator_sha256=sha(Path(__file__)),parts_sha256=sha(Path(__file__).with_name('terran_missile_parts.py')),
            mesh_objects=len(meshes),views=[view for view,_ in VIEWS],axis='+Z nose; front -Y; authored units',
            references=dict(management=ref['management_preview']['source_sha256'],surface=ref['surface']['source_sha256'],frames=[0,3,6,9]),
            observed=['Gray segmented cylindrical body','Red jacket and long rounded tail pods',
                      'Recessed nose instrumentation','Distinct rounded versus stepped nose'],
            inferred=['Fourfold hidden tail pod arrangement','Exact dimensions and materials','Nozzle interior and service fittings'],
            imported_geometry_or_textures=[],unresolved=['Gameplay axes and scale','Socket transforms','Final artistic acceptance'],
            acceptance='study; visual and integration acceptance open')
        (output/'model.json').write_text(json.dumps(metadata,indent=2)+'\n')
        print('TERRAN_MISSILE_OK',name,len(meshes),flush=True)


if __name__=='__main__': main()
