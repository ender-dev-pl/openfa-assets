"""Check actual BR22 jar profiles, attachments, authored finish and native/GLB renders."""
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_braccatian_pithoi import ROOT, SOURCE, OUTPUT, MEDIA, BASE, JAR, NECK, ORB, VIEWS, selected, fit_camera, sha, skin
from verify_rigellian_crowns import snapshot, drift, compare_render


def tree(obj):
    return BVHTree.FromPolygons([obj.matrix_world@v.co for v in obj.data.vertices],[list(p.vertices) for p in obj.data.polygons])


def inside(bvh, point):
    direction=Vector((.173,.291,.941)).normalized()
    hit,normal,_,_=bvh.ray_cast(Vector(point),direction,10)
    return hit is not None and normal.dot(direction)>0


def effective_pixels(socket, kind):
    link=socket.links[0]
    node=link.from_node
    channel=None
    if node.type=='SEPARATE_COLOR':
        channel=list(node.outputs).index(link.from_socket)
        node=node.inputs['Color'].links[0].from_node
    assert node.type=='TEX_IMAGE','Unrecognized exported shader graph'
    image=node.image
    assert image.packed_file and list(image.size)==[256,256]
    pixels=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(pixels)
    pixels=pixels.reshape(-1,4)
    assert np.isfinite(pixels).all()
    # glTF packs roughness in G and metallic in B. Compare effective shader
    # channels, not the unrelated RGB bytes of that packed transport image.
    values=pixels[:,:3] if kind=='colour' else pixels[:,channel if channel is not None else 0]
    return np.ascontiguousarray(values),image


def structure():
    root=bpy.data.objects['PlacementRoot']
    assert root['catalogue_id']=='openfa:building/legacy/084'
    assert root['footprint_width']==root['footprint_height']==2
    assert max(abs(root.matrix_world[i][j]-(i==j)) for i in range(4) for j in range(4))<1e-6
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    assert len(objects)==36
    trees,geometry={},{ }
    for obj in objects:
        assert obj.parent==root and obj.data.uv_layers,obj.name
        assert not obj.modifiers, (obj.name,'Unapplied portable geometry')
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        assert all(e.is_manifold for e in bm.edges),(obj.name,'Open geometry')
        assert all(e.is_contiguous for e in bm.edges),(obj.name,'Inconsistent winding')
        volume=bm.calc_volume(signed=True)
        assert volume>1e-8,(obj.name,'Nonpositive volume',volume)
        bm.free()
        trees[obj.name]=tree(obj)
        geometry[obj.name]=dict(volume=volume)
    assert not any(o.animation_data for o in bpy.context.scene.objects),'Unestablished idle mechanism'
    collections=[c for c in bpy.data.collections if c.asset_data]
    assert len(collections)==1
    assert all(o.name in collections[0].objects for o in objects+[root])
    # Sample the actual shell with radial rays. Profile constants alone are not proof.
    jar=trees['BR22 rose double shoulder jar']
    radii=[]
    for z in [1.23,1.42,1.64]:
        hit=jar.ray_cast(Vector((2,0,z)),Vector((-1,0,0)),4)[0]
        assert hit is not None
        radii.append(hit.x)
    assert min(radii[0],radii[2])/radii[1]>1.25,'Double shoulder/waist missing'
    points=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
    assert abs(min(p.z for p in points))<1e-6 and 2.97<max(p.z for p in points)<3.02
    assert max(abs(p.x) for p in points)<.63 and max(abs(p.y) for p in points)<.66,'Footprint/silhouette grew unexpectedly'
    contacts=[]

    def contact(a,b,p):
        assert inside(trees[a],p) and inside(trees[b],p),(a,b,'Disconnected assembly',p)
        contacts.append(dict(parts=[a,b],point=list(p)))

    contact('BR22 gold lower cylinder','BR22 rose double shoulder jar',(0,0,.98))
    contact('BR22 rose double shoulder jar','BR22 gold upper neck',(0,0,2.15))
    contact('BR22 gold upper neck','BR22 gold terminal globe',(0,0,2.675))
    contact('BR22 gold terminal globe','BR22 terminal top button',(0,0,2.96))
    for i in range(12):
        if i==9:continue
        obj=bpy.data.objects[f'BR22 lower gold flute {i:02}']
        for z in [.20,.50,.80]:
            p=obj.matrix_world@Vector((0,-.419,z))
            contact('BR22 gold lower cylinder',obj.name,p)
    contact('BR22 gold lower cylinder','BR22 front lower dark equipment backing',(0,-.42,.20))
    for i,z in enumerate([.28,.49,.70]):
        contact('BR22 gold lower cylinder',f'BR22 front lower gold port {i}',(0,-.415,z+.060))
        contact(f'BR22 front lower gold port {i}',f'BR22 front pale blue inset {i}',(.053,-.445,z))
        # The blue field must be exposed through the actual annular port.
        hit=trees[f'BR22 front pale blue inset {i}'].ray_cast(Vector((0,-2,z)),Vector((0,1,0)),3)[0]
        ring=trees[f'BR22 front lower gold port {i}'].ray_cast(Vector((0,-2,z)),Vector((0,1,0)),3)[0]
        assert hit is not None and ring is None,'Port face masked by solid gold cap'
    for name,profile,x,z in [
        ('BR22 front middle gold louver frame',JAR,.20,1.38),
        ('BR22 front upper broad gold round bezel',JAR,.17,1.78),
        ('BR22 front upper dark fitting backing',JAR,0,1.78),
        ('BR22 front upper inner gold round fitting',JAR,.08,1.78),
        ('BR22 front upper central gold fitting',JAR,0,1.78),
        ('BR22 upper neck red inset',NECK,0,2.38)]:
        parent='BR22 gold upper neck' if profile==NECK else 'BR22 rose double shoulder jar'
        contact(parent,name,(x,skin(profile,x,z)+.006,z))
    for i in range(5):
        x=-.16+i*.08;z=1.38
        contact('BR22 rose double shoulder jar',f'BR22 front dark louver field {i}',(x,skin(JAR,x,z)+.006,z))
    for z in [2.29,2.48]:
        contact('BR22 gold upper neck','BR22 upper neck gold transverse trim '+str(z),(0,skin(NECK,0,z)+.006,z))
    maps={}
    for material in {m for o in objects for m in o.data.materials}:
        shader=material.node_tree.nodes.get('Principled BSDF')
        for kind,socket in [('colour','Base Color'),('roughness','Roughness')]:
            values,image=effective_pixels(shader.inputs[socket],kind)
            assert np.ptp(values)>.005
            maps[material.name+'/'+kind]=dict(size=list(image.size),effective_pixel_sha256=__import__('hashlib').sha256(values.tobytes()).hexdigest())
    assert len(maps)==8
    return dict(positive_closed_meshes=len(objects),jar_radial_sections=radii,part_contacts=contacts,packed_maps=maps,static_clip_policy=True)


def main():
    meta=json.loads((OUTPUT/'model.json').read_text())
    assert meta['source_blend_sha256']==sha(SOURCE)
    for kind in ['blend','glb']:assert meta[kind+'_sha256']==sha(OUTPUT/('model.'+kind))
    assert meta['generator_sha256']==sha(Path(__file__).with_name('refine_braccatian_pithoi.py'))
    for field,name in [('lore_sha256','braccatian-lore-evidence.json'),('reference_sha256','braccatian-refining-baseline.json'),('functional_sha256','functional-text-index.json')]:
        assert meta[field]==sha(ROOT/'sources/docs/reconstruction/models'/name)
    for name,value in meta['dependency_sha256'].items():assert sha(Path(__file__).with_name(name))==value
    for name,value in meta['texture_sha256'].items():assert sha(ROOT/name)==value
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT/'model.blend'))
    native=snapshot();native_structure=structure()
    views=['front-quarter','front','jar-detail']
    for view in views:
        fit_camera(VIEWS[view],selected(view))
        bpy.context.scene.render.filepath=str(MEDIA/(view+'.png'))
        bpy.ops.render.render(write_still=True)
    for obj in list(bpy.context.scene.objects):
        if obj.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
    for material in list(bpy.data.materials):bpy.data.materials.remove(material,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(OUTPUT/'model.glb'))
    imported=snapshot();imported_structure=structure()
    assert native.keys()==imported.keys()
    assert native_structure['packed_maps']==imported_structure['packed_maps'],'Authored map pixels changed'
    error=0
    for name in native:
        error=max(error,drift(native[name]['points'],imported[name]['points']),drift(imported[name]['points'],native[name]['points']))
        assert native[name]['materials']==imported[name]['materials'] and native[name]['parent']==imported[name]['parent']
    assert error<.0001
    renders={}
    for view in views:
        fit_camera(VIEWS[view],selected(view))
        path=MEDIA/('imported-'+view+'.png')
        bpy.context.scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
        renders[view]=compare_render(MEDIA/(view+'.png'),path,view!='jar-detail')
    report=dict(issue=190,model='br22',blender=bpy.app.version_string,
                source_blend_sha256=sha(SOURCE),blend_sha256=sha(OUTPUT/'model.blend'),glb_sha256=sha(OUTPUT/'model.glb'),
                generator_sha256=meta['generator_sha256'],verifier_sha256=sha(Path(__file__)),
                native_mesh_count=len(native),imported_mesh_count=len(imported),maximum_native_imported_position_error=error,
                native_structure=native_structure,imported_structure=imported_structure,renders=renders,
                preserved_geometry_claim='None: old generic study preserved separately; new assembly authored',
                acceptance='Actual source-bound native/import verification; final artistic acceptance and gameplay calibration open')
    (MEDIA/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('BR22_NATIVE_GLB_VERIFIED',len(native),error,flush=True)


if __name__=='__main__':main()
