"""Test the actual BR03/13/16 broad bases, auxiliary tower, straight masts and gaps."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector,Matrix
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from refine_braccatian_mast_facilities import ROOT,CASES,VIEWS,folders,source,selected,fit_camera,sha,authored,profile_radius,SHIELD_CENTRES,SHIELD_BELL,SHIELD_HANDLE,SENSOR_MAIN,SENSOR_SIDE,SENSOR_LOWER,SENSOR_SIDE_BASE,AEGIS_FOOT,AEGIS_COLUMN
from verify_refined_braccatian_pithoi import tree,inside,effective_pixels
from verify_rigellian_crowns import snapshot,drift,compare_render


def structure(key):
    prefix=key.upper();root=bpy.data.objects['PlacementRoot'];number,_=CASES[key]
    old=json.loads(source(key).with_suffix('.json').read_text())
    assert root['catalogue_id']==f'openfa:building/legacy/{number:03}'
    assert [root['footprint_width'],root['footprint_height']]==old['footprint']
    assert max(abs(root.matrix_world[i][j]-(i==j)) for i in range(4) for j in range(4))<1e-6
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    assert len(objects)=={'br03':24,'br13':25,'br16':22}[key]
    trees={}
    for obj in objects:
        assert obj.parent==root and obj.data.uv_layers and not obj.modifiers,obj.name
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges),(obj.name,'Open or inconsistently wound geometry')
        assert bm.calc_volume(signed=True)>1e-9,(obj.name,'Nonpositive geometry')
        bm.free();trees[obj.name]=tree(obj)
    collections=[c for c in bpy.data.collections if c.asset_data]
    assert len(collections)==1 and all(o.name in collections[0].objects for o in objects+[root])
    assert not any(o.animation_data for o in bpy.context.scene.objects),'Unestablished operating motion'
    points=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
    assert abs(min(p.z for p in points))<1e-6
    assert abs(max(p.z for p in points)-{'br03':1.31,'br13':3.00,'br16':2.26}[key])<1e-4
    assert max(abs(p.x) for p in points)<(1.18 if key=='br03' else .70)
    assert max(abs(p.y) for p in points)<(1.18 if key=='br03' else .70)
    contacts=[];features={}

    def contact(a,b,p):
        a,b=prefix+' '+a,prefix+' '+b
        assert inside(trees[a],p) and inside(trees[b],p),(a,b,'Disconnected part',list(p))
        contacts.append(dict(parts=[a,b],point=list(p)))

    def point(profile,x,z,xy=(0,0),rotation=0):
        p=Matrix.Rotation(rotation,3,'Z')@Vector((x,authored.skin(profile,x,z)+.006,z))
        return p+Vector((*xy,0))

    if key=='br03':
        sections=[]
        for i,xy in enumerate(SHIELD_CENTRES):
            base=f'unit {i} '
            contact(base+'continuous flared bell',base+'banded handle',(*xy,.66))
            z=.0925;r=profile_radius(SHIELD_BELL,z)
            contact(base+'continuous flared bell',base+'rose hem trim',(xy[0]+r-.005,xy[1],z))
            for j,z in enumerate([.7725,1.0425]):
                r=profile_radius(SHIELD_HANDLE,z)
                contact(base+'banded handle',base+f'blue handle band {j}',(xy[0]+r-.005,xy[1],z))
            contact(base+'continuous flared bell',base+'front gold rim',point(SHIELD_BELL,.063,.46,xy))
            contact(base+'continuous flared bell',base+'red front field',point(SHIELD_BELL,0,.46,xy))
            contact(base+'continuous flared bell',base+'pale side field',point(SHIELD_BELL,0,.48,xy,-math.pi/3))
            body=trees[prefix+' '+base+'continuous flared bell'];radii=[]
            for z in [.075,.33,.59]:
                hit=body.ray_cast(Vector((xy[0]+2,xy[1],z)),Vector((-1,0,0)),4)[0]
                assert hit is not None
                radii.append(hit.x-xy[0])
            assert .52<radii[0]<.56 and radii[0]/radii[1]>1.7 and radii[1]/radii[2]>1.5,'Bell casing lacks a continuous outward flare'
            obj=bpy.data.objects[prefix+' '+base+'continuous flared bell']
            pts=[obj.matrix_world@v.co for v in obj.data.vertices]
            assert abs(min(p.z for p in pts))<1e-6,'An independent unit is not grounded'
            # Weld coincident glTF UV/normal seams before physical connectivity analysis.
            bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
            remaining=set(bm.verts);components=0
            while remaining:
                queue=[remaining.pop()];components+=1
                while queue:
                    vertex=queue.pop()
                    for edge in vertex.link_edges:
                        other=edge.other_vert(vertex)
                        if other in remaining:remaining.remove(other);queue.append(other)
            bm.free();assert components==1,'Bell body is an assembly of disconnected blobs'
            sections.append(radii)
        features.update(independent_grounded_units=3,measured_bell_sections=sections,continuous_flared_casings=True)
    elif key=='br13':
        main,side=SENSOR_MAIN,SENSOR_SIDE
        contact('main tapered body','main gold capsule',(*main,1.81))
        contact('main gold capsule','main blue collar',(*main,2.33))
        contact('main blue collar','main single mast',(*main,2.41))
        contact('main tapered body','main dark equipment backing',point(SENSOR_LOWER,0,1.20,main))
        for i,z in enumerate([1.12,1.32,1.52]):contact('main tapered body',f'main pale face {i}',point(SENSOR_LOWER,0,z,main))
        contact('main tapered body','main lower gold service field',point(SENSOR_LOWER,0,.40,main))
        for i,z in enumerate([.37,.50,.63,.76,.89]):contact('main tapered body',f'main service dark division {i}',point(SENSOR_LOWER,0,z,main))
        contact('side lower cylinder','side gold globe',(*side,.84))
        contact('side gold globe','side blue cap',(*side,1.235))
        contact('side lower cylinder','side dark service field',point(SENSOR_SIDE_BASE,0,.30,side))
        for i,z in enumerate([.20,.34,.48,.62]):contact('side lower cylinder',f'side gold field division {i}',point(SENSOR_SIDE_BASE,0,z,side))
        start=Vector((*side,1.31));elbow=Vector((*side,1.75));end=Vector((*main,1.89));direction=(end-elbow).normalized()
        contact('side blue cap','visible link upright',start+Vector((0,0,.012)))
        contact('visible link upright','visible link elbow',elbow-Vector((0,0,.012)))
        contact('visible link crosspiece','visible link elbow',elbow+direction*.012)
        contact('visible link crosspiece','main gold capsule',end-direction*.012)
        for name in ['main tapered body','side lower cylinder']:
            pts=[bpy.data.objects[prefix+' '+name].matrix_world@v.co for v in bpy.data.objects[prefix+' '+name].data.vertices]
            assert abs(min(p.z for p in pts))<1e-6
        assert main[0]-side[0]>.45,'Auxiliary tower lost its lateral separation'
        features.update(auxiliary_grounded_tower=True,physical_link=True)
    else:
        contact('rose dome foot','central gold column',(0,0,.44))
        contact('central gold column','upper gold globe',(0,0,1.095))
        for name,x in [('foot broad gold fitting',.11),('foot dark fitting backing',0),('foot central gold fitting',0)]:contact('rose dome foot',name,point(AEGIS_FOOT,x,.22))
        contact('central gold column','column dark field backing',point(AEGIS_COLUMN,0,.70))
        for i,x in enumerate([-.10,0,.10]):contact('central gold column',f'red vertical field {i}',point(AEGIS_COLUMN,x,.70))
        for i in range(8):
            phi=math.tau*i/8
            contact('upper gold globe',f'upper globe lobe {i}',(.165*math.cos(phi),-.065,1.29+.165*math.sin(phi)))
        for sign in [-1,1]:
            contact('central gold column','gold mast crossarm '+str(sign),(sign*.02,0,.65))
            contact('gold mast crossarm '+str(sign),'straight side mast '+str(sign),(sign*.475,0,.65))
            obj=bpy.data.objects[prefix+' straight side mast '+str(sign)]
            mid=[obj.matrix_world@v.co for v in obj.data.vertices if .9<v.co.z<1.8]
            assert mid and max(abs(p.x-sign*.48) for p in mid)<.029,'Mast is not straight'
            origin=Vector((sign*.35,-2,1.30));direction=Vector((0,1,0))
            assert all(bvh.ray_cast(origin,direction,4)[0] is None for bvh in trees.values()),'Gold assembly closed the clear side gap'
        features.update(straight_mast_pair=True,actual_side_gaps=True,complete_central_column_and_globe=True)
    connected={n for sample in contacts for n in sample['parts']}
    assert connected==set(trees),('Untested attachment',set(trees)-connected)
    maps={}
    for material in {m for obj in objects for m in obj.data.materials}:
        shader=material.node_tree.nodes.get('Principled BSDF')
        for kind,socket in [('colour','Base Color'),('roughness','Roughness')]:
            values,image=effective_pixels(shader.inputs[socket],kind)
            assert np.ptp(values)>.005
            maps[material.name+'/'+kind]=dict(size=list(image.size),effective_pixel_sha256=hashlib.sha256(values.tobytes()).hexdigest())
    assert len(maps)=={'br03':10,'br13':10,'br16':8}[key]
    return dict(positive_closed_meshes=len(objects),part_contacts=contacts,all_parts_contact_checked=True,packed_maps=maps,static_clip_policy=True,**features)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=CASES,required=True)
    key=parser.parse_args(sys.argv[sys.argv.index('--')+1:]).model;output,media=folders(key)
    meta=json.loads((output/'model.json').read_text())
    assert meta['source_blend_sha256']==sha(source(key))
    for kind in ['blend','glb']:assert meta[kind+'_sha256']==sha(output/('model.'+kind))
    assert meta['generator_sha256']==sha(Path(__file__).with_name('refine_braccatian_mast_facilities.py'))
    for name,value in meta['dependency_sha256'].items():assert sha(Path(__file__).with_name(name))==value
    for name,value in meta['texture_sha256'].items():assert sha(ROOT/name)==value
    for field,name in [('lore_sha256','braccatian-lore-evidence.json'),('reference_sha256','braccatian-refining-baseline.json'),('functional_sha256','functional-text-index.json')]:assert meta[field]==sha(ROOT/'sources/docs/reconstruction/models'/name)
    bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'))
    native=snapshot();native_structure=structure(key);views=['front-quarter','front','equipment-detail']
    for view in views:
        fit_camera(VIEWS[view],selected(view));bpy.context.scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    for obj in list(bpy.context.scene.objects):
        if obj.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
    for material in list(bpy.data.materials):bpy.data.materials.remove(material,do_unlink=True)
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
      preserved_geometry_claim='None: original placeholder preserved separately',acceptance='Actual native/import checks and rendered review; final art/game calibration open')
    (media/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('BRACCATIAN_MAST_NATIVE_GLB_VERIFIED',key,len(native),error,flush=True)


if __name__=='__main__':main()
