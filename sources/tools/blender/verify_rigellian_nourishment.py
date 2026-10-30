"""Reopen RI03 Blend/GLB, verify actual structure, UVs and authored texture pixels."""
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
from build_rigellian_nourishment import ROOT,VIEWS
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_nourishment_parts import MODULE_STARTS,DENTS,module_profile,radius
from verify_assault_fighter import check_meshes
from verify_cannon_equipment import ray
from verify_nuclear_missile import geometry_bounds
from verify_rigellian_filtration import material_values


def texture_evidence(meshes):
    evidence={}
    for name,size in [('RI03 | aged jade coating',1024),('RI03 | worn planar end caps',512)]:
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
        if not (obj.name.startswith('RI03 rounded vessel') or obj.name=='RI03 flared mounting pedestal'): continue
        low=min(v.co.z for v in obj.data.vertices);high=max(v.co.z for v in obj.data.vertices)
        radii={z:max(math.hypot(v.co.x,v.co.y) for v in obj.data.vertices if abs(v.co.z-z)<1e-6) for z in [low,high]}
        seen=set()
        for face in obj.data.polygons:
            shader=obj.data.materials[face.material_index].node_tree.nodes.get('Principled BSDF')
            texture=shader.inputs['Base Color'].links[0].from_node
            uv_name=texture.inputs['Vector'].links[0].from_node.uv_map if texture.inputs['Vector'].is_linked else None
            uv=obj.data.uv_layers[uv_name] if uv_name else obj.data.uv_layers.active
            points=[obj.data.vertices[obj.data.loops[index].vertex_index].co for index in face.loop_indices]
            cap_z=next((z for z in [low,high] if all(abs(p.z-z)<1e-6 for p in points)),None)
            if cap_z is not None:
                seen.add(cap_z);assert obj.data.materials[face.material_index].name=='RI03 | worn planar end caps'
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv
                    assert abs(u-(.5+point.x/(2*radii[cap_z])))<1e-5 and abs(v-(.5+point.y/(2*radii[cap_z])))<1e-5,'End cap must use planar XY mapping'
            else:
                assert obj.data.materials[face.material_index].name=='RI03 | aged jade coating'
                for index,point in zip(face.loop_indices,points):
                    u,v=uv.data[index].uv;expected=(math.atan2(point.y,point.x)+math.pi)/math.tau
                    assert abs((u-expected+.5)%1-.5)<1e-5 and abs(v-point.z/4.2)<1e-5,'Incorrect cylindrical side mapping'
        assert len(seen)==2;cap_planes+=len(seen)
    assert cap_planes==8
    assert all(image.packed_file for image in bpy.data.images if image.source=='FILE')
    return dict(materials=evidence,planar_cap_surfaces=cap_planes)


def structure(meshes):
    bpy.context.view_layer.update();root=bpy.data.objects['PlacementRoot']
    assert all(obj.parent==root for obj in meshes)
    assert root.location.length<1e-6 and root.rotation_euler.to_matrix().is_identity and all(abs(v-1)<1e-6 for v in root.scale)
    vessels=[bpy.data.objects[f'RI03 rounded vessel {i}'] for i in range(3)]
    for i,start in enumerate(MODULE_STARTS):
        pocket=ray(vessels[i],(.08,-2,start+.45),(0,1,0))
        outside=ray(vessels[i],(-.2,-2,start+.45),(0,1,0))
        assert pocket is not None and outside is not None and pocket.y-outside.y>.05,'Recess not cut into actual vessel'
        phi,z,depth=DENTS[i];normal=Vector((math.cos(phi),math.sin(phi),0))
        hit=ray(vessels[i],normal*2+Vector((0,0,z)),-normal)
        assert depth*.75<radius(module_profile(start),z)-math.hypot(hit.x,hit.y)<depth*1.3
        neck=bpy.data.objects[f'RI03 solid brass interstage neck {i}']
        lower=bpy.data.objects['RI03 flared mounting pedestal'] if i==0 else vessels[i-1]
        neck_low=ray(neck,(0,0,-1),(0,0,1));neck_high=ray(neck,(0,0,6),(0,0,-1))
        lower_high=ray(lower,(0,0,6),(0,0,-1));upper_low=ray(vessels[i],(0,0,-1),(0,0,1))
        assert neck_low.z<lower_high.z and neck_high.z>upper_low.z,'Neck must overlap both actual axial caps'
    pedestal=bpy.data.objects['RI03 flared mounting pedestal'];closure=bpy.data.objects['RI03 pedestal brass inspection closure']
    skin=ray(pedestal,(.12,-2,.17),(0,1,0));front=ray(closure,(.12,-2,.17),(0,1,0));back=ray(closure,(.12,0,.17),(0,-1,0))
    assert front.y<skin.y<back.y,'Foot fitting must be exposed and embedded'
    contact=audit();assert len(contact['components'])==1,contact['isolated']
    bounds=geometry_bounds(meshes);assert min(bounds[:2])>=-1 and max(bounds[3:5])<=1 and abs(bounds[2])<.001
    assert not any(obj.animation_data for obj in meshes)
    return bounds,contact


def main():
    meta=json.loads((ROOT/'model.json').read_text());wear=json.loads((ROOT/'authored-wear.json').read_text())
    for ext in ['blend','glb']: assert hashlib.sha256((ROOT/f'model.{ext}').read_bytes()).hexdigest()==meta[ext+'_sha256']
    assert hashlib.sha256((ROOT/'authored-wear.json').read_bytes()).hexdigest()==meta['authored_wear_sha256']
    for name,digest in wear['images'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'))
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH'];check_meshes(meshes,allow_packed_images=True)
    native,contacts=structure(meshes);textures=texture_evidence(meshes);materials=material_values(meshes)
    assert len(meshes)==meta['mesh_objects'] and len(materials)==7
    assert {image.name for image in bpy.data.images if image.source=='FILE'}==set(wear['images'])
    for image in bpy.data.images:
        if image.source=='FILE': assert hashlib.sha256(image.packed_file.data).hexdigest()==wear['images'][image.name]
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']==meta['id'] and root['footprint_width']==root['footprint_height']==2
    scene=setup_scene(900,64);bpy.ops.import_scene.gltf(filepath=str(ROOT/'model.glb'))
    imported=[obj for obj in scene.objects if obj.type=='MESH'];check_meshes(imported,allow_packed_images=True)
    exported,imported_contacts=structure(imported);assert texture_evidence(imported)==textures
    imported_materials=material_values(imported);assert materials.keys()==imported_materials.keys()
    for name,value in materials.items():
        other=imported_materials[name]
        assert max(abs(a-b) for a,b in zip(value[0]+value[1:],other[0]+other[1:]))<1/255+.00001
    assert len(meshes)==len(imported) and max(abs(a-b) for a,b in zip(native,exported))<.002
    fit_camera(scene,evaluated_points(imported),VIEWS[0][1]);render_to(scene,ROOT/'imported-glb-front-quarter.png')
    report=dict(issue=972,revision=meta['revision'],blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),materials=materials,bounds=native,texture_pixels=textures,
        contact_diagnostics=dict(native=contacts,glb=imported_contacts),
        checks=['Native/GLB topology, material values, bounds and identity placement','Three actual cut pockets and measured geometric dents',
                'Three solid necks overlapping adjacent axial caps','Exposed and embedded low foot fitting',
                'Packed authored images, matching colour/roughness pixels and mapped UVs','Connected contact sample graph; not exhaustive intersection proof'],
        final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n');print('RIGELLIAN_NOURISHMENT_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
