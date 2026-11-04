"""Reopen RIS2 native/GLB states and validate tier sockets and physical joints."""
import hashlib,json,struct,sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_refined_rigellian_scaffold import ROOT,PITCH,LIMITS_PATH,FAMILY_LIMITS,CASES
from build_openfa_assets import setup_scene
from analyse_scaffold_stacking import scaffold_chain
from build_refined_terran import render_to
from verify_assault_fighter import check_meshes
from verify_nuclear_missile import geometry_bounds
from verify_rigellian_filtration import material_values


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def texture_pixels():
    result={}
    for material in [m for m in bpy.data.materials if m.name.startswith('RIS2 |')]:
        shader=material.node_tree.nodes.get('Principled BSDF');items=[]
        for key in ['Base Color','Roughness']:
            node=shader.inputs[key].links[0].from_node;channel=None
            if node.type in ['SEPRGB','SEPARATE_COLOR']: channel=1;node=node.inputs[0].links[0].from_node
            assert node.type=='TEX_IMAGE' and node.image.packed_file
            values=node.image.pixels[:];values=values[channel::4] if channel is not None else (values[0::4] if key=='Roughness' else values)
            assert list(node.image.size)==[256,256]
            items.append(hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in values)).hexdigest())
        result[material.name]=items
    assert len(result)==2
    return result


def uv_samples(obj):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    try:
        assert mesh.uv_layers.active is not None,obj.name+' has no UV mapping'
        uv=mesh.uv_layers.active.data
        return [tuple(evaluated.matrix_world @ mesh.vertices[loop.vertex_index].co)+tuple(uv[loop.index].uv) for loop in mesh.loops]
    finally: evaluated.to_mesh_clear()


def matching_uvs(a,b):
    for source,target in [(a,b),(b,a)]:
        tree=KDTree(len(target))
        for i,value in enumerate(target): tree.insert(value[:3],i)
        tree.balance()
        for value in source:
            assert any(max(abs(value[k]-target[index][k]) for k in [3,4])<1e-5 for _,index,_ in tree.find_range(value[:3],1e-5)),'Export altered evaluated position/UV pairing'


def inspect(record):
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];check_meshes(meshes,allow_packed_images=True)
    assert record['frames']==[item['frame'] for item in scaffold_chain(record['total_stage']-1,0,255,2)]
    assert len(meshes)==record['mesh_objects']
    assert len({obj.data.as_pointer() for obj in meshes})==record['unique_meshes'],'Shared native/imported mesh instances were expanded'
    root=bpy.data.objects['PlacementRoot']
    assert root.matrix_world.is_identity and root['family']=='RIS2' and root['construction_stage']==record['total_stage']
    assert root['footprint_width']==root['footprint_height']==2 and not root['physical_pitch_calibrated']
    assert len([o for o in meshes if o.name.startswith('Ground foot ')])==33
    # Clamp pins protrude beyond the nominal 1.8 envelope by 0.003 units.
    expected_rows=sum(2 if frame==1 else 3 for frame in record['frames'])
    assert len([o for o in meshes if ' clamp ' in o.name and ' pin ' not in o.name])==33*expected_rows
    assert len([o for o in meshes if ' clamp pin ' in o.name])==66*expected_rows
    snapshots={}
    for level,frame in enumerate(record['frames']):
        tier=bpy.data.objects[f'Tier {level}'];assert tier.parent==root and tier['stage_frame']==frame
        assert abs(tier.matrix_world.translation.z-level*PITCH)<1e-6
        bottom=bpy.data.objects[f'Tier {level} BottomSocket'];top=bpy.data.objects[f'Tier {level} TopSocket']
        assert bottom.parent==top.parent==tier
        assert abs((top.matrix_world.translation-bottom.matrix_world.translation).z-PITCH)<1e-6
        if level:
            assert record['frames'][level-1]==2,'Only complete tiers may support a following tier'
            previous=bpy.data.objects[f'Tier {level-1} TopSocket']
            assert (bottom.matrix_world.translation-previous.matrix_world.translation).length<1e-6
        for i in range(33):
            post=bpy.data.objects[f'Tier {level} upright {i}'];assert post.parent==tier
            bounds=geometry_bounds([post]);assert abs(bounds[2]-level*PITCH)<1e-6
            assert abs(bounds[5]-(level+frame/2)*PITCH)<1e-6
            if level:
                lower=geometry_bounds([bpy.data.objects[f'Tier {level-1} upright {i}']]);sleeve=geometry_bounds([bpy.data.objects[f'Tier {level} joint sleeve {i}']])
                assert abs(lower[5]-bounds[2])<1e-6,'Post butt joint gap'
                assert sleeve[2]<bounds[2]<sleeve[5] and lower[5]>sleeve[2],'Sleeve must bridge both posts'
    for obj in bpy.context.scene.objects:
        if obj.type not in ['MESH','EMPTY']: continue
        snapshots[obj.name]=dict(parent=obj.parent.name if obj.parent else None,matrix=[v for row in obj.matrix_world for v in row],bounds=geometry_bounds([obj]) if obj.type=='MESH' else None,uv_samples=uv_samples(obj) if obj.type=='MESH' else None)
    bounds=geometry_bounds(meshes);assert min(bounds[:2])>=-.910 and max(bounds[3:5])<=.910 and abs(bounds[2])<1e-6
    assert abs(bounds[5]-((len(record['frames'])-1)+record['frames'][-1]/2)*PITCH)<1e-6
    return snapshots,material_values(meshes),texture_pixels(),bounds


def main():
    meta=json.loads((ROOT/'model.json').read_text());wear=json.loads((ROOT/'authored-wear.json').read_text())
    assert sha(Path(__file__).with_name('build_refined_rigellian_scaffold.py'))==meta['generator_sha256']
    assert sha(ROOT/'authored-wear.json')==meta['wear_sha256']
    assert sha(Path(__file__).with_name('author_refined_rigellian_scaffold_wear.py'))==wear['generator_sha256']
    for name,digest in wear['images'].items(): assert sha(ROOT/name)==digest
    assert sha(LIMITS_PATH)==meta['stage_limits_sha256']
    assert meta['required_max_stage']==FAMILY_LIMITS['max_required_stage'] and meta['required_max_tiers']==FAMILY_LIMITS['max_required_tiers']
    assert [r['total_stage'] for r in meta['cases']]==CASES
    assert len(meta['cases'][-1]['frames'])==FAMILY_LIMITS['max_required_tiers']
    reports=[]
    for record in meta['cases']:
        print('RIS2_VERIFY_STAGE',record['total_stage'],'of',meta['required_max_stage'],flush=True)
        folder=ROOT/f"stage-{record['total_stage']:02}"
        for ext in ['blend','glb']: assert sha(folder/f'model.{ext}')==record[ext+'_sha256']
        glb=(folder/'model.glb').read_bytes();length=struct.unpack_from('<I',glb,12)[0];document=json.loads(glb[20:20+length])
        assert len(document['meshes'])==record['unique_meshes'],'GLB expanded shared geometry'
        bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'));native,materials,textures,bounds=inspect(record)
        for image in bpy.data.images:
            if image.source=='FILE': assert image.packed_file and hashlib.sha256(image.packed_file.data).hexdigest()==wear['images'][image.name]
        camera=bpy.context.scene.camera;pose=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
        scene=setup_scene(900,64);bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'))
        imported,other,imported_textures,imported_bounds=inspect(record)
        assert native.keys()==imported.keys() and textures==imported_textures and materials.keys()==other.keys()
        for name,value in native.items():
            actual=imported[name];assert value['parent']==actual['parent']
            assert max(abs(a-b) for a,b in zip(value['matrix'],actual['matrix']))<1e-5
            if value['bounds']:
                assert max(abs(a-b) for a,b in zip(value['bounds'],actual['bounds']))<1e-5
                matching_uvs(value['uv_samples'],actual['uv_samples'])
        for name,value in materials.items():
            actual=other[name];assert max(abs(a-b) for a,b in zip(value[0]+value[1:],actual[0]+actual[1:]))<1/255+.00001
        scene.camera.location=pose[0];scene.camera.rotation_euler=pose[1];scene.camera.data.ortho_scale=pose[2]
        render_to(scene,folder/'imported-front-quarter.png')
        reports.append(dict(total_stage=record['total_stage'],bounds=bounds,mesh_objects=record['mesh_objects'],unique_meshes=record['unique_meshes'],verified_nodes=len(native),textures=textures))
    report=dict(issue=186,support_source_sha256={f'tools/blender/{name}':sha(Path(__file__).with_name(name)) for name in ['build_openfa_assets.py','build_refined_terran.py','catalogue_rendering.py','terran_light_ship_parts.py','analyse_scaffold_stacking.py','author_refined_rigellian_scaffold_wear.py']},model_manifest_sha256=sha(ROOT/'model.json'),verifier_sha256=sha(Path(__file__)),cases=reports,checks=['Native/imported positive topology; shared mesh data and glTF mesh reuse preserved','Actual evaluated bounds per mesh and complete parent/world matrix comparison','Matching packed colour/roughness pixels and quantized materials; bidirectional evaluated world-position/UV correspondence','Coincident tier sockets and post endpoints; sleeves bridge both adjoining posts; ground feet occur once','Actual imported renders with saved native camera'],unresolved=['Physical pitch is provisional','Bounds/joint checks do not prove exhaustive collision clearance','Final visual reference acceptance and game integration'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('RIS2_NATIVE_GLB_OK',len(reports),flush=True)


if __name__=='__main__': main()
