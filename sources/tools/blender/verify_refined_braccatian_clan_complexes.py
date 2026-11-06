"""Test BR01 joined pyramids/recesses and BR02/05 distinct cores, necks and open crown castings."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from refine_braccatian_clan_complexes import ROOT,CASES,VIEWS,folders,source,selected,fit_camera,sha
from verify_refined_braccatian_pithoi import tree,inside,effective_pixels
from verify_rigellian_crowns import snapshot,drift,compare_render


def structure(key):
    root=bpy.data.objects['PlacementRoot'];old=json.loads(source(key).with_suffix('.json').read_text());number,_=CASES[key]
    assert root['catalogue_id']==f'openfa:building/legacy/{number:03}'
    assert [root['footprint_width'],root['footprint_height']]==old['footprint']
    assert max(abs(root.matrix_world[i][j]-(i==j)) for i in range(4) for j in range(4))<1e-6
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objects)=={'br01':74,'br02':47,'br05':37}[key]
    collections=[c for c in bpy.data.collections if c.asset_data]
    assert len(collections)==1 and all(o.name in collections[0].objects for o in objects+[root])
    trees={};samples={};bounds={}
    for obj in objects:
        assert obj.parent==root and obj.data.uv_layers and not obj.modifiers,obj.name
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges),(obj.name,'Open/inconsistent solid')
        assert bm.calc_volume(signed=True)>1e-9,(obj.name,'Nonpositive solid')
        bm.free();trees[obj.name]=tree(obj)
        pts=[obj.matrix_world@v.co for v in obj.data.vertices]
        bounds[obj.name]=[(min(p[k] for p in pts),max(p[k] for p in pts)) for k in range(3)]
        samples[obj.name]=[obj.matrix_world@(p.center-p.normal*.0001) for p in list(obj.data.polygons)[::max(1,len(obj.data.polygons)//1000)]]
        samples[obj.name]+=pts[::max(1,len(pts)//1000)]
    assert not any(o.animation_data for o in bpy.context.scene.objects),'Unsupported operating clip'
    points=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
    assert abs(min(p.z for p in points))<1e-6 and abs(max(p.z for p in points)-{'br01':2.60,'br02':3.07,'br05':2.64}[key])<1e-4
    assert max(abs(p.x) for p in points)<(.56 if key=='br05' else 1.02)
    assert max(abs(p.y) for p in points)<(.56 if key=='br05' else 1.02)
    contacts=[];graph={o.name:set() for o in objects};names=list(graph)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            if any(bounds[a][k][1]<bounds[b][k][0] or bounds[b][k][1]<bounds[a][k][0] for k in range(3)):continue
            hit=next((p for p in samples[a] if inside(trees[b],p)),None)
            if hit is None:hit=next((p for p in samples[b] if inside(trees[a],p)),None)
            if hit is not None:graph[a].add(b);graph[b].add(a);contacts.append(dict(parts=[a,b],point=list(hit)))
    reached=set();queue=[names[0]]
    while queue:
        name=queue.pop()
        if name in reached:continue
        reached.add(name);queue+=list(graph[name]-reached)
    assert reached==set(names),('Disconnected assembly',set(names)-reached)

    def first_hit(x,z):
        hits=[]
        for name,bvh in trees.items():
            hit,_,_,distance=bvh.ray_cast(Vector((x,-3,z)),Vector((0,1,0)),6)
            if hit is not None:hits.append((distance,name,hit))
        assert hits
        return min(hits,key=lambda item:item[0])

    features={}
    if key=='br01':
        sections=[]
        for i,(x,y,height) in enumerate([(0,.46,2.42),(-.49,-.02,2.10),(.49,-.02,2.10),(0,-.47,1.85)]):
            bvh=trees[f'BR01 pyramid {i}'];radii=[]
            for z in [.55,height-.40]:
                hit=bvh.ray_cast(Vector((x+2,y,z)),Vector((-1,0,0)),4)[0];assert hit is not None;radii.append(hit.x-x)
            assert radii[0]>.27 and radii[0]/radii[1]>3,'Tower lost broad pyramidal taper'
            assert abs(bounds[f'BR01 pyramid {i}'][2][0])<1e-6
            sections.append(radii)
        recesses=[]
        for i,x,y,height in [(1,-.49,-.02,2.10),(3,0,-.47,1.85)]:
            _,name,hit=first_hit(x+.045,.16)
            assert name==f'BR01 pyramid {i} entrance dark recessed back',(name,'Portal became a solid painted face')
            half=.43+(.055-.43)*(.16-.08)/(height-.30-.08)
            depth=hit.y-(-half+y);assert .09<depth<.14,('Lost actual entrance depth',depth)
            assert first_hit(x,.30)[1]==f'BR01 pyramid {i} entrance pale vertical grille 1','Grille is hidden or absent'
            recesses.append(dict(pyramid=i,measured_depth=depth))
        assert sum(name.endswith(' blue collar') for name in names)==4
        features=dict(measured_pyramid_sections=sections,grounded_joined_pyramids=4,measured_portal_recesses=recesses,visible_portal_grilles=2,blue_collars=4)
    else:
        prefix=key.upper()+' ';z,spread=(2.49,.22) if key=='br02' else (2.06,.19)
        # Rays pass through the actual off-axis crown void but hit the loop casting.
        origin=Vector((spread*.60,-.50,z+.23));direction=Vector((0,1,0))
        assert not any(b.ray_cast(origin,direction,1)[0] is not None for b in trees.values()),'Crown became a solid globe/fan'
        assert trees[prefix+' crown open loop 0'].ray_cast(Vector((spread,-.5,z+.23)),direction,1)[0] is not None,'Missing open crown frame'
        assert sum('crown open loop' in name for name in names)==2
        features.update(open_crown_loops=2,actual_crown_gap=True)
        if key=='br02':
            widths=[]
            for zz in [.12,1.40]:
                hit=trees['BR02 central cylindrical core'].ray_cast(Vector((2,0,zz)),Vector((-1,0,0)),4)[0];assert hit is not None;widths.append(hit.x)
            assert abs(widths[0]-.29)<.001 and abs(widths[0]-widths[1])<.001,'Central cylinder regressed to generic cone'
            for i,x in enumerate([-.12,.12]):assert first_hit(x,1.33)[1]==f'BR02 pale vertical face {i} 2','Upper core faces obscured'
            assert all(f'BR02 peripheral pyramid {i}' in trees for i in range(3))
            assert sum(name.endswith(' blue collar') for name in names)==3
            features.update(actual_cylindrical_sections=widths,peripheral_pyramids=3,exposed_upper_core_faces=2,blue_collars=3)
        else:
            neck=trees['BR05 rose narrow neck'].ray_cast(Vector((2,0,.94)),Vector((-1,0,0)),4)[0]
            roof=trees['BR05 broad-foot upper spire'].ray_cast(Vector((2,0,1.07)),Vector((-1,0,0)),4)[0]
            assert neck is not None and roof is not None and .10<neck.x<.11 and roof.x/neck.x>2.5,'Stepped body/narrow neck/spire distinction lost'
            assert all(f'BR05 low satellite {i}' in trees for i in range(3))
            assert not any(name.endswith(' blue collar') for name in names),'Unsupported blue upper collars'
            assert first_hit(-.29,.25)[1]=='BR05 low satellite 0 red face','Red satellite fitting occluded'
            for j,(x,zz) in enumerate([(.29,.305),(.25,.22),(.33,.22)]):assert first_hit(x,zz)[1]==f'BR05 low satellite 1 blue face {j}','Blue satellite fitting occluded'
            features.update(actual_neck_radius=neck.x,actual_spire_foot_radius=roof.x,low_satellites=3,exposed_red_blue_fittings=4)
    maps={}
    for mat in {m for o in objects for m in o.data.materials}:
        shader=mat.node_tree.nodes.get('Principled BSDF')
        for kind,socket in [('colour','Base Color'),('roughness','Roughness')]:
            values,image=effective_pixels(shader.inputs[socket],kind);assert np.ptp(values)>.005
            maps[mat.name+'/'+kind]=dict(size=list(image.size),effective_pixel_sha256=hashlib.sha256(values.tobytes()).hexdigest())
    assert len(maps)==10
    return dict(positive_closed_meshes=len(objects),part_contacts=contacts,all_parts_contact_checked=True,joined_assembly=True,packed_maps=maps,**features)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=CASES,required=True)
    key=parser.parse_args(sys.argv[sys.argv.index('--')+1:]).model;output,media=folders(key);meta=json.loads((output/'model.json').read_text())
    assert meta['source_blend_sha256']==sha(source(key))
    for kind in ['blend','glb']:assert meta[kind+'_sha256']==sha(output/('model.'+kind))
    assert meta['generator_sha256']==sha(Path(__file__).with_name('refine_braccatian_clan_complexes.py'))
    for name,value in meta['dependency_sha256'].items():assert sha(Path(__file__).with_name(name))==value
    for name,value in meta['texture_sha256'].items():assert sha(ROOT/name)==value
    for field,name in [('lore_sha256','braccatian-lore-evidence.json'),('reference_sha256','braccatian-refining-baseline.json'),('functional_sha256','functional-text-index.json')]:assert meta[field]==sha(ROOT/'sources/docs/reconstruction/models'/name)
    bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'))
    native=snapshot();native_structure=structure(key);views=['front-quarter','front','equipment-detail']+([] if key=='br01' else ['crown-detail'])
    for view in views:
        fit_camera(VIEWS[view],selected(view));bpy.context.scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    for obj in list(bpy.context.scene.objects):
        if obj.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
    for mat in list(bpy.data.materials):bpy.data.materials.remove(mat,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(output/'model.glb'))
    imported=snapshot();imported_structure=structure(key)
    assert native.keys()==imported.keys() and native_structure['packed_maps']==imported_structure['packed_maps']
    error=0
    for name in native:
        error=max(error,drift(native[name]['points'],imported[name]['points']),drift(imported[name]['points'],native[name]['points']))
        assert native[name]['materials']==imported[name]['materials'] and native[name]['parent']==imported[name]['parent']
    assert error<.0001
    renders={}
    for view in views:
        fit_camera(VIEWS[view],selected(view));path=media/('imported-'+view+'.png');bpy.context.scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        renders[view]=compare_render(media/(view+'.png'),path,view in ['front-quarter','front'])
    report=dict(issue=190,model=key,blender=bpy.app.version_string,source_blend_sha256=sha(source(key)),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),
      generator_sha256=meta['generator_sha256'],verifier_sha256=sha(Path(__file__)),verifier_dependencies_sha256={n:sha(Path(__file__).with_name(n)) for n in ['verify_refined_braccatian_pithoi.py','verify_rigellian_crowns.py']},
      native_mesh_count=len(native),imported_mesh_count=len(imported),maximum_native_imported_position_error=error,native_structure=native_structure,imported_structure=imported_structure,renders=renders,
      preserved_geometry_claim='None: prior generic source preserved separately',acceptance='Actual native/import checks; final artistic/game calibration open')
    (media/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('BRACCATIAN_CLAN_NATIVE_GLB_VERIFIED',key,len(native),error,flush=True)


if __name__=='__main__':main()
