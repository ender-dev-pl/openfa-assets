"""Check actual BR07/09/10 whole construction, entrance/slot voids, attachments and GLB parity."""
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
from refine_braccatian_public_facilities import ROOT,CASES,VIEWS,folders,source,selected,fit_camera,sha
from verify_refined_braccatian_pithoi import tree,inside,effective_pixels
from verify_rigellian_crowns import snapshot,drift,compare_render


def structure(key):
    root=bpy.data.objects['PlacementRoot'];old=json.loads(source(key).with_suffix('.json').read_text());number,_=CASES[key]
    assert root['catalogue_id']==f'openfa:building/legacy/{number:03}'
    assert [root['footprint_width'],root['footprint_height']]==old['footprint']
    assert max(abs(root.matrix_world[i][j]-(i==j)) for i in range(4) for j in range(4))<1e-6
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objects)=={'br07':37,'br09':29,'br10':37}[key]
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
    assert abs(min(p.z for p in points))<1e-6
    assert abs(max(p.z for p in points)-{'br07':2.05,'br09':2.33,'br10':2.40}[key])<1e-4
    assert max(abs(p.x) for p in points)<(.60 if key=='br09' else 1.20)
    assert max(abs(p.y) for p in points)<(.60 if key=='br09' else 1.20)
    graph={o.name:set() for o in objects};contacts=[];names=list(graph)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            if any(bounds[a][k][1]<bounds[b][k][0] or bounds[b][k][1]<bounds[a][k][0] for k in range(3)):continue
            hit=next((p for p in samples[a] if inside(trees[b],p)),None)
            if hit is None:hit=next((p for p in samples[b] if inside(trees[a],p)),None)
            if hit is not None:
                graph[a].add(b);graph[b].add(a);contacts.append(dict(parts=[a,b],point=list(hit)))
    reached=set();queue=[names[0]]
    while queue:
        name=queue.pop()
        if name in reached:continue
        reached.add(name);queue+=list(graph[name]-reached)
    assert reached==set(names),('Disconnected assembly',set(names)-reached)
    features={}

    def first_hit(x,z):
        origin=Vector((x,-3,z));direction=Vector((0,1,0));hits=[]
        for name,bvh in trees.items():
            hit,_,_,distance=bvh.ray_cast(origin,direction,6)
            if hit is not None:hits.append((distance,name))
        assert hits
        return min(hits)[1]

    if key=='br07':
        for z in [.10,.22]:
            assert not any(b.ray_cast(Vector((0,-1.20,z)),Vector((0,1,0)),.55)[0] is not None for b in trees.values()),'Entrance blocked'
        radii=[]
        for z in [.55,1.55]:
            hit=trees['BR07 broad domed hall'].ray_cast(Vector((3,0,z)),Vector((-1,0,0)),5)[0];assert hit is not None;radii.append(hit.x)
        assert radii[0]>1 and radii[0]/radii[1]>1.7,'Hall lost broad domed silhouette'
        assert sum(name.startswith('BR07 front pillar ') for name in names)==2
        assert sum(name.startswith('BR07 front gold globe ') for name in names)==2
        for i,(x,z) in enumerate([(0,1.59),(-.30,1.30),(.30,1.30),(0,1.16)]):
            assert first_hit(x,z)==('BR07 upper pale fitting' if i==0 else f'BR07 hall dark face {i}'),'Face fitting is occluded'
        features=dict(measured_dome_sections=radii,paired_front_pillars=2,clear_entrance=True,exposed_face_centres=4)
    elif key=='br09':
        for i in range(8):
            a=(i+.5)*math.tau/8;direction=Vector((-math.cos(a),-math.sin(a),0));origin=Vector((.45*math.cos(a),.45*math.sin(a),1.54))
            assert not any(b.ray_cast(origin,direction,.26)[0] is not None for b in trees.values()),'Upper cage became a solid cylinder'
        assert trees['BR09 upper cage upright 0'].ray_cast(Vector((.45,0,1.54)),Vector((-1,0,0)),.26)[0] is not None,'Missing actual cage rib'
        sections=[]
        for i,(x,y) in enumerate([(-.27,-.18),(.27,-.18),(0,.30)]):
            widths=[]
            for z in [.10,.60]:
                hit=trees[f'BR09 pyramidal support {i}'].ray_cast(Vector((x+2,y,z)),Vector((-1,0,0)),4)[0];assert hit is not None;widths.append(hit.x-x)
            assert widths[0]/widths[1]>2.2 and abs(bounds[f'BR09 pyramidal support {i}'][2][0])<1e-6
            sections.append(widths)
        for j,(x,z) in enumerate([(-.27,.33),(-.312,.24),(-.228,.24)]):assert first_hit(x,z)==f'BR09 foot blue fitting {j}','Blue face occluded'
        features=dict(actual_open_cage_intervals=8,grounded_pyramidal_supports=3,measured_support_sections=sections,exposed_blue_fittings=3)
    else:
        stairs=[bounds[f'BR10 access step {i}'] for i in range(3)]
        assert [round(b[2][1],3) for b in stairs]==[.12,.18,.24]
        assert stairs[0][1][0]<stairs[1][1][0]<stairs[2][1][0] and stairs[0][0][1]>stairs[1][0][1]>stairs[2][0][1],'Lost actual rising access steps'
        assert sum(name.startswith('BR10 side pyramidal module ') for name in names)==2
        assert sum(name.startswith('BR10 front gold fitting ') for name in names)==3
        for j,(x,z) in enumerate([(.59,.33),(.548,.24),(.632,.24)]):assert first_hit(x,z)==f'BR10 side blue port {j}','Blue face occluded'
        assert first_hit(.20,1.56)=='BR10 upper red face','Upper red face occluded'
        features=dict(actual_access_steps=3,side_pyramidal_modules=2,front_gold_fittings=3,exposed_blue_fittings=3,exposed_red_face=True)
    maps={}
    for mat in {m for o in objects for m in o.data.materials}:
        shader=mat.node_tree.nodes.get('Principled BSDF')
        for kind,socket in [('colour','Base Color'),('roughness','Roughness')]:
            values,image=effective_pixels(shader.inputs[socket],kind);assert np.ptp(values)>.005
            maps[mat.name+'/'+kind]=dict(size=list(image.size),effective_pixel_sha256=hashlib.sha256(values.tobytes()).hexdigest())
    assert len(maps)=={'br07':10,'br09':10,'br10':10}[key]
    return dict(positive_closed_meshes=len(objects),part_contacts=contacts,all_parts_contact_checked=True,joined_assembly=True,packed_maps=maps,**features)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=CASES,required=True)
    key=parser.parse_args(sys.argv[sys.argv.index('--')+1:]).model;output,media=folders(key);meta=json.loads((output/'model.json').read_text())
    assert meta['source_blend_sha256']==sha(source(key))
    for kind in ['blend','glb']:assert meta[kind+'_sha256']==sha(output/('model.'+kind))
    assert meta['generator_sha256']==sha(Path(__file__).with_name('refine_braccatian_public_facilities.py'))
    for name,value in meta['dependency_sha256'].items():assert sha(Path(__file__).with_name(name))==value
    for name,value in meta['texture_sha256'].items():assert sha(ROOT/name)==value
    for field,name in [('lore_sha256','braccatian-lore-evidence.json'),('reference_sha256','braccatian-refining-baseline.json'),('functional_sha256','functional-text-index.json')]:assert meta[field]==sha(ROOT/'sources/docs/reconstruction/models'/name)
    bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'))
    native=snapshot();native_structure=structure(key);views=['front-quarter','front','equipment-detail']
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
        renders[view]=compare_render(media/(view+'.png'),path,view!='equipment-detail')
    report=dict(issue=190,model=key,blender=bpy.app.version_string,source_blend_sha256=sha(source(key)),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),
      generator_sha256=meta['generator_sha256'],verifier_sha256=sha(Path(__file__)),verifier_dependencies_sha256={n:sha(Path(__file__).with_name(n)) for n in ['verify_refined_braccatian_pithoi.py','verify_rigellian_crowns.py']},
      native_mesh_count=len(native),imported_mesh_count=len(imported),maximum_native_imported_position_error=error,native_structure=native_structure,imported_structure=imported_structure,renders=renders,
      preserved_geometry_claim='None: prior generic study preserved separately',acceptance='Actual native/import checks; artistic/game calibration remains open')
    (media/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('BRACCATIAN_PUBLIC_NATIVE_GLB_VERIFIED',key,len(native),error,flush=True)


if __name__=='__main__':main()
