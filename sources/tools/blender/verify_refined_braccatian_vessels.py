"""Verify distinct Source/Anchor/fusion-plant construction in native Blender and GLB."""
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
from refine_braccatian_vessels import ROOT,CASES,VIEWS,folders,source,selected,fit_camera,sha,profile_radius,authored
from verify_refined_braccatian_pithoi import tree,inside,effective_pixels
from verify_rigellian_crowns import snapshot,drift,compare_render


def structure(key):
    case=CASES[key];prefix=key.upper();lower,upper=case['lower'],case['upper']
    root=bpy.data.objects['PlacementRoot']
    old=json.loads(source(key).with_suffix('.json').read_text())
    assert root['catalogue_id']==f"openfa:building/legacy/{case['number']:03}"
    assert [root['footprint_width'],root['footprint_height']]==old['footprint']==[2,2]
    assert max(abs(root.matrix_world[i][j]-(i==j)) for i in range(4) for j in range(4))<1e-6
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    assert len(objects)=={'br04':28,'br14':30,'br15':20}[key]
    trees={}
    for obj in objects:
        assert obj.parent==root and obj.data.uv_layers and not obj.modifiers,obj.name
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        assert all(e.is_manifold and e.is_contiguous for e in bm.edges),(obj.name,'Open or inconsistently wound geometry')
        assert bm.calc_volume(signed=True)>1e-8,(obj.name,'Nonpositive volume')
        bm.free();trees[obj.name]=tree(obj)
    collections=[c for c in bpy.data.collections if c.asset_data]
    assert len(collections)==1 and all(o.name in collections[0].objects for o in objects+[root])
    assert not any(o.animation_data for o in bpy.context.scene.objects),'Unsupported operating loop'
    pts=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
    expected_height={'br04':2.46,'br14':2.18,'br15':2.43}[key]
    assert abs(min(p.z for p in pts))<1e-6 and abs(max(p.z for p in pts)-expected_height)<1e-4
    assert max(abs(p.x) for p in pts)<.63 and max(abs(p.y) for p in pts)<.66

    def radial(name,z):
        hit=trees[prefix+' '+name].ray_cast(Vector((2,0,z)),Vector((-1,0,0)),4)[0]
        assert hit is not None
        return hit.x

    if key=='br14':
        sections=[radial('upper body',z) for z in [1.23,1.42,1.64]]
        assert min(sections[0],sections[2])/sections[1]>1.25,'Anchor shoulder/waist missing'
        assert radial('upper body',2.06)/sections[2]>.55,'Anchor dome regressed to a pointed cap'
        assert not any('mast' in o.name or 'collar' in o.name for o in objects),'Anchor grew an unsupported terminal'
    elif key=='br04':
        sections=[radial('lower body',.55),radial('lower body',1.30),radial('upper body',1.75)]
        assert sections[2]/sections[1]>4 and .38<sections[0]<.42,'Source cylinder/narrow-neck/upper-vessel hierarchy missing'
    else:
        sections=[radial('lower body',.28),radial('lower body',.91),radial('upper body',1.32)]
        assert min(sections[0],sections[2])/sections[1]>3.5,'Fusion plant regressed to generic tower'
    contacts=[]

    def contact(a,b,p):
        a,b=prefix+' '+a,prefix+' '+b
        assert inside(trees[a],p) and inside(trees[b],p),(a,b,'Disconnected assembly',p)
        contacts.append(dict(parts=[a,b],point=list(p)))

    def attached(name,profile,x,z,body='upper body'):
        contact(body,name,(x,authored.skin(profile,x,z)+.006,z))

    contact('lower body','upper body',(0,0,{'br04':1.31,'br14':.98,'br15':.94}[key]))
    if key!='br14':
        contact('upper body','blue collar',(0,0,2.13 if key=='br04' else 1.825))
        contact('blue collar','single gold mast',(0,0,2.235 if key=='br04' else 1.935))
    if key=='br14':
        for i in range(12):
            if i==9:continue
            obj=bpy.data.objects[prefix+f' lower gold flute {i:02}']
            for z in [.20,.5,.8]:contact('lower body',obj.name.removeprefix(prefix+' '),obj.matrix_world@Vector((0,-.419,z)))
        attached('lower dark field',lower,0,.20,'lower body')
        for i,z in enumerate([.28,.49,.70]):
            attached(f'lower port rim {i}',lower,.063,z,'lower body')
            attached(f'lower port face {i}',lower,0,z,'lower body')
            ray=Vector((0,-2,z));direction=Vector((0,1,0))
            assert trees[prefix+f' lower port rim {i}'].ray_cast(ray,direction,3)[0] is None
            assert trees[prefix+f' lower port face {i}'].ray_cast(ray,direction,3)[0] is not None
        attached('middle gold field frame',upper,.20,1.38)
        for i in range(5):attached(f'middle dark field {i}',upper,-.16+i*.08,1.38)
        for name,x in [('broad gold upper fitting',.17),('upper dark fitting centre',0),('inner gold upper fitting',.08),('gold central fitting',0)]:attached(name,upper,x,1.78)
    elif key=='br04':
        for i in range(8):
            if i==6:continue
            obj=bpy.data.objects[prefix+f' lower cast rib {i}']
            for z in [.20,.50,.80]:contact('lower body',obj.name.removeprefix(prefix+' '),obj.matrix_world@Vector((0,-.394,z)))
        for sign in [-1,1]:attached('lower gold service rail '+str(sign),lower,sign*.20,.4,'lower body')
        for label,profile,z in [('lower high',lower,.98),('lower middle',lower,.735),('upper high',upper,2.005),('upper low',upper,1.51)]:
            contact('lower body' if profile==lower else 'upper body','rose band '+label,(profile_radius(profile,z)-.005,0,z))
        attached('lower gold fitting belt',lower,.30,.56,'lower body')
        for name,x in [('lower gold round fitting',.095),('lower dark round fitting',0),('lower gold centre',0)]:attached(name,lower,x,.56,'lower body')
        attached('bottom service rim',lower,.055,.18,'lower body')
        attached('bottom pale blue service face',lower,0,.18,'lower body')
        attached('upper dark equipment field',upper,0,1.77)
        for i,z in enumerate([1.70,1.84]):attached(f'upper pale equipment face {i}',upper,0,z)
        for sign in [-1,1]:attached('upper gold side rail '+str(sign),upper,sign*.09,1.77)
    else:
        contact('lower body','gold waist ring',(profile_radius(lower,.90)-.005,0,.90))
        attached('upper gold face bezel',upper,.15,1.36)
        attached('upper dark grille backing',upper,0,1.36)
        for i,x in enumerate([-.075,0,.075]):attached(f'upper gold grille bar {i}',upper,x,1.36)
        for name,x in [('lower gold face bezel',-.30),('lower dark face backing',-.16),('lower inner gold face',-.10),('lower gold centre',-.16)]:attached(name,lower,x,.42,'lower body')
        for i,(x,y) in enumerate([(.22,-.51),(.40,-.40)]):
            contact('lower body',f'front upright {i}',(x,y,.30))
            contact(f'front upright {i}',f'front upright foot {i}',(x,y,.04))
            contact(f'front upright {i}',f'front upright collar {i}',(x,y,.60))
    # Every authored part must participate in a measured physical attachment.
    connected={n for c in contacts for n in c['parts']}
    assert connected=={o.name for o in objects},('Untested parts',set(trees)-connected)
    maps={}
    for material in {m for o in objects for m in o.data.materials}:
        shader=material.node_tree.nodes.get('Principled BSDF')
        for kind,socket in [('colour','Base Color'),('roughness','Roughness')]:
            values,image=effective_pixels(shader.inputs[socket],kind)
            assert np.ptp(values)>.005
            maps[material.name+'/'+kind]=dict(size=list(image.size),effective_pixel_sha256=hashlib.sha256(values.tobytes()).hexdigest())
    assert len(maps)=={'br04':10,'br14':10,'br15':8}[key]
    return dict(positive_closed_meshes=len(objects),measured_radial_sections=sections,part_contacts=contacts,
                all_parts_contact_checked=True,packed_maps=maps,static_clip_policy=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=CASES,required=True)
    key=parser.parse_args(sys.argv[sys.argv.index('--')+1:]).model
    output,media=folders(key);meta=json.loads((output/'model.json').read_text())
    assert meta['source_blend_sha256']==sha(source(key))
    for kind in ['blend','glb']:assert meta[kind+'_sha256']==sha(output/('model.'+kind))
    assert meta['generator_sha256']==sha(Path(__file__).with_name('refine_braccatian_vessels.py'))
    for field,name in [('lore_sha256','braccatian-lore-evidence.json'),('reference_sha256','braccatian-refining-baseline.json'),('functional_sha256','functional-text-index.json')]:assert meta[field]==sha(ROOT/'sources/docs/reconstruction/models'/name)
    for name,value in meta['dependency_sha256'].items():assert sha(Path(__file__).with_name(name))==value
    for name,value in meta['texture_sha256'].items():assert sha(ROOT/name)==value
    bpy.ops.wm.open_mainfile(filepath=str(output/'model.blend'))
    native=snapshot();native_structure=structure(key)
    views=['front-quarter','front','equipment-detail']
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
        generator_sha256=meta['generator_sha256'],verifier_sha256=sha(Path(__file__)),
        verifier_dependencies_sha256={n:sha(Path(__file__).with_name(n)) for n in ['verify_refined_braccatian_pithoi.py','verify_rigellian_crowns.py']},
        native_mesh_count=len(native),imported_mesh_count=len(imported),maximum_native_imported_position_error=error,
        native_structure=native_structure,imported_structure=imported_structure,renders=renders,
        preserved_geometry_claim='None: earlier placeholder preserved separately',acceptance='Actual native/import technical checks; final artistic acceptance and gameplay calibration open')
    (media/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('BRACCATIAN_VESSEL_NATIVE_GLB_VERIFIED',key,len(native),error,flush=True)


if __name__=='__main__':main()
