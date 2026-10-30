"""Reopen RI09 Blend/GLB, verify actual structure, UVs and authored texture pixels."""
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
from build_rigellian_construction import ROOT,VIEWS
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_construction_parts import CENTRES,SLOT_ANGLES,DENTS
from verify_assault_fighter import check_meshes
from verify_cannon_equipment import ray
from verify_nuclear_missile import geometry_bounds
from verify_rigellian_filtration import material_values


def texture_evidence(meshes):
    evidence={}
    for name,size in [('RI09 | worn blue grey casting',1024),('RI09 | worn planar casting caps',512)]:
        material=bpy.data.materials[name];shader=material.node_tree.nodes.get('Principled BSDF')
        texture=shader.inputs['Base Color'].links[0].from_node;colour=texture.image
        assert list(colour.size)==[size,size] and colour.packed_file
        rough=shader.inputs['Roughness'].links[0].from_node;channel=0
        if rough.type in ['SEPARATE_COLOR','SEPRGB']: channel=1;rough=rough.inputs[0].links[0].from_node
        assert rough.type=='TEX_IMAGE' and rough.image.packed_file
        evidence[name]=dict(colour=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in colour.pixels[:])).hexdigest(),
            roughness=hashlib.sha256(bytes(round(max(0,min(1,v))*255) for v in rough.image.pixels[:][channel::4])).hexdigest())
    mapped=[]
    for obj in meshes:
        if not any(m.name=='RI09 | worn blue grey casting' for m in obj.data.materials): continue
        assert obj.data.uv_layers.active is not None
        points=[obj.matrix_world @ v.co for v in obj.data.vertices]
        xmin=min(v.x for v in points);xmax=max(v.x for v in points)
        ymin=min(v.y for v in points);ymax=max(v.y for v in points)
        low=min(v.z for v in points);high=max(v.z for v in points)
        cx=(xmin+xmax)/2;cy=(ymin+ymax)/2
        uv=obj.data.uv_layers.active
        for face in obj.data.polygons:
            planar=obj.data.materials[face.material_index].name=='RI09 | worn planar casting caps'
            for index in face.loop_indices:
                point=points[obj.data.loops[index].vertex_index];u,v=uv.data[index].uv
                assert math.isfinite(u) and math.isfinite(v)
                if planar:
                    assert min(abs(point.z-low),abs(point.z-high))<1e-5
                    assert abs(u-(point.x-xmin)/(xmax-xmin))<1e-5
                    assert abs(v-(point.y-ymin)/(ymax-ymin))<1e-5
                else:
                    expected=(math.atan2(point.y-cy,point.x-cx)+math.pi)/math.tau
                    assert abs((u-expected+.5)%1-.5)<1e-5 and abs(v-point.z/1.6)<1e-5
        used={obj.data.materials[f.material_index].name for f in obj.data.polygons}
        assert used=={'RI09 | worn blue grey casting','RI09 | worn planar casting caps'}
        mapped.append(obj.name)
    assert len(mapped)==6
    assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
    return dict(materials=evidence,mapped_solids=sorted(mapped))


def structure(meshes):
    bpy.context.view_layer.update();root=bpy.data.objects['PlacementRoot']
    assert all(obj.parent==root for obj in meshes)
    assert root.location.length<1e-6 and root.rotation_euler.to_matrix().is_identity and all(abs(v-1)<1e-6 for v in root.scale)
    for i,(cx,cy) in enumerate(CENTRES):
        ring=bpy.data.objects[f'RI09 open annular platform {i}']
        assert all(ray(obj,(cx,cy,3),(0,0,-1)) is None for obj in meshes),'Annular centre must stay open through the assembly'
        axis=Vector((cx,cy,.18))
        for j,phi in enumerate(SLOT_ANGLES):
            normal=Vector((math.cos(phi),math.sin(phi),0))
            floor=ray(ring,axis+normal*2,-normal);assert floor is not None
            radius=(floor-axis).dot(normal);assert .895<radius<.915,('Channel depth',radius)
            backing=bpy.data.objects[f'RI09 ring {i} channel {j} backing']
            assert ray(backing,axis,normal).dot(normal)<floor.dot(normal)<ray(backing,axis+normal*2,-normal).dot(normal)
        phi,z,depth=DENTS[i];normal=Vector((math.cos(phi),math.sin(phi),0));axis=Vector((cx,cy,z))
        dent=ray(ring,axis+normal*2,-normal)
        assert depth*.65<.95-(dent-axis).dot(normal)<depth*1.5,'Actual casting dent missing'
    hood=bpy.data.objects['RI09 raised circular machinery hood'];floor=bpy.data.objects['RI09 hood recessed inspection floor']
    bottom=ray(hood,(0,.32,3),(0,0,-1));assert abs(bottom.z-1.36)<.001
    assert ray(floor,(0,.32,0),(0,0,1)).z<bottom.z<ray(floor,(0,.32,3),(0,0,-1)).z
    column=bpy.data.objects['RI09 central raised support column'];spine=bpy.data.objects['RI09 longitudinal cast support spine']
    assert ray(column,(0,.12,-1),(0,0,1)).z<ray(spine,(0,.12,3),(0,0,-1)).z
    assert ray(column,(0,.12,3),(0,0,-1)).z>ray(hood,(0,.12,0),(0,0,1)).z
    contact=audit();assert len(contact['components'])==1,contact['components']
    bounds=geometry_bounds(meshes);assert min(bounds[:2])>=-2 and max(bounds[3:5])<=2 and abs(bounds[2])<.001
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
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']==meta['id'] and root['footprint_width']==root['footprint_height']==4
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
    report=dict(issue=979,revision=meta['revision'],blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),materials=materials,bounds=native,texture_pixels=textures,
        contact_diagnostics=dict(native=contacts,glb=imported_contacts),
        checks=['Native/GLB topology, material values, bounds and identity placement',
                'Two genuinely open annular centres and ten recessed channels with embedded backings',
                'Measured geometric ring dents, hood inspection recess/floor and column support overlaps',
                'Packed authored images and matching colour/roughness pixels; planar/cylindrical wear UVs on six castings',
                'Connected contact sample graph; not exhaustive intersection proof'],
        final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('RIGELLIAN_CONSTRUCTION_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
