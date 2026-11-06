"""Reopen RI16 Blend/GLB, verify actual structure, UVs and authored texture pixels."""
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_rigellian_cpu_contacts import audit
from build_openfa_assets import setup_scene
from build_refined_terran import render_to
from build_rigellian_shield_generator import ROOT,VIEWS
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_shield_generator_parts import PROFILES,DENTS,PAINT,CENTRES,ANGLES
from manufactured_vessels import profile_radius
from verify_assault_fighter import check_meshes
from verify_cannon_equipment import ray
from verify_nuclear_missile import geometry_bounds
from verify_rigellian_filtration import material_values


def texture_evidence(meshes):
    evidence={}
    for name,size in [('RI16 | aged bronze head',1024),('RI16 | aged support alloy',1024),('RI16 | weathered green housings',1024)]+[(f'RI16 | {style} planar caps',512) for style in ['bronze','grey','green']]:
        material=bpy.data.materials[name];shader=material.node_tree.nodes.get('Principled BSDF')
        texture=shader.inputs['Base Color'].links[0].from_node;colour=texture.image
        assert list(colour.size)==[size,size] and colour.packed_file
        rough=shader.inputs['Roughness'].links[0].from_node;channel=0
        if rough.type in ['SEPARATE_COLOR','SEPRGB']: channel=1;rough=rough.inputs[0].links[0].from_node
        assert rough.type=='TEX_IMAGE' and rough.image.packed_file
        evidence[name]=dict(colour=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in colour.pixels[:])).hexdigest(),
            roughness=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in rough.image.pixels[:][channel::4])).hexdigest())
    cap_planes=0
    for obj in meshes:
        if obj.name not in PAINT: continue
        style=PAINT[obj.name];cx,cy=CENTRES[obj.name]
        vertices=[(obj.matrix_world @ v.co)-Vector((cx,cy,0)) for v in obj.data.vertices];low=min(p.z for p in vertices);high=max(p.z for p in vertices)
        radii={z:max(math.hypot(p.x,p.y) for p in vertices if abs(p.z-z)<1e-6) for z in [low,high]}
        seen=set()
        for face in obj.data.polygons:
            shader=obj.data.materials[face.material_index].node_tree.nodes.get('Principled BSDF')
            texture=shader.inputs['Base Color'].links[0].from_node
            uv_name=texture.inputs['Vector'].links[0].from_node.uv_map if texture.inputs['Vector'].is_linked else None
            uv=obj.data.uv_layers[uv_name] if uv_name else obj.data.uv_layers.active
            points=[(obj.matrix_world @ obj.data.vertices[obj.data.loops[index].vertex_index].co)-Vector((cx,cy,0)) for index in face.loop_indices]
            cap_z=next((z for z in [low,high] if all(abs(p.z-z)<1e-6 for p in points)),None)
            if cap_z is not None:
                seen.add(cap_z);assert obj.data.materials[face.material_index].name==('RI16 | '+style+' planar caps')
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv
                    assert abs(u-(.5+point.x/(2*radii[cap_z])))<1e-5 and abs(v-(.5+point.y/(2*radii[cap_z])))<1e-5,'End cap must use planar XY mapping'
            else:
                assert obj.data.materials[face.material_index].name=={'bronze':'RI16 | aged bronze head','grey':'RI16 | aged support alloy','green':'RI16 | weathered green housings'}[style]
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv;expected=(math.atan2(point.y,point.x)+math.pi)/math.tau
                    assert abs((u-expected+.5)%1-.5)<1e-5 and abs(v-point.z/3.0)<1e-5,'Incorrect cylindrical side mapping'
        assert len(seen)==2;cap_planes+=len(seen)
    assert cap_planes==20
    assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
    return dict(materials=evidence,planar_cap_surfaces=cap_planes)


def structure(meshes):
    bpy.context.view_layer.update();root=bpy.data.objects['PlacementRoot']
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-5
    assert all(obj.parent==root for obj in meshes)
    for name,profile in PROFILES.items():
        phi,z,depth=DENTS[name];n=Vector((math.cos(phi),math.sin(phi),0));cx,cy=CENTRES[name]
        hit=ray(bpy.data.objects[name],Vector((cx,cy,z))+n*2,-n)
        assert depth*.65<profile_radius(profile,z)-math.hypot(hit.x-cx,hit.y-cy)<depth*1.45,(name,'Geometric dent missing')
    head=bpy.data.objects['RI16 bronze generator head']
    assert ray(head,(2,0,2.56),(-1,0,0)).x<.175,'Missing head assembly groove'
    assert ray(head,(2,0,2.10),(-1,0,0)).x<.11,'Head must retain its narrow waist'
    for i,phi in enumerate(ANGLES):
        n=Vector((math.cos(phi),math.sin(phi),0));c=n*.45
        pod=bpy.data.objects[f'RI16 green lower housing {i}'];foot=bpy.data.objects[f'RI16 ground foot {i}']
        stem=bpy.data.objects[f'RI16 housing foot stem {i}'];rod=bpy.data.objects[f'RI16 vertical alloy support {i}'];brace=bpy.data.objects[f'RI16 housing radial brace {i}']
        for a,b,z in [(foot,stem,.07),(stem,pod,.30)]:
            assert ray(a,c+Vector((0,0,z)),n) is not None and ray(b,c+Vector((0,0,z)),n) is not None,(a.name,b.name,'Assembly overlap missing')
        origin=Vector((0,0,1.68));near=ray(rod,origin,n);far=ray(rod,n*2+origin,-n)
        assert near is not None and far is not None
        assert ray(head,n*2+origin,-n).dot(n)>near.dot(n),'Support must enter head flange'
        for other,z in [(rod,.46),(pod,.53)]:
            origin=Vector((0,0,z))
            near_a=ray(other,origin,n);far_a=ray(other,n*2+origin,-n)
            near_b=ray(brace,origin,n);far_b=ray(brace,n*2+origin,-n)
            assert all(value is not None for value in [near_a,far_a,near_b,far_b])
            assert max(near_a.dot(n),near_b.dot(n))<min(far_a.dot(n),far_b.dot(n)),(i,other.name,'Brace gap')
        hit=ray(pod,c+Vector((2,0,.755)),(-1,0,0));assert hit.x-c.x<.336,'Missing green housing assembly groove'
        screw=bpy.data.objects[f'RI16 flange captive screw {i}'];p=screw.matrix_world.translation
        skin=ray(head,p+Vector((0,0,3)),(0,0,-1))
        assert ray(screw,p-Vector((0,0,3)),(0,0,1)).z<skin.z<ray(screw,p+Vector((0,0,3)),(0,0,-1)).z
    bounds=geometry_bounds(meshes)
    assert min(bounds[:2])>=-1 and max(bounds[3:5])<=1 and abs(bounds[2])<.001 and abs(bounds[5]-2.86)<.001
    assert not any(obj.animation_data for obj in meshes)
    return bounds,audit()


def main():
    meta=json.loads((ROOT/'model.json').read_text());wear=json.loads((ROOT/'authored-wear.json').read_text())
    for field,name in [('generator_sha256','build_rigellian_shield_generator.py'),('parts_sha256','rigellian_shield_generator_parts.py')]:
        assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==meta[field]
    assert hashlib.sha256(Path(__file__).with_name('author_shield_generator_wear.py').read_bytes()).hexdigest()==wear['generator_sha256']
    for name,digest in meta['helper_sha256'].items():
        assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==digest
    repo=Path(__file__).resolve().parents[2]
    for field,name in [('reference_sha256','rigellian-building-references.json'),('functional_source_sha256','functional-text-index.json')]:
        assert hashlib.sha256((repo/'docs/reconstruction/models'/name).read_bytes()).hexdigest()==meta[field]
    for ext in ['blend','glb']: assert hashlib.sha256((ROOT/f'model.{ext}').read_bytes()).hexdigest()==meta[ext+'_sha256']
    assert hashlib.sha256((ROOT/'authored-wear.json').read_bytes()).hexdigest()==meta['authored_wear_sha256']
    for name,digest in wear['images'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'))
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH'];check_meshes(meshes,allow_packed_images=True)
    native,contacts=structure(meshes);textures=texture_evidence(meshes);materials=material_values(meshes)
    transforms={obj.name:([list(row) for row in obj.matrix_world],geometry_bounds([obj])) for obj in meshes}
    assert len(meshes)==meta['mesh_objects'] and len(materials)==8
    assert {image.name for image in bpy.data.images if image.source=='FILE'}==set(wear['images'])
    for image in bpy.data.images:
        if image.source=='FILE': assert hashlib.sha256(image.packed_file.data).hexdigest()==wear['images'][image.name]
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']==meta['id'] and root['footprint_width']==root['footprint_height']==2
    camera=bpy.context.scene.camera
    native_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    detail_target=Vector((0,0,2.28));offset=Vector((4,-10,7)).normalized()*20
    camera.location=detail_target+offset;camera.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=1.4
    detail_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    render_to(bpy.context.scene,ROOT/'head-detail.png')
    camera.location=Vector((0,0,.45))+offset;camera.data.ortho_scale=1.7
    base_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    render_to(bpy.context.scene,ROOT/'base-detail.png')
    scene=setup_scene(900,64);bpy.ops.import_scene.gltf(filepath=str(ROOT/'model.glb'))
    imported=[obj for obj in scene.objects if obj.type=='MESH'];check_meshes(imported,allow_packed_images=True)
    exported,imported_contacts=structure(imported);assert texture_evidence(imported)==textures
    assert {obj.name for obj in imported}==set(transforms)
    for obj in imported:
        matrix,bounds=transforms[obj.name]
        assert max(abs(obj.matrix_world[i][j]-matrix[i][j]) for i in range(4) for j in range(4))<1e-5
        assert max(abs(a-b) for a,b in zip(geometry_bounds([obj]),bounds))<.002
    imported_materials=material_values(imported);assert materials.keys()==imported_materials.keys()
    for name,value in materials.items():
        other=imported_materials[name]
        assert max(abs(a-b) for a,b in zip(value[0]+value[1:],other[0]+other[1:]))<1/255+.00001
    assert len(meshes)==len(imported) and max(abs(a-b) for a,b in zip(native,exported))<.002
    scene.camera.location=native_camera[0];scene.camera.rotation_euler=native_camera[1];scene.camera.data.ortho_scale=native_camera[2]
    render_to(scene,ROOT/'imported-glb-front-quarter.png')
    scene.camera.location=detail_camera[0];scene.camera.rotation_euler=detail_camera[1];scene.camera.data.ortho_scale=detail_camera[2]
    render_to(scene,ROOT/'imported-glb-head-detail.png')
    scene.camera.location=base_camera[0];scene.camera.rotation_euler=base_camera[1];scene.camera.data.ortho_scale=base_camera[2]
    render_to(scene,ROOT/'imported-glb-base-detail.png')
    report=dict(issue=988,verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),revision=meta['revision'],blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),materials=materials,bounds=native,texture_pixels=textures,
        contact_diagnostics=dict(native=contacts,glb=imported_contacts),
        checks=['Native/GLB topology, material values, bounds and identity placement',
                'Foot/stem/housing/brace/support/head overlap and flange fastener contacts',
                'Ten geometric dents, head waist and actual head/housing assembly grooves',
                'Packed authored images, matching colour/roughness pixels and mapped UVs'],
        final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('RIGELLIAN_SHIELD_GENERATOR_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
