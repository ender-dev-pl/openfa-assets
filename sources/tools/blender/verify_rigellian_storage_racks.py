"""Reopen RI21 Blend/GLB, verify actual structure, UVs and authored texture pixels."""
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
from build_rigellian_storage_racks import ROOT,VIEWS
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_storage_racks_parts import PROFILES,DENTS,PAINT,CENTRES,LAYOUT,FACE_KEYS,LEVELS
from manufactured_vessels import profile_radius
from verify_assault_fighter import check_meshes
from verify_cannon_equipment import ray
from verify_nuclear_missile import geometry_bounds
from verify_rigellian_filtration import material_values


def texture_evidence(meshes):
    evidence={}
    for name,size in [('RI21 | weathered bronze housings',1024),('RI21 | bronze planar caps',512)]:
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
                seen.add(cap_z);assert obj.data.materials[face.material_index].name==('RI21 | '+style+' planar caps')
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv
                    assert abs(u-(.5+point.x/(2*radii[cap_z])))<1e-5 and abs(v-(.5+point.y/(2*radii[cap_z])))<1e-5,'End cap must use planar XY mapping'
            else:
                assert obj.data.materials[face.material_index].name=='RI21 | weathered bronze housings'
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv;expected=(math.atan2(point.y,point.x)+math.pi)/math.tau
                    assert abs((u-expected+.5)%1-.5)<1e-5 and abs(v-point.z/3.0)<1e-5,'Incorrect cylindrical side mapping'
        assert len(seen)==2;cap_planes+=len(seen)
    assert cap_planes==12
    assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
    return dict(materials=evidence,planar_cap_surfaces=cap_planes)


def inside(obj,p):
    # An oblique line avoids exact shared-edge hits on axial cylinder extrema.
    n=Vector((.173,.291,.941)).normalized();near=ray(obj,p-n*3,n);far=ray(obj,p+n*3,-n)
    return near is not None and far is not None and near.dot(n)<p.dot(n)<far.dot(n)


def structure(meshes):
    bpy.context.view_layer.update();root=bpy.data.objects['PlacementRoot']
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-5
    assert all(obj.parent==root for obj in meshes)
    for name,profile in PROFILES.items():
        phi,z,depth=DENTS[name];n=Vector((math.cos(phi),math.sin(phi),0));cx,cy=CENTRES[name]
        hit=ray(bpy.data.objects[name],Vector((cx,cy,z))+n*2,-n)
        assert depth*.65<profile_radius(profile,z)-math.hypot(hit.x-cx,hit.y-cy)<depth*1.45,(name,'Geometric dent missing')
    for tier,z in enumerate(LEVELS):
        points=[Vector((*CENTRES[LAYOUT[(tier,i)]],z)) for i in range(3)]
        for i in range(3):
            a=points[i];b=points[(i+1)%3];direction=(b-a).normalized();edge=bpy.data.objects[f'RI21 cradle edge {tier} {i}']
            for name,p in [(LAYOUT[(tier,i)],a+direction*.045),(LAYOUT[(tier,(i+1)%3)],b-direction*.045)]:
                assert inside(edge,p) and inside(bpy.data.objects[name],p),(name,'Cradle attachment missing')
        for side,index in [(-1,1),(1,2)]:
            a=Vector((side*.55,.30,z));b=points[index];direction=(b-a).normalized();tie=bpy.data.objects[f'RI21 rear cradle tie {tier} {side}'];spine=bpy.data.objects[f'RI21 rear rack spine {side}']
            assert inside(tie,a+direction*.010) and inside(spine,a+direction*.010),'Rear spine/tie gap'
            assert inside(tie,b-direction*.045) and inside(bpy.data.objects[LAYOUT[(tier,index)]],b-direction*.045),'Rear tie/housing gap'
    for side in [-1,1]:
        guide=bpy.data.objects[f'RI21 front guide {side}'];tie=bpy.data.objects[f'RI21 front guide foot tie {side}'];edge=bpy.data.objects['RI21 cradle edge 0 1']
        p=Vector((side*.13,-.225,.105));assert inside(tie,p) and inside(edge,p),'Guide/cradle gap'
        p=Vector((side*.13,-.35,.105));assert inside(tie,p) and inside(guide,p),'Guide/tie gap'
    n=Vector((0,-1,0))
    for tier,index in FACE_KEYS:
        body=bpy.data.objects[LAYOUT[(tier,index)]];bezel=bpy.data.objects[f'RI21 face bezel {tier} {index}'];face=bpy.data.objects[f'RI21 green oval face {tier} {index}'];c=face.matrix_world.translation
        tx=face.matrix_world.to_3x3() @ Vector((1,0,0));ty=face.matrix_world.to_3x3() @ Vector((0,1,0))
        for i in range(32):
            a=i*math.tau/32;p=c+.117*(tx*math.cos(a)+ty*math.sin(a))
            back=ray(bezel,p-n*2,n);front=ray(bezel,p+n*2,-n);skin=ray(body,p+n*2,-n)
            assert back is not None and front is not None and skin is not None
            assert back.dot(n)<skin.dot(n)<front.dot(n),('Face fitting root gap',tier,index,i)
        for x,y in [(0,0),(.035,0),(-.035,0),(0,.060),(0,-.060)]:
            p=c+tx*x+ty*y;surface=ray(bezel,p+n*2,-n).dot(n)
            assert ray(face,p-n*2,n).dot(n)<surface<ray(face,p+n*2,-n).dot(n),'Oval face gap'
    bounds=geometry_bounds(meshes)
    assert min(bounds[:2])>=-1.5 and max(bounds[3:5])<=1.5 and abs(bounds[2])<.001 and abs(bounds[5]-1.81)<.001
    assert not any(obj.animation_data for obj in meshes)
    return bounds,audit()


def main():
    meta=json.loads((ROOT/'model.json').read_text());wear=json.loads((ROOT/'authored-wear.json').read_text())
    for field,name in [('generator_sha256','build_rigellian_storage_racks.py'),('parts_sha256','rigellian_storage_racks_parts.py')]:
        assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==meta[field]
    assert hashlib.sha256(Path(__file__).with_name('author_storage_racks_wear.py').read_bytes()).hexdigest()==wear['generator_sha256']
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
    assert len(meshes)==meta['mesh_objects'] and len(materials)==5
    assert {image.name for image in bpy.data.images if image.source=='FILE'}==set(wear['images'])
    for image in bpy.data.images:
        if image.source=='FILE': assert hashlib.sha256(image.packed_file.data).hexdigest()==wear['images'][image.name]
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']==meta['id'] and root['footprint_width']==root['footprint_height']==3
    camera=bpy.context.scene.camera
    native_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    detail_target=Vector((0,-.20,.55));offset=Vector((4,-10,7)).normalized()*20
    camera.location=detail_target+offset;camera.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=1.25
    detail_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    render_to(bpy.context.scene,ROOT/'rack-detail.png')
    camera.location=Vector((0,0,.20))+offset;camera.data.ortho_scale=1.1
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
    render_to(scene,ROOT/'imported-glb-rack-detail.png')
    scene.camera.location=base_camera[0];scene.camera.rotation_euler=base_camera[1];scene.camera.data.ortho_scale=base_camera[2]
    render_to(scene,ROOT/'imported-glb-base-detail.png')
    report=dict(issue=993,verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),revision=meta['revision'],blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),materials=materials,bounds=native,texture_pixels=textures,
        contact_diagnostics=dict(native=contacts,glb=imported_contacts),
        checks=['Native/GLB topology, material values, bounds and identity placement',
                'Six housing/cradle joints, rear spines/ties and front guides; five oval face attachments',
                'Six geometric dents and 160 face fitting flange root samples',
                'Packed authored images, matching colour/roughness pixels and mapped UVs'],
        final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('RIGELLIAN_STORAGE_RACKS_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
