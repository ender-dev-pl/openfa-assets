"""Build RI10 independently authored paired cover mechanism and exportable wear."""
import json
import math
import sys
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene
from build_refined_terran import render_to,save_blend_to
from build_terran_missiles import sha
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_ground_deck_parts import build,tidy
from rigellian_shaft_preview import ground_mask,surface_points
from terran_light_ship_parts import orient_and_chamfer

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/buildings/rigellian/ground-deck'
VIEWS=[('front-quarter',(6,-13,8)),('rear-quarter',(-8,12,8)),('front',(0,-16,4)),
       ('side',(16,0,4)),('top',(0,0,20)),('underside',(6,-8,-15)),('reference-facing',(0,-16,7))]


def wear(meshes):
    material=bpy.data.materials['RI10 | worn green casting']
    cap_material=material.copy();cap_material.name='RI10 | worn planar casting caps'
    for target,prefix in [(material,'shell'),(cap_material,'cap')]:
        nodes=target.node_tree.nodes;links=target.node_tree.links
        shader=nodes.get('Principled BSDF');coordinates=nodes.new('ShaderNodeUVMap');coordinates.uv_map='Authored surface wear'
        for suffix,input_name,space in [('colour','Base Color','sRGB'),('roughness','Roughness','Non-Color')]:
            image=bpy.data.images.load(str(ROOT/f'authored-{prefix}-{suffix}.png'));image.colorspace_settings.name=space;image.pack()
            texture=nodes.new('ShaderNodeTexImage');texture.image=image;texture.interpolation='Linear'
            links.new(texture.outputs['Color'],shader.inputs[input_name]);links.new(coordinates.outputs['UV'],texture.inputs['Vector'])
    for obj in meshes:
        if material not in list(obj.data.materials): continue
        bpy.context.view_layer.objects.active=obj
        for modifier in list(obj.modifiers): bpy.ops.object.modifier_apply(modifier=modifier.name)
        tidy(obj);bpy.context.view_layer.update()
        while obj.data.uv_layers: obj.data.uv_layers.remove(obj.data.uv_layers[0])
        uv=obj.data.uv_layers.new(name='Authored surface wear');uv.active_render=True
        points=[obj.matrix_world @ v.co for v in obj.data.vertices]
        low=min(p.z for p in points);high=max(p.z for p in points)
        xmin=min(p.x for p in points);xmax=max(p.x for p in points)
        ymin=min(p.y for p in points);ymax=max(p.y for p in points)
        cx=(xmin+xmax)/2;cy=(ymin+ymax)/2
        cap_index=len(obj.data.materials);obj.data.materials.append(cap_material)
        for face in obj.data.polygons:
            coords=[obj.matrix_world @ obj.data.vertices[obj.data.loops[index].vertex_index].co for index in face.loop_indices]
            planar=any(all(abs(p.z-z)<1e-6 for p in coords) for z in [low,high])
            if planar:
                face.material_index=cap_index
                for index,point in zip(face.loop_indices,coords): uv.data[index].uv=((point.x-xmin)/(xmax-xmin),(point.y-ymin)/(ymax-ymin))
                continue
            values=[(math.atan2(p.y-cy,p.x-cx)+math.pi)/math.tau for p in coords];wraps=max(values)-min(values)>.5
            for index,point,u in zip(face.loop_indices,coords,values): uv.data[index].uv=(u+1 if wraps and u<.5 else u,point.z/1.6)


def main():
    ROOT.mkdir(parents=True,exist_ok=True);scene=setup_scene(900,64)
    collection=bpy.data.collections.new('Rigellian Ground Deck editable source');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    covers,segments=build();meshes=[obj for obj in collection.objects if obj.type=='MESH'];orient_and_chamfer(meshes)
    wear(meshes)
    root=bpy.data.objects.new('PlacementRoot',None);collection.objects.link(root)
    root['catalogue_id']='openfa:building/legacy/049';root['footprint_width']=3;root['footprint_height']=3
    bpy.context.view_layer.update()
    for obj in meshes:
        if obj.parent is None: obj.parent=root
    for cover in covers: cover.parent=root
    scene.frame_start=1;scene.frame_end=61
    for cover in covers:
        for frame,lift in [(1,0),(5,.035),(31,.035),(57,.035),(61,0)]:
            cover.location.z=1.02+lift;cover.keyframe_insert(data_path='location',frame=frame)
    for segment in segments:
        for frame,fraction in [(1,0),(5,0),(31,1),(57,0),(61,0)]:
            segment.location.x=segment['stroke']*fraction;segment.keyframe_insert(data_path='location',frame=frame)
    for animated in covers+segments:
        action=animated.animation_data.action;action.name=animated.name+' authored telescopic motion'
        track=animated.animation_data.nla_tracks.new();track.name='GroundDeckCoverCycle'
        track.strips.new('GroundDeckCoverCycle',1,action);animated.animation_data.action=None
    scene.frame_set(1)
    collection.asset_mark();collection.asset_data.description='Independent RI10 paired telescopic deck; nominal 3x3 placement'
    ground_mask();points=surface_points(meshes)
    for view,direction in VIEWS:
        ground_mask().hide_render=view=='underside'
        fit_camera(scene,evaluated_points(meshes) if view=='underside' else points,direction)
        render_to(scene,ROOT/(view+'.png'))
    ground_mask().hide_render=False
    fit_camera(scene,points,VIEWS[0][1])
    for frame,label in [(16,'half-open'),(31,'open')]:
        scene.frame_set(frame);render_to(scene,ROOT/(label+'.png'))
    scene.frame_set(1)
    fit_camera(scene,points,VIEWS[0][1]);bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes+[root]+covers+segments: obj.select_set(True)
    bpy.context.view_layer.objects.active=root;bpy.ops.export_scene.gltf(filepath=str(ROOT/'model.glb'),export_format='GLB',export_extras=True,use_selection=True,export_apply=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_frame_range=True);save_blend_to(ROOT/'model.blend')
    meta=dict(id='openfa:building/legacy/049',issue=980,revision=6,culture='rigellian',name='Ground Deck',global_type=49,
        footprint=[3,3],placement_root='PlacementRoot',origin='Nominal footprint centre, ground Z=0; runtime calibration pending',
        blend_sha256=sha(ROOT/'model.blend'),glb_sha256=sha(ROOT/'model.glb'),blender=bpy.app.version_string,
        generator_sha256=sha(Path(__file__)),parts_sha256=sha(Path(__file__).with_name('rigellian_ground_deck_parts.py')),
        reference_sha256=sha(REPO/'docs/reconstruction/models/rigellian-building-references.json'),
        functional_evidence_sha256=sha(REPO/'docs/reconstruction/models/rigellian-ground-deck-mechanism.json'),
        authored_wear_sha256=sha(ROOT/'authored-wear.json'),mesh_objects=len(meshes),views=[name for name,_ in VIEWS],resolution=900,
        helper_sha256={name:sha(Path(__file__).with_name(name)) for name in ['rigellian_construction_parts.py','manufactured_annuli.py','manufactured_vessels.py']},
        observed=['Green oval body, paired disappearing covers and deep hangar-access shaft with vertical wall features and red fittings','Brass structural buttresses, front steps and right mast'],
        inferred=['Lift and two-stage side retraction are an authored mechanism hypothesis','Shaft depth, guide engineering, dimensions, wear and 61-frame preview timing'],
        underground_geometry=[obj.name for obj in meshes if obj.name.startswith('RI10 shaft')],
        underground_depth_inferred=True,preview_ground_mask='Render-only holdout outside the shaft mouth; excluded from GLB',
        animation=dict(clip='GroundDeckCoverCycle',closed_frame=1,half_frame=16,open_frame=31,end_frame=61,
            scale_animated=False,mechanism="lift-then-two-stage-retraction",legacy_state_evidence='docs/reconstruction/models/rigellian-ground-deck-mechanism.json'),
        imported_geometry_or_textures=[],unresolved=['Final artistic acceptance','Construction/damage states','Runtime scale/orientation/placement'],
        acceptance='Reference-refined study, not final acceptance')
    (ROOT/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('RIGELLIAN_GROUND_DECK_MODEL_OK',len(meshes),flush=True)


if __name__=='__main__': main()
