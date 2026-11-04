"""Reopen RI14 Blend/GLB, verify actual structure, UVs and authored texture pixels."""
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
from build_rigellian_energy_gatherer import ROOT,VIEWS
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_energy_gatherer_parts import PROFILES,DENTS,PAINT,CENTRES,CROWN
from manufactured_vessels import profile_radius
from verify_assault_fighter import check_meshes
from verify_cannon_equipment import ray
from verify_nuclear_missile import geometry_bounds
from verify_rigellian_filtration import material_values


def texture_evidence(meshes):
    evidence={}
    for name,size in [('RI14 | aged bronze housing',1024),('RI14 | weathered grey alloy',1024),('RI14 | bronze planar caps',512),('RI14 | grey planar caps',512)]:
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
        style=PAINT[obj.name]
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
                seen.add(cap_z);assert obj.data.materials[face.material_index].name==('RI14 | '+style+' planar caps')
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv
                    assert abs(u-(.5+point.x/(2*radii[cap_z])))<1e-5 and abs(v-(.5+point.y/(2*radii[cap_z])))<1e-5,'End cap must use planar XY mapping'
            else:
                assert obj.data.materials[face.material_index].name==('RI14 | aged bronze housing' if style=='bronze' else 'RI14 | weathered grey alloy')
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv;expected=(math.atan2(point.y,point.x)+math.pi)/math.tau
                    assert abs((u-expected+.5)%1-.5)<1e-5 and abs(v-point.z/4.2)<1e-5,'Incorrect cylindrical side mapping'
        assert len(seen)==2;cap_planes+=len(seen)
    assert cap_planes==10
    assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
    return dict(materials=evidence,planar_cap_surfaces=cap_planes)


def structure(meshes):
    bpy.context.view_layer.update();root=bpy.data.objects['PlacementRoot']
    assert max(abs(root.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-5
    assert all(obj.parent==root for obj in meshes)
    for name,profile in PROFILES.items():
        phi,z,depth=DENTS[name];normal=Vector((math.cos(phi),math.sin(phi),0))
        hit=ray(bpy.data.objects[name],normal*2+Vector((0,0,z)),-normal)
        assert depth*.65<profile_radius(profile,z)-math.hypot(hit.x,hit.y)<depth*1.45,(name,'Geometric dent missing')
    for a,b,z in [('RI14 twin chamber lower body','RI14 tapered grey connector',1.56),('RI14 tapered grey connector','RI14 bronze upper vessel',2.03),('RI14 bronze upper vessel','RI14 crown floor',2.80),('RI14 crown floor','RI14 central crown probe',2.79)]:
        assert ray(bpy.data.objects[a],(0,0,z),(1,0,0)) is not None and ray(bpy.data.objects[b],(0,0,z),(1,0,0)) is not None,(a,b,'Missing assembly overlap')
    crown=bpy.data.objects['RI14 open upturned crown'];floor=bpy.data.objects['RI14 crown floor']
    assert ray(crown,(2,0,2.785),(-1,0,0)).x>ray(floor,(0,0,2.785),(1,0,0)).x>ray(crown,(0,0,2.785),(1,0,0)).x
    for i,phi in enumerate([0,math.pi/2,math.pi,3*math.pi/2]):
        n=Vector((math.cos(phi),math.sin(phi),0));post=bpy.data.objects[f'RI14 crown upright {i}']
        point=n*2+Vector((0,0,3.00));outer=ray(crown,point,-n);inner=ray(crown,Vector((0,0,3.00)),n)
        assert ray(post,point,-n).dot(n)>inner.dot(n) and ray(post,Vector((0,0,3.00)),n).dot(n)<outer.dot(n)
    # Clear bowl above the floor, away from the central probe and crown uprights.
    for radius in [.12,.20,.28]:
        hit=ray(crown,(radius,0,4),(0,0,-1));floor_hit=ray(floor,(radius,0,4),(0,0,-1))
        assert floor_hit is not None and (hit is None or hit.z<floor_hit.z),'Crown must not close the aperture above its floor'
    body=bpy.data.objects['RI14 twin chamber lower body'];pipe=bpy.data.objects['RI14 silver front conduit']
    for i,z in enumerate([.20,.59,1.09,1.43]):
        shoe=bpy.data.objects[f'RI14 conduit retaining shoe {i}']
        skin=ray(body,(.20,-2,z),(0,1,0)).y
        assert ray(shoe,(.20,2,z),(0,-1,0)).y>skin>ray(shoe,(.20,-2,z),(0,1,0)).y
        assert ray(pipe,(.20,2,z),(0,-1,0)).y>ray(shoe,(.20,-2,z),(0,1,0)).y
    for i,z in enumerate([.38,1.25]):
        frame=bpy.data.objects[f'RI14 service panel frame {i}'];panel=bpy.data.objects[f'RI14 service panel {i}']
        for x in [-.17,-.08,.01]:
            for height in [z-.12,z,z+.12]:
                assert ray(frame,(x,2,height),(0,-1,0)).y>ray(body,(x,-2,height),(0,1,0)).y
                assert ray(panel,(x,2,height),(0,-1,0)).y>ray(frame,(x,-2,height),(0,1,0)).y
    vessel=bpy.data.objects['RI14 bronze upper vessel']
    for i,phi in enumerate([-math.pi/2,math.pi/6,5*math.pi/6]):
        n=Vector((math.cos(phi),math.sin(phi),0));panel=bpy.data.objects[f'RI14 upper vessel alloy inset {i}']
        for z in [2.37,2.45,2.53]:
            p=n*2+Vector((0,0,z));skin=ray(vessel,p,-n).dot(n)
            assert ray(panel,p,-n).dot(n)>skin>ray(panel,-n*2+Vector((0,0,z)),n).dot(n)
    bounds=geometry_bounds(meshes)
    assert min(bounds[:2])>=-1 and max(bounds[3:5])<=1 and abs(bounds[2])<.001 and abs(bounds[5]-3.40)<.001
    assert not any(obj.animation_data for obj in meshes)
    return bounds,audit()


def main():
    meta=json.loads((ROOT/'model.json').read_text());wear=json.loads((ROOT/'authored-wear.json').read_text())
    for field,name in [('generator_sha256','build_rigellian_energy_gatherer.py'),('parts_sha256','rigellian_energy_gatherer_parts.py')]:
        assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==meta[field]
    assert hashlib.sha256(Path(__file__).with_name('author_energy_gatherer_wear.py').read_bytes()).hexdigest()==wear['generator_sha256']
    for name,digest in meta['helper_sha256'].items():
        assert hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==digest
    for ext in ['blend','glb']: assert hashlib.sha256((ROOT/f'model.{ext}').read_bytes()).hexdigest()==meta[ext+'_sha256']
    assert hashlib.sha256((ROOT/'authored-wear.json').read_bytes()).hexdigest()==meta['authored_wear_sha256']
    for name,digest in wear['images'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'))
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH'];check_meshes(meshes,allow_packed_images=True)
    native,contacts=structure(meshes);textures=texture_evidence(meshes);materials=material_values(meshes)
    transforms={obj.name:([list(row) for row in obj.matrix_world],geometry_bounds([obj])) for obj in meshes}
    assert len(meshes)==meta['mesh_objects'] and len(materials)==7
    assert {image.name for image in bpy.data.images if image.source=='FILE'}==set(wear['images'])
    for image in bpy.data.images:
        if image.source=='FILE': assert hashlib.sha256(image.packed_file.data).hexdigest()==wear['images'][image.name]
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']==meta['id'] and root['footprint_width']==root['footprint_height']==2
    camera=bpy.context.scene.camera
    native_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    detail_target=Vector((0,0,2.85));offset=Vector((4,-10,7)).normalized()*20
    camera.location=detail_target+offset;camera.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=1.55
    detail_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    render_to(bpy.context.scene,ROOT/'crown-detail.png')
    camera.location=Vector((0,0,.80))+offset;camera.data.ortho_scale=1.8
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
    render_to(scene,ROOT/'imported-glb-crown-detail.png')
    scene.camera.location=base_camera[0];scene.camera.rotation_euler=base_camera[1];scene.camera.data.ortho_scale=base_camera[2]
    render_to(scene,ROOT/'imported-glb-base-detail.png')
    report=dict(issue=986,verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),revision=meta['revision'],blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),materials=materials,bounds=native,texture_pixels=textures,
        contact_diagnostics=dict(native=contacts,glb=imported_contacts),
        checks=['Native/GLB topology, material values, bounds and identity placement',
                'Body/connector/vessel/floor/probe contacts, open crown, upright/floor joins and conduit retainers',
                'Four geometric dents, service panels and upper vessel inset contacts',
                'Packed authored images, matching colour/roughness pixels and mapped UVs'],
        final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('RIGELLIAN_ENERGY_GATHERER_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
