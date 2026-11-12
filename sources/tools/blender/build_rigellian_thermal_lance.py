"""Build RI19 independently authored thermal lance and exportable wear."""
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene
from build_refined_terran import render_to,save_blend_to,stage_path,publish
from build_terran_missiles import sha
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_thermal_lance_parts import build,PROFILES,PAINT,CENTRES,PIVOT,LANCE_TIP,LANCE_AXIS,MOVING
from manufactured_roof_wells import analytic_lathe_normals
from terran_light_ship_parts import orient_and_chamfer

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/buildings/rigellian/thermal-lance'
VIEWS=[('front-quarter',(6,-13,8)),('rear-quarter',(-8,12,8)),('front',(0,-16,4)),
       ('side',(16,0,4)),('top',(0,0,20)),('underside',(6,-8,-15))]


def export_glb_to(target):
    # Preserve the explicit socket/pivot metadata as glTF extras for runtime tools.
    temporary=stage_path('.glb')
    bpy.ops.export_scene.gltf(filepath=str(temporary),export_format='GLB',use_selection=True,
        export_apply=True,export_animations=False,export_extras=True)
    publish(temporary,target)


def wear(meshes):
    styles={}
    for style,name in [('green','RI19 | weathered green armour')]:
        surface=bpy.data.materials[name];cap=surface.copy();cap.name='RI19 | '+style+' planar caps'
        styles[style]=(surface,cap)
        for target,suffix in [(surface,'shell'),(cap,'cap')]:
            nodes=target.node_tree.nodes;links=target.node_tree.links;shader=nodes.get('Principled BSDF')
            coordinates=nodes.new('ShaderNodeUVMap');coordinates.uv_map='Authored surface wear'
            for kind,input_name,space in [('colour','Base Color','sRGB'),('roughness','Roughness','Non-Color')]:
                image=bpy.data.images.load(str(ROOT/f'authored-{style}-{suffix}-{kind}.png'));image.colorspace_settings.name=space;image.pack()
                texture=nodes.new('ShaderNodeTexImage');texture.image=image;texture.interpolation='Linear'
                links.new(texture.outputs['Color'],shader.inputs[input_name]);links.new(coordinates.outputs['UV'],texture.inputs['Vector'])
    bpy.context.view_layer.update()
    for obj in meshes:
        if obj.name not in PAINT: continue
        while obj.data.uv_layers: obj.data.uv_layers.remove(obj.data.uv_layers[0])
        uv=obj.data.uv_layers.new(name='Authored surface wear');uv.active_render=True
        points=[v.co for v in obj.data.vertices];low=min(p.z for p in points);high=max(p.z for p in points)
        radii={z:max(math.hypot(p.x,p.y) for p in points if abs(p.z-z)<1e-6) for z in [low,high]}
        cap_index=len(obj.data.materials);obj.data.materials.append(styles[PAINT[obj.name]][1])
        for face in obj.data.polygons:
            coords=[obj.data.vertices[obj.data.loops[index].vertex_index].co.copy() for index in face.loop_indices]
            cap_z=next((z for z in [low,high] if all(abs(p.z-z)<1e-6 for p in coords)),None)
            if cap_z is not None:
                face.material_index=cap_index
                for index,point in zip(face.loop_indices,coords): uv.data[index].uv=(.5+point.x/(2*radii[cap_z]),.5+point.y/(2*radii[cap_z]))
                continue
            values=[(math.atan2(p.y,p.x)+math.pi)/math.tau for p in coords];wraps=max(values)-min(values)>.5
            for index,point,u in zip(face.loop_indices,coords,values): uv.data[index].uv=(u+1 if wraps and u<.5 else u,point.z/3.0)


def main():
    ROOT.mkdir(parents=True,exist_ok=True);scene=setup_scene(900,64)
    collection=bpy.data.collections.new('Rigellian Thermal Lance editable source');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    build();meshes=[obj for obj in collection.objects if obj.type=='MESH'];orient_and_chamfer(meshes)
    for name,profile in PROFILES.items():
        analytic_lathe_normals(bpy.data.objects[name],profile)
    wear(meshes)
    root=bpy.data.objects.new('PlacementRoot',None);collection.objects.link(root)
    root['catalogue_id']='openfa:building/legacy/058';root['footprint_width']=3;root['footprint_height']=3
    for obj in meshes: obj.parent=root
    yaw=bpy.data.objects.new('YawPivot',None);collection.objects.link(yaw);yaw.parent=root;yaw.location=PIVOT;yaw['axis']='local +Z'
    bpy.context.view_layer.update()
    for name in MOVING:
        obj=bpy.data.objects[name];world=obj.matrix_world.copy();obj.parent=yaw;obj.matrix_world=world
    socket=bpy.data.objects.new('LanceTipSocket',None);collection.objects.link(socket);socket.parent=yaw;socket.location=LANCE_TIP-PIVOT;socket.rotation_euler=LANCE_AXIS.to_track_quat('Z','Y').to_euler();socket['forward_axis']='local +Z'
    bpy.context.view_layer.update()
    collection.asset_mark();collection.asset_data.description='Independent RI19 thermal lance; nominal 3x3 placement'
    points=evaluated_points(meshes)
    for view,direction in VIEWS: fit_camera(scene,points,direction);render_to(scene,ROOT/(view+'.png'))
    fit_camera(scene,points,VIEWS[0][1]);bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes+[root,yaw,socket]: obj.select_set(True)
    bpy.context.view_layer.objects.active=root;export_glb_to(ROOT/'model.glb');save_blend_to(ROOT/'model.blend')
    meta=dict(id='openfa:building/legacy/058',issue=991,revision=1,culture='rigellian',name='Thermal Lance',global_type=58,
        footprint=[3,3],placement_root='PlacementRoot',yaw_pivot='YawPivot',tip_socket='LanceTipSocket',moving_meshes=MOVING,origin='Nominal footprint centre, ground Z=0; runtime calibration pending',
        blend_sha256=sha(ROOT/'model.blend'),glb_sha256=sha(ROOT/'model.glb'),blender=bpy.app.version_string,
        generator_sha256=sha(Path(__file__)),parts_sha256=sha(Path(__file__).with_name('rigellian_thermal_lance_parts.py')),
        reference_sha256=sha(REPO/'docs/reconstruction/models/rigellian-building-references.json'),
        authored_wear_sha256=sha(ROOT/'authored-wear.json'),mesh_objects=len(meshes),views=[name for name,_ in VIEWS],resolution=900,
        helper_sha256={name:sha(Path(__file__).with_name(name)) for name in ['manufactured_roof_wells.py','manufactured_vessels.py','manufactured_annuli.py','manufactured_surface_mounts.py','rigellian_construction_parts.py']},
        functional_source_sha256=sha(REPO/'docs/reconstruction/models/functional-text-index.json'),
        function='Anti-ship thermal weapon; ENGLISH.TXT record 919 at 0x117A1',
        observed=['Fixed green pedestal with bronze strip and side fitting','Rounded upper head and tapered lance change direction across sixteen source overlays'],
        inferred=['Exact profiles, hidden geometry, yaw pivot height and fixed lance elevation','Manufactured bearing/fittings and lance-tip socket; no pitch or firing animation established'],
        imported_geometry_or_textures=[],unresolved=['Final artistic acceptance','Runtime direction calibration, pitch/effects if established','Construction/damage states','Runtime scale/orientation/placement'],
        acceptance='First authored iteration; artistic refinement deferred')
    (ROOT/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('RIGELLIAN_THERMAL_LANCE_MODEL_OK',len(meshes),flush=True)


if __name__=='__main__': main()
