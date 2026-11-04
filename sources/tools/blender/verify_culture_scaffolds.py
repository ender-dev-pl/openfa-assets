"""Actual native/independent GLB validation for every exported culture state."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_culture_scaffolds import ROOT,REPO,FAMILIES,sha,LIMITS
from culture_scaffold_contract import chain,definitions_for,phases
from build_openfa_assets import setup_scene
from build_refined_terran import render_to
from verify_assault_fighter import check_meshes
from verify_rigellian_filtration import material_values


def local_uv(obj):
    mesh=obj.data
    assert mesh.uv_layers.active is not None,obj.name
    uv=mesh.uv_layers.active.data
    return [tuple(mesh.vertices[loop.vertex_index].co)+tuple(uv[loop.index].uv) for loop in mesh.loops]


def equivalent_samples(a,b):
    for source,target in [(a,b),(b,a)]:
        tree=KDTree(len(target))
        for i,value in enumerate(target):tree.insert(value[:3],i)
        tree.balance()
        for value in source:
            assert any(max(abs(value[k]-target[index][k]) for k in [3,4])<1e-5 for _,index,_ in tree.find_range(value[:3],1e-5)),'Local geometry/UV correspondence changed'


def texture_pixels():
    result={}
    for material in bpy.data.materials:
        if ' scaffold ' not in material.name:continue
        shader=material.node_tree.nodes.get('Principled BSDF')
        entries=[]
        for key in ['Base Color','Roughness']:
            node=shader.inputs[key].links[0].from_node;channel=None
            if node.type in ['SEPRGB','SEPARATE_COLOR']:
                channel=1;node=node.inputs[0].links[0].from_node
            assert node.type=='TEX_IMAGE' and node.image.packed_file
            assert list(node.image.size)==[256,256]
            values=node.image.pixels[:]
            values=values[channel::4] if channel is not None else (values[0::4] if key=='Roughness' else values)
            entries.append(hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in values)).hexdigest())
        result[material.name]=entries
    assert len(result)==2
    return result


def inspect(manifest,case):
    scene=bpy.context.scene
    meshes=[o for o in scene.objects if o.type=='MESH']
    assert len(meshes)==case['mesh_objects']
    unique={o.data.as_pointer():o for o in meshes}
    assert len(unique)==case['unique_meshes'],'Geometry instancing expanded'
    check_meshes(list(unique.values()),allow_packed_images=True)
    root=bpy.data.objects['PlacementRoot']
    assert root.matrix_world.is_identity
    assert root['family']==manifest['family'] and root['culture']==manifest['culture']
    assert root['footprint_width']==root['footprint_height']==manifest['footprint']
    assert root['construction_stage']==case['stage'] and not root['physical_pitch_calibrated']
    assert case['frames']==chain(case['stage'],manifest['capacity'])
    foundations=[o for o in meshes if o['scaffold_role']=='foundation']
    assert len(foundations)==12 and all(o.parent==root for o in foundations)
    assert sorted(o.name for o in meshes if not o['reveal_visible'])==sorted(case['hide_on_reveal'])
    assert all(o['scaffold_role']=='temporary-crown' for o in meshes if not o['reveal_visible'])
    assert not any(o['scaffold_role']=='interior-shoring' for o in meshes)
    count=max(2,manifest['footprint']*2)
    pitch=manifest['pitch'];unit=pitch/manifest['capacity']
    for level,frame in enumerate(case['frames']):
        tier=bpy.data.objects[f'Tier {level}']
        assert tier.parent==root and tier['stage_frame']==frame
        bottom=bpy.data.objects[f'Tier {level} BottomSocket'];top=bpy.data.objects[f'Tier {level} TopSocket']
        assert bottom.parent==top.parent==tier
        assert abs(bottom.matrix_world.translation.z-level*pitch)<1e-5
        assert abs(top.matrix_world.translation.z-(level+1)*pitch)<1e-5
        if level:
            assert case['frames'][level-1]==manifest['capacity']
            previous=bpy.data.objects[f'Tier {level-1} TopSocket']
            assert (bottom.matrix_world.translation-previous.matrix_world.translation).length<1e-5
        for side in range(4):
            for n in range(count):
                post=bpy.data.objects[f'Tier {level} side {side} post {n}']
                points=[post.matrix_world@v.co for v in post.data.vertices]
                low=min(v.z for v in points);high=max(v.z for v in points)
                assert abs(low-level*pitch)<1e-5
                assert abs(high-(level*pitch+frame*unit))<1e-5
                if level:
                    sleeve=bpy.data.objects[f'Tier {level} sleeve {side}-{n}']
                    points=[sleeve.matrix_world@v.co for v in sleeve.data.vertices]
                    assert min(v.z for v in points)<low<max(v.z for v in points)
    samples={pointer:local_uv(obj) for pointer,obj in unique.items()}
    objects={}
    all_points=[]
    for obj in scene.objects:
        if obj.type not in ['MESH','EMPTY']:continue
        if obj.type=='MESH':all_points.extend(obj.matrix_world@Vector(corner) for corner in obj.bound_box)
        objects[obj.name]=dict(parent=obj.parent.name if obj.parent else None,matrix=[v for row in obj.matrix_world for v in row],
                               role=obj.get('scaffold_role'),reveal=obj.get('reveal_visible'),
                               geometry=obj.data.as_pointer() if obj.type=='MESH' else None)
    bounds=[min(p[axis] for p in all_points) for axis in range(3)]+[max(p[axis] for p in all_points) for axis in range(3)]
    assert bounds[0]>=-manifest['footprint']*.45-.13 and bounds[1]>=-manifest['footprint']*.45-.13
    assert bounds[3]<=manifest['footprint']*.45+.13 and bounds[4]<=manifest['footprint']*.45+.13
    assert bounds[2]>=-.06 and bounds[5]<=case['stage']*unit+.20
    return objects,samples,material_values(list(unique.values())),texture_pixels(),bounds


def verify_family(family):
    folder=ROOT/'families'/family['family'];manifest=json.loads((folder/'model.json').read_text())
    assert not manifest['preview_only']
    assert [c['stage'] for c in manifest['cases']]==list(range(1,family['max_required_stage']+1))
    assert manifest['definitions']==definitions_for(family['family'],LIMITS) and manifest['phases']==phases()
    assert len(manifest['cases'][-1]['frames'])==family['max_required_tiers']
    for path,digest in manifest['inputs'].items():assert sha(REPO/path)==digest,path
    reports=[]
    for case in manifest['cases']:
        print('CULTURE_VERIFY',family['family'],case['stage'],'/',family['max_required_stage'],flush=True)
        stage=folder/f"stage-{case['stage']:02}"
        for ext in ['blend','glb']:assert sha(stage/f'model.{ext}')==case[f'{ext}_sha256']
        raw=(stage/'model.glb').read_bytes();length=struct.unpack_from('<I',raw,12)[0];gltf=json.loads(raw[20:20+length])
        assert len(gltf['meshes'])==case['unique_meshes']
        assert sum('mesh' in n for n in gltf['nodes'])==case['mesh_objects']
        bpy.ops.wm.open_mainfile(filepath=str(stage/'model.blend'))
        native,samples,materials,textures,bounds=inspect(manifest,case)
        camera=bpy.context.scene.camera;pose=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
        scene=setup_scene(512,24);scene.render.threads_mode='FIXED';scene.render.threads=8
        bpy.ops.import_scene.gltf(filepath=str(stage/'model.glb'))
        imported,other_samples,other_materials,other_textures,other_bounds=inspect(manifest,case)
        assert native.keys()==imported.keys() and textures==other_textures
        assert max(abs(a-b) for a,b in zip(bounds,other_bounds))<1e-5
        pairs=set()
        for name,item in native.items():
            other=imported[name]
            assert item['parent']==other['parent'] and item['role']==other['role'] and item['reveal']==other['reveal']
            assert max(abs(a-b) for a,b in zip(item['matrix'],other['matrix']))<1e-5,name
            if item['geometry'] is not None:pairs.add((item['geometry'],other['geometry']))
        for a,b in pairs:equivalent_samples(samples[a],other_samples[b])
        assert materials.keys()==other_materials.keys()
        for name,value in materials.items():
            other=other_materials[name]
            assert max(abs(a-b) for a,b in zip(value[0]+value[1:],other[0]+other[1:]))<1/255+.00001
        scene.camera.location=pose[0];scene.camera.rotation_euler=pose[1];scene.camera.data.ortho_scale=pose[2]
        render_to(scene,stage/'imported-front-quarter.png')
        reports.append(dict(stage=case['stage'],nodes=len(native),mesh_objects=case['mesh_objects'],unique_meshes=case['unique_meshes'],bounds=bounds,geometry_uv_pairs=len(pairs),material_pixels=textures))
    report=dict(issue=188,family=family['family'],model_manifest_sha256=sha(folder/'model.json'),verifier_sha256=sha(Path(__file__)),
                checks=['All native and independently imported states','Positive mesh topology; shared meshes; local geometry/UV correspondence','Parent and world matrices; node role/reveal extras','Material values and packed pixels','Source ranges; phase/definition sequences','Single foundations; all post endpoints; sockets and sleeve overlap','Imported render using saved native camera'],
                cases=reports,limitations=['Conservative transformed mesh-box footprint checks, not exhaustive collision proof','World-height calibration and game integration remain open'])
    (folder/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n')
    return dict(family=family['family'],cases=len(reports),technical_review_sha256=sha(folder/'technical-review.json'))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--families',nargs='*')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    records=[verify_family(f) for f in FAMILIES if not args.families or f['family'] in args.families]
    if not args.families:(ROOT/'technical-review.json').write_text(json.dumps(dict(issue=188,families=records,verified_states=sum(r['cases'] for r in records)),indent=2)+'\n')
    print('CULTURE_SCAFFOLDS_VERIFIED',len(records),sum(r['cases'] for r in records),flush=True)


if __name__=='__main__':main()
