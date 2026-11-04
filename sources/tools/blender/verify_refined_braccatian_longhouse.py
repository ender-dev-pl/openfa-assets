"""Validate actual BR06 entrance voids, joined halls, tapered towers and portable output."""
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
from refine_braccatian_longhouse import ROOT,VIEWS,folders,source,selected,fit_camera,sha
from verify_refined_braccatian_pithoi import tree,inside,effective_pixels
from verify_rigellian_crowns import snapshot,drift,compare_render


def structure():
    root=bpy.data.objects['PlacementRoot'];old=json.loads(source().with_suffix('.json').read_text())
    assert root['catalogue_id']=='openfa:building/legacy/068'
    assert [root['footprint_width'],root['footprint_height']]==old['footprint']==[3,3]
    assert max(abs(root.matrix_world[i][j]-(i==j)) for i in range(4) for j in range(4))<1e-6
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objects)==61
    collections=[c for c in bpy.data.collections if c.asset_data]
    assert len(collections)==1 and all(o.name in collections[0].objects for o in objects+[root])
    trees={};samples={};bounds={}
    for obj in objects:
        assert obj.parent==root and obj.data.uv_layers and not obj.modifiers,obj.name
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges),(obj.name,'Open/inconsistent geometry')
        assert bm.calc_volume(signed=True)>1e-9,(obj.name,'Nonpositive solid')
        bm.free();trees[obj.name]=tree(obj)
        pts=[obj.matrix_world@v.co for v in obj.data.vertices]
        bounds[obj.name]=[(min(p[k] for p in pts),max(p[k] for p in pts)) for k in range(3)]
        # Actual triangle centroids, slightly inside each solid, avoid export seam boundaries.
        stride=max(1,len(obj.data.polygons)//1000)
        samples[obj.name]=[obj.matrix_world@(p.center-p.normal*.0001) for p in list(obj.data.polygons)[::stride]]
        samples[obj.name]+=pts[::max(1,len(pts)//1000)]
    assert not any(o.animation_data for o in bpy.context.scene.objects),'Unsupported operating motion'
    points=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
    assert abs(min(p.z for p in points))<1e-6 and abs(max(p.z for p in points)-2.55)<1e-4
    assert max(abs(p.x) for p in points)<1.13 and max(abs(p.y) for p in points)<.85
    # Geometric intersection graph: all components must actually touch the joined hall assembly.
    graph={o.name:set() for o in objects};contacts=[]
    names=list(graph)
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
    assert reached==set(names),('Disconnected assembly parts',set(names)-reached)
    entrances=[];sections=[]
    for i,(x,height) in enumerate(zip([-.72,0,.72],[2.23,2.04,1.85])):
        prefix=f'BR06 segment {i} '
        # The entrance stays empty through the front half metre, below its arched crown.
        for z in [.08,.17,.27]:
            origin=Vector((x,-.92,z));direction=Vector((0,1,0))
            assert not any(bvh.ray_cast(origin,direction,.56)[0] is not None for bvh in trees.values()),('Blocked entrance',i,z)
        arch=trees[prefix+'entrance open rose arch']
        assert arch.ray_cast(Vector((x+.24,-.92,.12)),Vector((0,1,0)),.56)[0] is not None,'Missing arch jamb'
        assert arch.ray_cast(Vector((x,-.92,.40)),Vector((0,1,0)),.56)[0] is not None,'Missing arch crown'
        entrances.append(dict(segment=i,clear_depth=.56,clear_heights=[.08,.17,.27]))
        tower=trees[prefix+'terraced gold tower'];radii=[]
        for z in [.75,height-.15]:
            hit=tower.ray_cast(Vector((x+2,.12,z)),Vector((-1,0,0)),4)[0];assert hit is not None
            radii.append(hit.x-x)
        assert .22<radii[0]<.25 and radii[0]/radii[1]>2.3,'Lost broad-foot stepped tower taper'
        sections.append(radii)
        collar=bpy.data.objects[prefix+'red upper collar']
        assert all('red-field' in m.name for m in collar.data.materials),'Red collar replaced with another colour'
    maps={}
    for mat in {m for o in objects for m in o.data.materials}:
        shader=mat.node_tree.nodes.get('Principled BSDF')
        for kind,socket in [('colour','Base Color'),('roughness','Roughness')]:
            values,image=effective_pixels(shader.inputs[socket],kind);assert np.ptp(values)>.005
            maps[mat.name+'/'+kind]=dict(size=list(image.size),effective_pixel_sha256=hashlib.sha256(values.tobytes()).hexdigest())
    assert len(maps)==8
    return dict(positive_closed_meshes=len(objects),part_contacts=contacts,all_parts_contact_checked=True,
       joined_assembly=True,open_arched_entrances=entrances,measured_tower_sections=sections,packed_maps=maps)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=['br06'],default='br06')
    parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    output,media=folders();meta=json.loads((output/'model.json').read_text())
    assert meta['source_blend_sha256']==sha(source())
    for kind in ['blend','glb']:assert meta[kind+'_sha256']==sha(output/('model.'+kind))
    assert meta['generator_sha256']==sha(Path(__file__).with_name('refine_braccatian_longhouse.py'))
    for name,value in meta['dependency_sha256'].items():assert sha(Path(__file__).with_name(name))==value
    for name,value in meta['texture_sha256'].items():assert sha(ROOT/name)==value
    for field,name in [('lore_sha256','braccatian-lore-evidence.json'),('reference_sha256','braccatian-refining-baseline.json'),('functional_sha256','functional-text-index.json')]:assert meta[field]==sha(ROOT/'sources/docs/reconstruction/models'/name)
    bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'))
    native=snapshot();native_structure=structure();views=['front-quarter','front','entrance-detail']
    for view in views:
        fit_camera(VIEWS[view],selected(view));bpy.context.scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    for obj in list(bpy.context.scene.objects):
        if obj.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
    for mat in list(bpy.data.materials):bpy.data.materials.remove(mat,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(output/'model.glb'))
    imported=snapshot();imported_structure=structure()
    assert native.keys()==imported.keys() and native_structure['packed_maps']==imported_structure['packed_maps']
    error=0
    for name in native:
        error=max(error,drift(native[name]['points'],imported[name]['points']),drift(imported[name]['points'],native[name]['points']))
        assert native[name]['materials']==imported[name]['materials'] and native[name]['parent']==imported[name]['parent']
    assert error<.0001
    renders={}
    for view in views:
        fit_camera(VIEWS[view],selected(view));path=media/('imported-'+view+'.png');bpy.context.scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        renders[view]=compare_render(media/(view+'.png'),path,view!='entrance-detail')
    report=dict(issue=190,model='br06',blender=bpy.app.version_string,source_blend_sha256=sha(source()),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),
      generator_sha256=meta['generator_sha256'],verifier_sha256=sha(Path(__file__)),verifier_dependencies_sha256={n:sha(Path(__file__).with_name(n)) for n in ['verify_refined_braccatian_pithoi.py','verify_rigellian_crowns.py']},
      native_mesh_count=len(native),imported_mesh_count=len(imported),maximum_native_imported_position_error=error,native_structure=native_structure,imported_structure=imported_structure,renders=renders,
      preserved_geometry_claim='None: prior generic towers preserved separately',acceptance='Actual native/import validation; artistic/game calibration remains open')
    (media/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('BRACCATIAN_LONGHOUSE_NATIVE_GLB_VERIFIED',len(native),error,flush=True)


if __name__=='__main__':main()
