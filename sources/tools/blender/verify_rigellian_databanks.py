"""Reopen RI08 Blend/GLB, verify actual structure, UVs and authored texture pixels."""
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
from build_rigellian_databanks import ROOT,VIEWS
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_databanks_parts import DRUM,NECK,MIDDLE,HEAD,SLOTS,DENTS,radius
from verify_assault_fighter import check_meshes
from verify_cannon_equipment import ray
from verify_nuclear_missile import geometry_bounds
from verify_rigellian_filtration import material_values


def texture_evidence(meshes):
    evidence={}
    for name,size in [('RI08 | aged jade shell',1024),('RI08 | worn planar end caps',512)]:
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
        if not (obj.name in ['RI08 lower intake drum','RI08 solid connecting neck','RI08 flared middle housing','RI08 rounded upper head']): continue
        vertices=[obj.matrix_world @ v.co for v in obj.data.vertices];low=min(p.z for p in vertices);high=max(p.z for p in vertices)
        radii={z:max(math.hypot(p.x,p.y) for p in vertices if abs(p.z-z)<1e-6) for z in [low,high]}
        seen=set()
        for face in obj.data.polygons:
            shader=obj.data.materials[face.material_index].node_tree.nodes.get('Principled BSDF')
            texture=shader.inputs['Base Color'].links[0].from_node
            uv_name=texture.inputs['Vector'].links[0].from_node.uv_map if texture.inputs['Vector'].is_linked else None
            uv=obj.data.uv_layers[uv_name] if uv_name else obj.data.uv_layers.active
            points=[obj.matrix_world @ obj.data.vertices[obj.data.loops[index].vertex_index].co for index in face.loop_indices]
            cap_z=next((z for z in [low,high] if all(abs(p.z-z)<1e-6 for p in points)),None)
            if cap_z is not None:
                seen.add(cap_z);assert obj.data.materials[face.material_index].name=='RI08 | worn planar end caps'
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv
                    assert abs(u-(.5+point.x/(2*radii[cap_z])))<1e-5 and abs(v-(.5+point.y/(2*radii[cap_z])))<1e-5,'End cap must use planar XY mapping'
            else:
                assert obj.data.materials[face.material_index].name=='RI08 | aged jade shell'
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv;expected=(math.atan2(point.y,point.x)+math.pi)/math.tau
                    assert abs((u-expected+.5)%1-.5)<1e-5 and abs(v-point.z/5.2)<1e-5,'Incorrect cylindrical side mapping'
        assert len(seen)==2;cap_planes+=len(seen)
    assert cap_planes==8
    assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
    return dict(materials=evidence,planar_cap_surfaces=cap_planes)


def structure(meshes):
    bpy.context.view_layer.update();root=bpy.data.objects['PlacementRoot']
    assert all(obj.parent==root for obj in meshes)
    assert root.location.length<1e-6 and root.rotation_euler.to_matrix().is_identity and all(abs(v-1)<1e-6 for v in root.scale)
    drum=bpy.data.objects['RI08 lower intake drum'];neck=bpy.data.objects['RI08 solid connecting neck'];middle=bpy.data.objects['RI08 flared middle housing'];head=bpy.data.objects['RI08 rounded upper head']
    for i,phi in enumerate(SLOTS):
        normal=Vector((math.cos(phi),math.sin(phi),0));axis=Vector((0,0,.49));bottom=ray(drum,axis+normal*2,-normal)
        assert bottom.dot(normal)<.51,'Lower slots must cut actual drum'
        backing=bpy.data.objects[f'RI08 lower slot {i} recessed backing']
        assert ray(backing,axis,normal).dot(normal)<bottom.dot(normal)<ray(backing,axis+normal*2,-normal).dot(normal)
    for obj,profile,(phi,z,depth) in zip([drum,middle,head],[DRUM,MIDDLE,HEAD],DENTS):
        normal=Vector((math.cos(phi),math.sin(phi),0));hit=ray(obj,normal*2+Vector((0,0,z)),-normal)
        assert depth*.75<radius(profile,z)-math.hypot(hit.x,hit.y)<depth*1.3
    assert ray(neck,(0,0,-1),(0,0,1)).z<ray(drum,(0,0,8),(0,0,-1)).z
    assert ray(neck,(0,0,8),(0,0,-1)).z>ray(middle,(0,0,-1),(0,0,1)).z
    assert ray(head,(0,0,-1),(0,0,1)).z<ray(middle,(0,0,8),(0,0,-1)).z
    collar=bpy.data.objects['RI08 head lower machined joint']
    for i in range(8):
        phi=i*math.tau/8;normal=Vector((math.cos(phi),math.sin(phi),0));axis=Vector((0,0,2.16))
        inner=ray(collar,axis,normal);outer=ray(collar,axis+normal*2,-normal)
        skin=max(ray(body,axis+normal*2,-normal).dot(normal) for body in [head,middle])
        assert inner is not None and outer is not None and inner.dot(normal)<skin<outer.dot(normal)-.005,'Collar must cover head/housing crossing'
    fittings=[(f'RI08 lower fitting {i}',drum,phi,z) for i,(phi,z) in enumerate([(-math.pi/2-.45,.62),(-math.pi/2+.05,.62),(-math.pi/2+.05,.35)])]
    fittings += [(f'RI08 upper collar fitting {i}',middle,phi,2.08) for i,phi in enumerate([-math.pi/2-.55,-math.pi/2,-math.pi/2+.55])]
    for label,body,phi,z in fittings:
        normal=Vector((math.cos(phi),math.sin(phi),0));axis=Vector((0,0,z))
        bezel=bpy.data.objects[label+' retaining bezel'];face=bpy.data.objects[label+' inset brass face']
        assert ray(bezel,axis,normal).dot(normal)<ray(body,axis+normal*2,-normal).dot(normal)<ray(bezel,axis+normal*2,-normal).dot(normal)
        assert ray(face,axis,normal).dot(normal)<ray(bezel,axis+normal*2,-normal).dot(normal)<ray(face,axis+normal*2,-normal).dot(normal)
    bezel=bpy.data.objects['RI08 large circular pressure bezel'];face=bpy.data.objects['RI08 large circular brass pressure face']
    centre=face.matrix_world.translation;normal=face.matrix_world.to_3x3() @ Vector((0,0,1))
    tangent_x=face.matrix_world.to_3x3() @ Vector((1,0,0));tangent_y=face.matrix_world.to_3x3() @ Vector((0,1,0))
    for offset in [Vector((0,0,0)),tangent_x*.14,-tangent_x*.14,tangent_y*.14,-tangent_y*.14]:
        point=centre+offset
        back=ray(bezel,point-normal*2,normal);front=ray(bezel,point+normal*2,-normal);skin=ray(middle,point+normal*2,-normal)
        assert back.dot(normal)<skin.dot(normal)<front.dot(normal),('Large fitting root gap',tuple(offset),back.dot(normal),skin.dot(normal),front.dot(normal))
        assert ray(face,point-normal*2,normal).dot(normal)<front.dot(normal)<ray(face,point+normal*2,-normal).dot(normal)
    for i in range(32):
        angle=i*math.tau/32;point=centre+.175*(tangent_x*math.cos(angle)+tangent_y*math.sin(angle))
        back=ray(bezel,point-normal*2,normal);front=ray(bezel,point+normal*2,-normal);skin=ray(middle,point+normal*2,-normal)
        assert back is not None and front is not None and skin is not None
        assert back.dot(normal)<skin.dot(normal)<front.dot(normal),'Cast flange must embed around its perimeter'
    bowl=bpy.data.objects['RI08 silver crown fork bowl']
    for support in [obj for obj in meshes if obj.name.startswith('RI08 twin upper support')]:
        x,y,_=support.matrix_world.translation
        assert ray(support,(x,y,-1),(0,0,1)).z<ray(head,(x,y,8),(0,0,-1)).z
        assert ray(support,(x,y,8),(0,0,-1)).z>ray(bowl,(x,y,-1),(0,0,1)).z
    case=bpy.data.objects['RI08 support-mounted side equipment casing'];inset=bpy.data.objects['RI08 side-module dark front inset']
    assert ray(inset,(.22,-2,3.35),(0,1,0)).y<ray(case,(.22,-2,3.35),(0,1,0)).y<ray(inset,(.22,0,3.35),(0,-1,0)).y
    for name,x,minimum in [('RI08 silver central terminal',0,5.14),('RI08 silver side terminal',-.21,4.83),('RI08 silver side terminal.001',.21,4.83)]:
        assert ray(bpy.data.objects[name],(x,0,8),(0,0,-1)).z>minimum
    contact=audit();assert len(contact['components'])==1,contact['isolated']
    bounds=geometry_bounds(meshes);assert min(bounds[:2])>=-1 and max(bounds[3:5])<=1 and abs(bounds[2])<.001
    assert not any(obj.animation_data for obj in meshes)
    return bounds,contact


def main():
    meta=json.loads((ROOT/'model.json').read_text());wear=json.loads((ROOT/'authored-wear.json').read_text())
    for name,digest in meta['helper_sha256'].items():
        assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==digest
    for ext in ['blend','glb']: assert hashlib.sha256((ROOT/f'model.{ext}').read_bytes()).hexdigest()==meta[ext+'_sha256']
    assert hashlib.sha256((ROOT/'authored-wear.json').read_bytes()).hexdigest()==meta['authored_wear_sha256']
    for name,digest in wear['images'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'))
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH'];check_meshes(meshes,allow_packed_images=True)
    native,contacts=structure(meshes);textures=texture_evidence(meshes);materials=material_values(meshes)
    assert len(meshes)==meta['mesh_objects'] and len(materials)==8
    assert {image.name for image in bpy.data.images if image.source=='FILE'}==set(wear['images'])
    for image in bpy.data.images:
        if image.source=='FILE': assert hashlib.sha256(image.packed_file.data).hexdigest()==wear['images'][image.name]
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']==meta['id'] and root['footprint_width']==root['footprint_height']==2
    camera=bpy.context.scene.camera
    native_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    scene=setup_scene(900,64);bpy.ops.import_scene.gltf(filepath=str(ROOT/'model.glb'))
    imported=[obj for obj in scene.objects if obj.type=='MESH'];check_meshes(imported,allow_packed_images=True)
    exported,imported_contacts=structure(imported);assert texture_evidence(imported)==textures
    imported_materials=material_values(imported);assert materials.keys()==imported_materials.keys()
    for name,value in materials.items():
        other=imported_materials[name]
        assert max(abs(a-b) for a,b in zip(value[0]+value[1:],other[0]+other[1:]))<1/255+.00001
    assert len(meshes)==len(imported) and max(abs(a-b) for a,b in zip(native,exported))<.002
    scene.camera.location=native_camera[0];scene.camera.rotation_euler=native_camera[1];scene.camera.data.ortho_scale=native_camera[2]
    render_to(scene,ROOT/'imported-glb-front-quarter.png')
    report=dict(issue=978,revision=meta['revision'],blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),materials=materials,bounds=native,texture_pixels=textures,
        contact_diagnostics=dict(native=contacts,glb=imported_contacts),
        checks=['Native/GLB topology, material values, bounds and identity placement','Three actual drum slots and three measured geometric dents',
                'Neck/housing and twin support/head/crown overlaps','Six small fitting contacts and five offset roots of large circular fitting; supported side module and silver crown',
                'Packed authored images, matching colour/roughness pixels and mapped UVs','Connected contact sample graph; not exhaustive intersection proof'],
        final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('RIGELLIAN_DATABANKS_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
