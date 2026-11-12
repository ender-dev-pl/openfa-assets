"""Build original Photon/Plasma equipment sources and transparent comparison views."""
import hashlib
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene
from build_refined_terran import export_glb_to,render_to,save_blend_to
from catalogue_rendering import evaluated_points,fit_camera
from cannon_equipment_parts import palette,photon,plasma
from terran_light_ship_parts import orient_and_chamfer

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/hardpoints'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    for name,builder,reference in [('photon-cannon',photon,'PH06.VID'),('plasma-cannon',plasma,'PH07.VID')]:
        output=ROOT/name
        output.mkdir(parents=True,exist_ok=True)
        scene=setup_scene(768,48)
        bpy.context.preferences.filepaths.save_version=0
        collection=bpy.data.collections.new(name+' independent equipment source')
        scene.collection.children.link(collection)
        bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
        builder(palette())
        collection.asset_mark()
        collection.asset_data.description='Independent PH06/PH07 study; mounting and aiming transforms not established'
        meshes=[obj for obj in collection.objects if obj.type=='MESH']
        orient_and_chamfer(meshes)
        points=evaluated_points(meshes)
        views=[('front-quarter',(8,-12,10)),('rear-quarter',(-8,12,10)),('top',(0,0,20)),
               ('front',(0,-15,3)),('rear',(0,15,3)),('side',(15,0,3)),('belly',(7,-10,-12))]
        for view,direction in views:
            fit_camera(scene,points,direction)
            render_to(scene,output/(view+'.png'))
        fit_camera(scene,points,views[0][1])
        bpy.ops.object.select_all(action='DESELECT')
        for obj in meshes:
            obj.select_set(True)
        bpy.context.view_layer.objects.active=meshes[0]
        export_glb_to(output/'model.glb')
        save_blend_to(output/'model.blend')
        metadata=dict(id='openfa:'+name,issue=957,revision=4 if name=='plasma-cannon' else 3,blender=bpy.app.version_string,
            generator_sha256=sha(Path(__file__)),parts_sha256=sha(Path(__file__).with_name('cannon_equipment_parts.py')),
            blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),
            mesh_objects=len(meshes),reference=reference,reference_frames=[0,7,14,22,29,36,44,51,59],
            views=[view for view,_ in views],imported_geometry_or_textures=[],
            inferred=['Exact dimensions','Internal barrel bores and breeches','Fastener and cooling geometry'],
            unresolved=['Cultural variants','3D ship sockets','Independent aiming/recoil mechanisms','Final matched-camera detail review'],
            acceptance='study; no final acceptance gates changed')
        (output/'model.json').write_text(json.dumps(metadata,indent=2)+'\n')
        print('CANNON_MODEL_OK',name,len(meshes),flush=True)


if __name__=='__main__':
    main()
