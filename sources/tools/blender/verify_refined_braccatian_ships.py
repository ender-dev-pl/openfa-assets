"""Fresh five-ship review: retained construction contracts, added equipment and independent GLB renders."""
import argparse
import hashlib
import importlib
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from refine_braccatian_ships import ROOT,CASES,MODIFIED,folders,review_media,source,objects,frame_view,sha
from verify_refined_braccatian_pithoi import tree,inside
from verify_rigellian_crowns import snapshot,drift,compare_render
from verify_rigellian_filtration import socket_value
sys.path.insert(0,str(ROOT/'tools'))
from gallery_animation_assets import glb_clips


def old_contract(key,imported=False):
    module=importlib.import_module('verify_braccatian_'+key.replace('-','_'))
    return dict(construction=module.structure(objects(),imported=imported),textures=module.texture_evidence(objects()))


def helpers():
    return {o.name:dict(parent=o.parent.name if o.parent else None,matrix=[list(row) for row in o.matrix_world]) for o in bpy.context.scene.objects if o.type=='EMPTY'}


def mesh_geometry(obj):
    return dict(vertices=[list(v.co) for v in obj.data.vertices],faces=[list(f.vertices) for f in obj.data.polygons],
      uv={layer.name:[list(p.uv) for p in layer.data] for layer in obj.data.uv_layers},normals=[list(n.vector) for n in obj.data.corner_normals])


def materials():
    result={}
    for mat in {m for o in objects() for m in o.data.materials}:
        shader=mat.node_tree.nodes.get('Principled BSDF');values={}
        for kind,socket in [('colour','Base Color'),('roughness','Roughness')]:
            entry=shader.inputs[socket]
            if not entry.is_linked:
                values[kind]=dict(constant=list(entry.default_value) if kind=='colour' else float(entry.default_value));continue
            link=entry.links[0];node=link.from_node;channel=None
            if node.type in ['SEPARATE_COLOR','SEPRGB']:
                channel=list(node.outputs).index(link.from_socket);node=node.inputs[0].links[0].from_node
            assert node.type=='TEX_IMAGE',mat.name
            image=node.image;assert image.packed_file and image.size[0]==image.size[1] and image.size[0] in [256,1024]
            pixels=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(pixels);pixels=pixels.reshape(-1,4)
            effective=pixels[:,:3] if kind=='colour' else pixels[:,channel if channel is not None else 0]
            assert np.isfinite(effective).all() and np.ptp(effective)>.005
            # Compare the actual shader channels, allowing transport channel packing.
            quantized=np.ascontiguousarray(np.round(effective*65535).astype(np.uint16))
            values[kind]=dict(size=list(image.size),effective_pixel_sha256=hashlib.sha256(quantized.tobytes()).hexdigest())
        values['metallic']=float(socket_value(shader.inputs['Metallic'],(.37,.52)));result[mat.name]=values
    return result


def compare_materials(a,b):
    assert a.keys()==b.keys()
    for name,x in a.items():
        y=b[name];assert abs(x['metallic']-y['metallic'])<.004
        for kind in ['colour','roughness']:
            if 'constant' not in x[kind]:assert x[kind]==y[kind],(name,kind,'Packed effective shader pixels changed')
            else:
                aa,bb=x[kind]['constant'],y[kind]['constant'];aa=aa if isinstance(aa,list) else [aa];bb=bb if isinstance(bb,list) else [bb]
                assert len(aa)==len(bb) and max(abs(u-v) for u,v in zip(aa,bb))<.004


def structure(key,meta):
    meshes=objects();root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']=='openfa:ship/braccatian/'+key
    assert all(o.parent==root and not o.modifiers for o in meshes)
    # Constant-material hardware needs no UV layer; every image-mapped part does.
    for obj in meshes:
        mapped=any(mat.use_nodes and any(n.type=='TEX_IMAGE' and n.image for n in mat.node_tree.nodes) for mat in obj.data.materials)
        assert not mapped or obj.data.uv_layers,(obj.name,'Image-mapped part lacks UVs')
    assert not any(o.animation_data for o in bpy.context.scene.objects),'Unsupported operating/deployment clip'
    assert max(abs(root.matrix_world[i][j]-(i==j)) for i in range(4) for j in range(4))<1e-6
    marked=[c for c in bpy.data.collections if c.asset_data]
    assert len(marked)==1 and all(o.name in marked[0].objects for o in meshes+[root])
    trees={};volumes={}
    for obj in meshes:
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges),(obj.name,'Open/inconsistent solid')
        volumes[obj.name]=bm.calc_volume(signed=True);assert volumes[obj.name]>1e-10,(obj.name,'Nonpositive solid');bm.free();trees[obj.name]=tree(obj)
    contacts=[];features={}
    if key in MODIFIED:
        assert len(meshes)==meta['mesh_objects']
        for spec in meta['attachments']:
            obj=bpy.data.objects[spec['name']];owner=trees[spec['owner']]
            points=[obj.matrix_world@v.co for v in obj.data.vertices]
            points += [obj.matrix_world@(f.center-f.normal*.0001) for f in obj.data.polygons]
            hit=next((p for p in points if inside(owner,p)),None)
            # A thick service casing can fully enclose its supporting arm.
            # Test the reverse containment direction as well as fitted roots.
            if hit is None:
                support=bpy.data.objects[spec['owner']]
                points=[support.matrix_world@(f.center-f.normal*.0001) for f in support.data.polygons]
                hit=next((p for p in points if inside(trees[obj.name],p)),None)
            assert hit is not None,(obj.name,spec['owner'],'Added equipment has no supporting intersection')
            contacts.append(dict(parts=[obj.name,spec['owner']],point=list(hit)))
        if key=='skymech':
            core=trees['SkyMech expanded axial pressure core'];sections=[]
            for z in [-.70,.55,1.15]:
                hit=core.ray_cast(Vector((3,0,z)),Vector((-1,0,0)),6)[0];assert hit is not None;sections.append(hit.x)
            assert sections[0]>.83 and sections[1]>.85 and .60<sections[2]<.66,'Expanded station body regressed to thin axial shaft'
            assert volumes['SkyMech expanded axial pressure core']>4.5,'Missing substantial central body volume'
            gaps=[]
            for i in range(4):
                n=Vector((math.cos(i*math.pi/2),math.sin(i*math.pi/2),0))
                casing=bpy.data.objects[f'SkyMech broad radial service casing {i}'];module=bpy.data.objects[f'SkyMech rose radial module {i}']
                outer=max((casing.matrix_world@v.co).dot(n) for v in casing.data.vertices);inner=min((module.matrix_world@v.co).dot(n) for v in module.data.vertices)
                gaps.append(inner-outer)
                assert outer>1.33 and abs(inner-outer)<.04,'Central service body stops too far from peripheral hemisphere'
            assert sum(n.startswith('SkyMech new axial housing ') and not any(s in n for s in ['collar','face']) for n in trees)==8
            features=dict(expanded_core_radial_sections=sections,expanded_core_volume=volumes['SkyMech expanded axial pressure core'],radial_casing_to_hemisphere_gaps=gaps,large_axial_housings=8)
        else:
            prefix=CASES[key][1];widths=[]
            for spec in meta['attachments']:
                obj=bpy.data.objects[spec['name']];points=[obj.matrix_world@v.co for v in obj.data.vertices if abs(v.co.y+.93)<.027]
                assert points;radials=[Vector((p.x,0,p.z)) for p in points]
                # Arc width measured as maximum radial direction separation, including wrap.
                spread=max(a.angle(b) for a in radials for b in radials);assert .20<spread<.26,'Forward fields became hairline accents';widths.append(spread)
            features=dict(broad_forward_field_count=len(widths),measured_field_angular_widths=widths)
    return dict(positive_closed_meshes=len(meshes),part_contacts=contacts,added_parts_support_checked=key in MODIFIED,volumes=volumes,**features)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=CASES,required=True)
    key=parser.parse_args(sys.argv[sys.argv.index('--')+1:]).model;media=review_media(key);media.mkdir(parents=True,exist_ok=True)
    output=folders(key)[0] if key in MODIFIED else source(key).parent
    meta=json.loads((output/'model.json').read_text());baseline=json.loads((ROOT/'sources/docs/reconstruction/models/braccatian-refining-baseline.json').read_text())
    record=next(r for r in baseline['records'] if r['key']==CASES[key][0]);assert sha(source(key))==record['blend_sha256'] and sha(source(key).with_suffix('.glb'))==record['glb_sha256']
    for kind in ['blend','glb']:assert meta[kind+'_sha256']==sha(output/('model.'+kind))
    if key in MODIFIED:
        assert meta['generator_sha256']==sha(Path(__file__).with_name('refine_braccatian_ships.py')) and meta['source_blend_sha256']==sha(source(key))
        for name,value in meta['dependency_sha256'].items():assert sha(Path(__file__).with_name(name))==value
        for name,value in meta['texture_sha256'].items():assert sha(ROOT/name)==value
        for field,name in [('lore_sha256','braccatian-lore-evidence.json'),('reference_sha256','braccatian-refining-baseline.json'),('functional_sha256','functional-text-index.json')]:assert meta[field]==sha(ROOT/'sources/docs/reconstruction/models'/name)
    bpy.ops.wm.open_mainfile(filepath=str(source(key)));baseline_contract=old_contract(key)
    original=snapshot();original_geometry={o.name:mesh_geometry(o) for o in objects()};original_helpers=helpers()
    original_core=None
    if key=='skymech':
        core=bpy.data.objects['SkyMech dark axial core'];bvh=tree(core)
        sections=[bvh.ray_cast(Vector((3,0,z)),Vector((-1,0,0)),6)[0].x for z in [-.70,.55,1.15]]
        bm=bmesh.new();bm.from_mesh(core.data);volume=bm.calc_volume(signed=True);bm.free()
        original_core=dict(radial_sections=sections,volume=volume)
    bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'));native=snapshot();native_helpers=helpers();native_structure=structure(key,meta);native_materials=materials()
    if original_core:
        assert native_structure['expanded_core_radial_sections'][1]>2.5*original_core['radial_sections'][1]
        assert native_structure['expanded_core_volume']>4.5*original_core['volume']
    removed=set(meta['removed_objects']) if key in MODIFIED else set();preserved=set(original)-removed
    added=set(meta['added_objects']) if key in MODIFIED else set();assert set(native)==preserved|added
    for name in preserved:
        assert native[name]==original[name],(name,'Retained body changed')
        assert mesh_geometry(bpy.data.objects[name])==original_geometry[name],(name,'Retained topology/UVs/corner normals changed')
    assert native_helpers==original_helpers,'Alignment helpers changed'
    native_contract=old_contract(key) if key not in MODIFIED else None
    views=['front-quarter','rear-quarter','side','equipment-detail']
    scene=bpy.context.scene;scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.cycles.samples=32
    for view in views:frame_view(key,view);scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    collection=next(c for c in bpy.data.collections if c.asset_data)
    for obj in list(scene.objects):
        if obj.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
    for mat in list(bpy.data.materials):bpy.data.materials.remove(mat,do_unlink=True)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    bpy.ops.import_scene.gltf(filepath=str(output/'model.glb'));imported=snapshot();imported_helpers=helpers();imported_structure=structure(key,meta);imported_materials=materials();compare_materials(native_materials,imported_materials)
    error=0;assert native.keys()==imported.keys() and native_helpers.keys()==imported_helpers.keys()
    for name in native:
        a,b=native[name],imported[name];error=max(error,drift(a['points'],b['points']),drift(b['points'],a['points']))
        assert a['parent']==b['parent'] and a['materials']==b['materials']
    assert error<.0001
    for name,a in native_helpers.items():
        b=imported_helpers[name];assert a['parent']==b['parent'] and max(abs(a['matrix'][i][j]-b['matrix'][i][j]) for i in range(4) for j in range(4))<1e-5
    imported_contract=old_contract(key,imported=True) if key not in MODIFIED else None
    if key not in MODIFIED:assert native_contract['textures']==imported_contract['textures']
    assert glb_clips(output/'model.glb')==glb_clips(source(key).with_suffix('.glb'))==[]
    renders={}
    for view in views:
        frame_view(key,view);path=media/('imported-'+view+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);renders[view]=compare_render(media/(view+'.png'),path,view!='equipment-detail')
    dependencies=['verify_braccatian_'+key.replace('-','_')+'.py','refine_braccatian_ships.py','verify_refined_braccatian_pithoi.py','verify_rigellian_crowns.py','verify_rigellian_filtration.py']
    report=dict(issue=190,model=key,decision='refined' if key in MODIFIED else 'retained-after-focused-review',blender=bpy.app.version_string,source_blend_sha256=sha(source(key)),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),
      generator_sha256=meta['generator_sha256'],verifier_sha256=sha(Path(__file__)),verifier_dependencies_sha256={n:sha(Path(__file__).with_name(n)) for n in dependencies},native_mesh_count=len(native),imported_mesh_count=len(imported),
      maximum_native_imported_position_error=error,native_structure=native_structure,imported_structure=imported_structure,native_materials=native_materials,imported_materials=imported_materials,source_baseline_construction_contract=baseline_contract,
      retained_native_contract=native_contract,retained_imported_contract=imported_contract,original_station_core=original_core,preserved_mesh_names=sorted(preserved),retained_geometry_uv_normal_equality=True,alignment_helpers_preserved=True,renders=renders,
      acceptance='Fresh actual native/import review; hidden construction and exact alloys remain authored')
    (media/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('BRACCATIAN_SHIP_NATIVE_GLB_VERIFIED',key,report['decision'],len(native),error,flush=True)


if __name__=='__main__':main()
