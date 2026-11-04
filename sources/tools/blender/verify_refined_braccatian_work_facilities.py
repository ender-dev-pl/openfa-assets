"""Validate actual six-spire wards, connected Forge branches and flat-capped extractor assembly."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from refine_braccatian_work_facilities import ROOT,CASES,VIEWS,folders,source,selected,fit_camera,sha
from verify_refined_braccatian_pithoi import tree,inside,effective_pixels
from verify_rigellian_crowns import snapshot,drift,compare_render


def structure(key):
    root=bpy.data.objects['PlacementRoot'];old=json.loads(source(key).with_suffix('.json').read_text());number,_=CASES[key]
    assert root['catalogue_id']==f'openfa:building/legacy/{number:03}'
    assert [root['footprint_width'],root['footprint_height']]==old['footprint']
    assert max(abs(root.matrix_world[i][j]-(i==j)) for i in range(4) for j in range(4))<1e-6
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objects)=={'br08':67,'br17':29,'br21':20}[key]
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
    assert abs(min(p.z for p in points))<1e-6 and abs(max(p.z for p in points)-{'br08':2.68,'br17':2.25,'br21':1.50}[key])<1e-4
    assert max(abs(p.x) for p in points)<(.60 if key=='br21' else 1.07)
    assert max(abs(p.y) for p in points)<(.60 if key=='br21' else 1.07)
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

    def first_hit(origin,direction):
        hits=[]
        for name,bvh in trees.items():
            hit,_,_,distance=bvh.ray_cast(Vector(origin),Vector(direction),6)
            if hit is not None:hits.append((distance,name,hit))
        assert hits
        return min(hits,key=lambda item:item[0])

    features={}
    if key=='br08':
        assert sum(name.endswith(' blue collar') for name in names)==6,'Legacy has six blue-collared towers, not five'
        sections=[]
        for i,(x,heights) in enumerate(zip([-.65,0,.65],[(2.26,2.00),(2.50,1.80),(2.26,2.00)])):
            for z in [.08,.17,.27]:
                assert not any(b.ray_cast(Vector((x,-.92,z)),Vector((0,1,0)),.56)[0] is not None for b in trees.values()),('Blocked ward entrance',i,z)
            arch=trees[f'BR08 ward {i} open entrance arch']
            assert arch.ray_cast(Vector((x+.24,-.92,.12)),Vector((0,1,0)),.56)[0] is not None
            assert arch.ray_cast(Vector((x,-.92,.40)),Vector((0,1,0)),.56)[0] is not None
            for j,(y,height) in enumerate(zip([.23,-.28],heights)):
                widths=[];name=f'BR08 ward {i} slim tower {j}'
                for zz in [.75,height-.34]:
                    hit=trees[name].ray_cast(Vector((x+2,y,zz)),Vector((-1,0,0)),4)[0];assert hit is not None;widths.append(hit.x-x)
                assert .13<widths[0]<.17 and widths[0]/widths[1]>3,'Lost slim tapered ward spire'
                sections.append(widths)
        features=dict(actual_blue_collared_towers=6,open_ward_entrances=3,measured_tower_sections=sections)
    elif key=='br17':
        sections=[]
        for zz in [.35,1.20]:
            hit=trees['BR17 tall main core'].ray_cast(Vector((2,0,zz)),Vector((-1,0,0)),4)[0];assert hit is not None;sections.append(hit.x+.14)
        assert all(abs(r-.30)<.001 for r in sections),'Main core regressed to generic spire'
        hall=[]
        for zz in [.10,.52,.70,.88]:
            hit=trees['BR17 layered low side hall'].ray_cast(Vector((2,.05,zz)),Vector((-1,0,0)),4)[0];assert hit is not None;hall.append(hit.x-.48)
        assert hall[0]>.35 and hall[1]/hall[2]>1.5 and hall[3]>.26,'Lost layered low side hall'
        for i,zz in enumerate([.33,.60,.87,1.10]):assert first_hit((-.56,-3,zz),(0,1,0))[1]==f'BR17 left red service field {i}','Red equipment hidden'
        for i,x in enumerate([-.24,-.14,-.04]):assert first_hit((x,-3,.75),(0,1,0))[1]==f'BR17 main long dark slot {i}','Long core slot hidden'
        assert all(f'BR17 paired upper tip {i}' in trees for i in range(2))
        globe=bounds['BR17 upper service gold globe'];assert globe[2][0]<1.92 and globe[2][1]>2.16
        features=dict(measured_main_core_sections=sections,measured_side_hall_sections=hall,visible_red_fields=4,visible_long_core_slots=3,paired_upper_tips=2,service_globe=True)
    else:
        radii=[]
        for zz in [.30,.75,1.20]:
            hit=trees['BR21 tiered cylindrical machine'].ray_cast(Vector((2,-.13,zz)),Vector((-1,0,0)),4)[0];assert hit is not None;radii.append(hit.x+.12)
        assert abs(radii[0]-.32)<.001 and abs(radii[2]-.29)<.001 and radii[1]/max(radii[0],radii[2])>1.2,'Broad machine shoulder missing'
        centre=first_hit((-.12,-.13,3),(0,0,-1));rim=first_hit((.13,-.13,3),(0,0,-1))
        assert centre[1]=='BR21 upper inset gold plate' and rim[1]=='BR21 flat upper rose rim'
        assert abs(centre[2].z-1.483)<1e-4 and abs(rim[2].z-1.50)<1e-4 and rim[2].z-centre[2].z<.025,'Upper end became a dome/mast/open shaft'
        for i,x in enumerate([.28,.39,.50]):assert first_hit((x,0,3),(0,0,-1))[1]==f'BR21 sloping dark equipment slot {i}','Sloping equipment field hidden'
        assert first_hit((.014,-3,.36),(0,1,0))[1]=='BR21 long red service field'
        assert first_hit((.08,-3,.36),(0,1,0))[1]=='BR21 short red service field'
        features=dict(measured_machine_sections=radii,actual_flat_top_heights=[centre[2].z,rim[2].z],visible_sloping_equipment_slots=3,visible_red_fields=2)
    maps={}
    for mat in {m for o in objects for m in o.data.materials}:
        shader=mat.node_tree.nodes.get('Principled BSDF')
        for kind,socket in [('colour','Base Color'),('roughness','Roughness')]:
            values,image=effective_pixels(shader.inputs[socket],kind);assert np.ptp(values)>.005
            maps[mat.name+'/'+kind]=dict(size=list(image.size),effective_pixel_sha256=hashlib.sha256(values.tobytes()).hexdigest())
    assert len(maps)==8
    return dict(positive_closed_meshes=len(objects),part_contacts=contacts,all_parts_contact_checked=True,joined_assembly=True,packed_maps=maps,**features)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=CASES,required=True)
    key=parser.parse_args(sys.argv[sys.argv.index('--')+1:]).model;output,media=folders(key);meta=json.loads((output/'model.json').read_text())
    assert meta['source_blend_sha256']==sha(source(key))
    for kind in ['blend','glb']:assert meta[kind+'_sha256']==sha(output/('model.'+kind))
    assert meta['generator_sha256']==sha(Path(__file__).with_name('refine_braccatian_work_facilities.py'))
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
      preserved_geometry_claim='None: prior generic source preserved separately',acceptance='Actual native/import validation; final artistic/game calibration open')
    (media/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('BRACCATIAN_WORK_NATIVE_GLB_VERIFIED',key,len(native),error,flush=True)


if __name__=='__main__':main()
