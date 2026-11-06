"""Build RI08 independently authored stacked vessels and exportable wear."""
import json
import math
import sys
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene
from build_refined_terran import export_glb_to,render_to,save_blend_to
from build_terran_missiles import sha
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_databanks_parts import build,DRUM
from manufactured_roof_wells import analytic_lathe_normals
from terran_light_ship_parts import orient_and_chamfer

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/buildings/rigellian/databanks'
VIEWS=[('front-quarter',(6,-13,8)),('rear-quarter',(-8,12,8)),('front',(0,-16,4)),
       ('side',(16,0,4)),('top',(0,0,20)),('underside',(6,-8,-15))]


def wear(meshes):
    material=bpy.data.materials['RI08 | aged jade shell'];cap_material=material.copy();cap_material.name='RI08 | worn planar end caps'
    for target,prefix in [(material,'shell'),(cap_material,'cap')]:
        nodes=target.node_tree.nodes;links=target.node_tree.links
        shader=nodes.get('Principled BSDF');coordinates=nodes.new('ShaderNodeUVMap');coordinates.uv_map='Authored surface wear'
        for suffix,input_name,space in [('colour','Base Color','sRGB'),('roughness','Roughness','Non-Color')]:
            image=bpy.data.images.load(str(ROOT/f'authored-{prefix}-{suffix}.png'));image.colorspace_settings.name=space;image.pack()
            texture=nodes.new('ShaderNodeTexImage');texture.image=image;texture.interpolation='Linear'
            links.new(texture.outputs['Color'],shader.inputs[input_name]);links.new(coordinates.outputs['UV'],texture.inputs['Vector'])
    bpy.context.view_layer.update()
    for obj in meshes:
        if not (obj.name in ['RI08 lower intake drum','RI08 solid connecting neck','RI08 flared middle housing','RI08 rounded upper head']): continue
        while obj.data.uv_layers: obj.data.uv_layers.remove(obj.data.uv_layers[0])
        uv=obj.data.uv_layers.new(name='Authored surface wear');uv.active_render=True
        points=[obj.matrix_world @ v.co for v in obj.data.vertices];low=min(p.z for p in points);high=max(p.z for p in points)
        radii={z:max(math.hypot(p.x,p.y) for p in points if abs(p.z-z)<1e-6) for z in [low,high]}
        cap_index=len(obj.data.materials);obj.data.materials.append(cap_material)
        for face in obj.data.polygons:
            coords=[obj.matrix_world @ obj.data.vertices[obj.data.loops[index].vertex_index].co for index in face.loop_indices]
            cap_z=next((z for z in [low,high] if all(abs(p.z-z)<1e-6 for p in coords)),None)
            if cap_z is not None:
                face.material_index=cap_index
                for index,point in zip(face.loop_indices,coords): uv.data[index].uv=(.5+point.x/(2*radii[cap_z]),.5+point.y/(2*radii[cap_z]))
                continue
            values=[(math.atan2(p.y,p.x)+math.pi)/math.tau for p in coords];wraps=max(values)-min(values)>.5
            for index,point,u in zip(face.loop_indices,coords,values): uv.data[index].uv=(u+1 if wraps and u<.5 else u,point.z/5.2)


def main():
    ROOT.mkdir(parents=True,exist_ok=True);scene=setup_scene(900,64)
    collection=bpy.data.collections.new('Rigellian Databanks editable source');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    build();meshes=[obj for obj in collection.objects if obj.type=='MESH'];orient_and_chamfer(meshes)
    analytic_lathe_normals(bpy.data.objects['RI08 lower intake drum'],DRUM)
    wear(meshes)
    root=bpy.data.objects.new('PlacementRoot',None);collection.objects.link(root)
    root['catalogue_id']='openfa:building/legacy/047';root['footprint_width']=2;root['footprint_height']=2
    for obj in meshes: obj.parent=root
    collection.asset_mark();collection.asset_data.description='Independent RI08 stacked vessels; nominal 2x2 placement'
    points=evaluated_points(meshes)
    for view,direction in VIEWS: fit_camera(scene,points,direction);render_to(scene,ROOT/(view+'.png'))
    fit_camera(scene,points,VIEWS[0][1]);bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes+[root]: obj.select_set(True)
    bpy.context.view_layer.objects.active=root;export_glb_to(ROOT/'model.glb');save_blend_to(ROOT/'model.blend')
    meta=dict(id='openfa:building/legacy/047',issue=978,revision=4,culture='rigellian',name='Databanks',global_type=47,
        footprint=[2,2],placement_root='PlacementRoot',origin='Nominal footprint centre, ground Z=0; runtime calibration pending',
        blend_sha256=sha(ROOT/'model.blend'),glb_sha256=sha(ROOT/'model.glb'),blender=bpy.app.version_string,
        generator_sha256=sha(Path(__file__)),parts_sha256=sha(Path(__file__).with_name('rigellian_databanks_parts.py')),
        reference_sha256=sha(REPO/'docs/reconstruction/models/rigellian-building-references.json'),
        authored_wear_sha256=sha(ROOT/'authored-wear.json'),mesh_objects=len(meshes),views=[name for name,_ in VIEWS],resolution=900,
        helper_sha256={name:sha(Path(__file__).with_name(name)) for name in ['manufactured_roof_wells.py','manufactured_vessels.py','manufactured_surface_mounts.py']},
        observed=['Lower drum, narrow neck, flared middle housing and upper head','Large gold circular fitting and smaller gold/dark fittings','Twin upper supports, side module and silver fork'],
        inferred=['Intake depths, fitting engineering and support/crown connections','Dimensions, materials, wear and small dents'],
        imported_geometry_or_textures=[],unresolved=['Final artistic acceptance','Construction/damage states','Runtime scale/orientation/placement'],
        acceptance='Reference-refined study, not final acceptance')
    (ROOT/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('RIGELLIAN_DATABANKS_MODEL_OK',len(meshes),flush=True)


if __name__=='__main__': main()
