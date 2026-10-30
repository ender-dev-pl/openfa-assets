"""Export and actually re-import RI10 descriptor-pose studies; legacy pixels remain reference-only."""
import hashlib
import json
import struct
import sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene
from build_refined_terran import render_to
from build_rigellian_ground_deck import ROOT,REPO
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_shaft_preview import asset_meshes,ground_mask,surface_points
from verify_assault_fighter import check_meshes
from verify_nuclear_missile import geometry_bounds
from verify_rigellian_filtration import material_values
from verify_rigellian_ground_deck import moving,tree,texture_evidence,indicator_visibility,clear_shaft

OUT=ROOT/'states'
EVIDENCE=REPO/'docs/reconstruction/models/rigellian-ground-deck-mechanism.json'


def sha(path):
    data=path.read_bytes()
    if path.suffix in ['.json','.py']: data=data.replace(b'\r\n',b'\n')
    return hashlib.sha256(data).hexdigest()


def gltf_evidence(path):
    raw=path.read_bytes();length,kind=struct.unpack_from('<II',raw,12);assert kind==0x4e4f534a
    document=json.loads(raw[20:20+length]);assert not document.get('animations')
    offset=20+length;size,kind=struct.unpack_from('<II',raw,offset);assert kind==0x004e4942
    binary=raw[offset+8:offset+8+size];images=[]
    for image in document.get('images',[]):
        view=document['bufferViews'][image['bufferView']];start=view.get('byteOffset',0)
        images.append(hashlib.sha256(binary[start:start+view['byteLength']]).hexdigest())
    return dict(materials=document['materials'],textures=document['textures'],images=images)


def pose_controls(widths):
    if widths is None: return [1,1]
    # Authored fit of remaining X extent, not recovered mechanics or timing.
    return [(.838/.88)*(1-width/14) for width in widths]


def apply_pose(fractions):
    for obj in bpy.context.scene.objects:
        if obj.animation_data: obj.animation_data_clear()
    for side,sign,fraction in zip(['Left','Right'],[-1,1],fractions):
        bpy.data.objects['Cover'+side].location.z=1.02 if fraction==0 else 1.055
        for segment in ['Inner','Outer']:
            root=bpy.data.objects['Cover'+side+segment]
            root.location.x=sign*(.88 if segment=='Inner' else .46)*fraction
    bpy.context.view_layer.update()


def check_pose(meshes):
    check_meshes(meshes,allow_packed_images=True)
    root=bpy.data.objects['PlacementRoot'];assert root.matrix_world.is_identity
    assert root['catalogue_id']=='openfa:building/legacy/049' and root['footprint_width']==root['footprint_height']==3
    assert all(not obj.animation_data for obj in bpy.context.scene.objects if obj.type in ['MESH','EMPTY'])
    movers=[obj for obj in meshes if moving(obj)];fixed=[obj for obj in meshes if not moving(obj)]
    assert len(meshes)==45 and len(movers)==8
    shapes={obj.name:tree(obj) for obj in meshes}
    for obj in movers:
        for target in fixed:
            assert not shapes[obj.name].overlap(shapes[target.name]),('Moving/fixed intersection',obj.name,target.name)
    for i,obj in enumerate(movers):
        for target in movers[i+1:]:
            if obj.parent!=target.parent:
                assert not shapes[obj.name].overlap(shapes[target.name]),('Separate stage intersection',obj.name,target.name)
    bounds=geometry_bounds(meshes);assert min(bounds[:2])>=-1.5 and max(bounds[3:5])<=1.5 and -2.05<bounds[2]<-1.9
    return dict(bounds=bounds,objects={obj.name:dict(matrix=[v for row in obj.matrix_world for v in row],bounds=geometry_bounds([obj])) for obj in meshes})


def main():
    OUT.mkdir(parents=True,exist_ok=True);meta=json.loads((ROOT/'model.json').read_text());evidence=json.loads(EVIDENCE.read_text())
    assert sha(ROOT/'model.blend')==meta['blend_sha256'] and sha(ROOT/'model.glb')==meta['glb_sha256']
    measurements={item['index']:item for item in evidence['measurements']};exports=[];common_gltf=None;first_textures=None
    for descriptor in list(range(2,15))+[15]:
        stowed=descriptor==15;name='covers-stowed' if stowed else f'descriptor-{descriptor:02}'
        widths=None if stowed else [half['projected_width'] for half in measurements[descriptor]['halves']]
        fractions=pose_controls(widths)
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'));apply_pose(fractions)
        scene=bpy.context.scene;meshes=asset_meshes(scene);native=check_pose(meshes)
        visibility=indicator_visibility(meshes,descriptor==15) if descriptor in [2,15] else None
        if descriptor==15: clear_shaft(meshes)
        native_materials=material_values(meshes)
        if first_textures is None: first_textures=texture_evidence(meshes)
        fit_camera(scene,surface_points(meshes),(0,-16,7));camera=scene.camera
        view=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
        native_render=OUT/(name+'-native.png');render_to(scene,native_render)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in scene.objects:
            if obj.type in ['MESH','EMPTY'] and not obj.get('preview_only'): obj.select_set(True)
        target=OUT/(name+'.glb')
        bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',export_extras=True,use_selection=True,
            export_apply=True,export_animations=False)
        embedded=gltf_evidence(target)
        if common_gltf is None: common_gltf=embedded
        else: assert embedded==common_gltf,'State changed embedded material/texture content'
        scene=setup_scene(900,64);bpy.ops.import_scene.gltf(filepath=str(target))
        imported=asset_meshes(scene);actual=check_pose(imported)
        if visibility is not None: assert indicator_visibility(imported,descriptor==15)==visibility
        if descriptor==15: clear_shaft(imported)
        assert native['objects'].keys()==actual['objects'].keys()
        error=max(abs(a-b) for key in native['objects'] for field in ['matrix','bounds'] for a,b in zip(native['objects'][key][field],actual['objects'][key][field]))
        assert error<.00003,('Imported pose geometry/transform differs',descriptor,error)
        materials=material_values(imported);assert materials.keys()==native_materials.keys()
        for key,value in native_materials.items():
            other=materials[key];assert max(abs(a-b) for a,b in zip(value[0]+value[1:],other[0]+other[1:]))<1/255+.00001
        if descriptor==2: assert texture_evidence(imported)==first_textures
        ground_mask()
        scene.camera.location=view[0];scene.camera.rotation_euler=view[1];scene.camera.data.ortho_scale=view[2]
        imported_render=OUT/(name+'-imported.png');render_to(scene,imported_render)
        exports.append(dict(key=name,descriptors=[15,16,17] if stowed else [descriptor],reference_widths=widths,authored_fractions=fractions,
            glb=target.name,glb_sha256=sha(target),native_render=native_render.name,native_render_sha256=sha(native_render),
            imported_render=imported_render.name,imported_render_sha256=sha(imported_render),maximum_geometry_transform_error=error,
            indicator_visibility=visibility,fixed_moving_intersections=0,separate_moving_stage_intersections=0,bounds=actual['bounds']))
        print('RI10_DESCRIPTOR_POSE_OK',name,flush=True)
    states=[]
    for descriptor in range(2,18):
        item=next(item for item in exports if descriptor in item['descriptors'])
        role=('paired-cover-overlay' if descriptor<15 else 'empty-cover-overlay' if descriptor<17 else 'lower-structure-and-mixed-shadow-overlay')
        states.append(dict(descriptor=descriptor,asset=item['glb'],legacy_role=role,
            composition_verified=False if descriptor==17 else None,
            note='Full authored 3D assembly pose; not original overlay pixels or calibrated game composition'))
    result=dict(issue=980,id=meta['id'],revision=meta['revision'],source_blend_sha256=meta['blend_sha256'],
        source_glb_sha256=meta['glb_sha256'],mechanism_evidence_sha256=sha(EVIDENCE),generator_sha256=sha(Path(__file__)),
        text_hash_policy='lf-for-json-and-python',mapping='Authored remaining-X-width fit from reference alpha bounds; hidden mechanics are inferred',
        no_attached_ship_descriptor=2,altitude_bands=evidence['legacy_mapping']['signed_altitude_bands'],
        states=states,exports=exports,embedded_material_texture_evidence=common_gltf,
        validations=['Actual native pose and static GLB re-import per unique pose','Topology, 3x3 root, matrices and per-object actual vertex bounds',
            'Moving/fixed and separate moving-stage surface intersections','Common embedded materials/images plus full colour/roughness pixels on first pose',
            'Native and imported diagnostic frontal render for every unique pose'],
        unresolved=['Final visual acceptance and pose refinement','Continuous sweep, volumetric containment and complete attachment engineering',
            'Descriptor 17 lower-structure/purple-shadow composition and calibrated game integration'],final_visual_acceptance=False)
    (OUT/'state-exports.json').write_text(json.dumps(result,indent=2)+'\n');print('RI10_DESCRIPTOR_EXPORTS_OK',len(exports),'assets',len(states),'descriptors',flush=True)


if __name__=='__main__': main()
