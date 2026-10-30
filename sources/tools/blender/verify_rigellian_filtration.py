"""Verify RI02 native/export geometry, physical wear, contacts and materials."""
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
from build_rigellian_filtration import ROOT,VIEWS
from catalogue_rendering import evaluated_points,fit_camera
from rigellian_filtration_parts import BODY,radius
from verify_assault_fighter import check_meshes
from verify_cannon_equipment import ray
from verify_nuclear_missile import geometry_bounds


def structure(meshes):
    bpy.context.view_layer.update();root=bpy.data.objects['PlacementRoot']
    assert all(obj.parent==root for obj in meshes)
    assert root.location.length<1e-6 and root.rotation_euler.to_matrix().is_identity
    assert all(abs(value-1)<1e-6 for value in root.scale)
    lookup={obj.name:obj for obj in meshes};body=lookup['RI02 rounded filtration pressure body']
    for i in range(8):
        phi=-math.pi/2+(i-3.5)*.13;normal=Vector((math.cos(phi),math.sin(phi),0))
        point=ray(body,normal*2+Vector((0,0,.23)),-normal)
        assert point is not None and Vector((point.x,point.y,0)).length<.735,'Lower slot must cut the real body'
    for phi,z,depth in [(-2.02,.43,.010),(-.50,1.13,.008),(1.14,.72,.012)]:
        if phi==-.50: continue  # This location is now intentionally cut by the side service channel.
        normal=Vector((math.cos(phi),math.sin(phi),0));point=ray(body,normal*2+Vector((0,0,z)),-normal)
        measured=radius(BODY,z)-math.hypot(point.x,point.y)
        assert depth*.75<measured<depth*1.3,(phi,measured)
    normal=Vector((math.cos(-.55),math.sin(-.55),0))
    for z in [.40,.78,1.12]:
        point=ray(body,normal*2+Vector((0,0,z)),-normal)
        assert point is not None and math.hypot(point.x,point.y)<.735,'Side channel must be cut into actual body'
    for row,z in enumerate([.53,.85,1.17]):
        for column,phi in enumerate([-math.pi/2-.30,-math.pi/2+.30]):
            face=lookup[f'RI02 front port {row}-{column} brass pressure face']
            normal=Vector((math.cos(phi),math.sin(phi),0))
            back=ray(face,Vector((0,0,z)),normal);skin=ray(body,normal*2+Vector((0,0,z)),-normal)
            front=ray(face,normal*2+Vector((0,0,z)),-normal)
            assert back is not None and front is not None and back.dot(normal)<skin.dot(normal)<front.dot(normal)
    contact=audit()
    assert len(contact['components'])==1,contact['isolated']
    bounds=geometry_bounds(meshes)
    assert min(bounds[:2])>=-1 and max(bounds[3:5])<=1 and abs(bounds[2])<.001
    assert not any(obj.animation_data for obj in meshes)
    return bounds,contact


def socket_value(socket,uv):
    if not socket.is_linked:
        value=socket.default_value
        return list(value) if hasattr(value,'__len__') else value
    link=socket.links[0];node=link.from_node
    if node.type=='TEX_IMAGE':
        image=node.image;x=int(uv[0]*image.size[0])%image.size[0];y=int(uv[1]*image.size[1])%image.size[1]
        offset=(y*image.size[0]+x)*4;value=list(image.pixels[offset:offset+4])
        if link.from_socket.name=='Alpha': value=value[3]
    elif node.type in ['SEPARATE_COLOR','SEPRGB']:
        value=socket_value(node.inputs[0],uv)[{'Red':0,'Green':1,'Blue':2,'R':0,'G':1,'B':2}[link.from_socket.name]]
    elif node.type=='MATH' and node.operation=='MULTIPLY':
        value=socket_value(node.inputs[0],uv)*socket_value(node.inputs[1],uv)
    else: raise AssertionError('Unverified material node '+node.type)
    return sum(value[:3])/3 if socket.type=='VALUE' and isinstance(value,list) else value


def material_values(meshes):
    result={}
    for obj in meshes:
        for index in {face.material_index for face in obj.data.polygons}:
            material=obj.material_slots[index].material;name=material.name
            if name.startswith('RI02 | aged jade shell.'): name='RI02 | aged jade shell'
            shader=material.node_tree.nodes.get('Principled BSDF')
            values=[socket_value(shader.inputs[key],(.37,.52)) for key in ['Base Color','Metallic','Roughness']]
            if name in result:
                assert max(abs(a-b) for a,b in zip(values[0]+values[1:],result[name][0]+result[name][1:]))<1/255+.00001
            result[name]=values
    return result


def texture_evidence():
    material=bpy.data.objects['RI02 rounded filtration pressure body'].data.materials[0]
    shader=material.node_tree.nodes.get('Principled BSDF')
    assert shader.inputs['Base Color'].is_linked and shader.inputs['Roughness'].is_linked
    image=shader.inputs['Base Color'].links[0].from_node.image
    texture=shader.inputs['Base Color'].links[0].from_node
    for name in ['RI02 rounded filtration pressure body','RI02 capped upper tower']:
        obj=bpy.data.objects[name];own_shader=obj.data.materials[0].node_tree.nodes.get('Principled BSDF')
        own_texture=own_shader.inputs['Base Color'].links[0].from_node
        uv_name=own_texture.inputs['Vector'].links[0].from_node.uv_map if own_texture.inputs['Vector'].is_linked else None
        uv=obj.data.uv_layers[uv_name] if uv_name else obj.data.uv_layers.active
        assert uv is not None
        for index in range(0,len(obj.data.loops),max(1,len(obj.data.loops)//100)):
            point=obj.data.vertices[obj.data.loops[index].vertex_index].co;u,v=uv.data[index].uv
            expected=(math.atan2(point.y,point.x)+math.pi)/math.tau
            assert abs((u-expected+.5)%1-.5)<1e-5 and abs(v-point.z/2.5)<1e-5,('Wrong wear UV set',name,uv.name,tuple(point),(u,v),(expected,point.z/2.5))
    assert list(image.size)==[1024,1024] and image.packed_file
    pixel_hash=hashlib.sha256(bytes(round(max(0,min(1,value))*255) for value in image.pixels[:])).hexdigest()
    assert all(image.packed_file for image in bpy.data.images if image.source=='FILE'),'External image dependency'
    rough_node=shader.inputs['Roughness'].links[0].from_node;channel=0
    if rough_node.type in ['SEPARATE_COLOR','SEPRGB']:
        channel=1;rough_node=rough_node.inputs[0].links[0].from_node
    assert rough_node.type=='TEX_IMAGE'
    rough_hash=hashlib.sha256(bytes(round(max(0,min(1,value))*255) for value in rough_node.image.pixels[:][channel::4])).hexdigest()
    return dict(colour_pixels_sha256=pixel_hash,roughness_pixels_sha256=rough_hash,
        packed_images=[image.name for image in bpy.data.images if image.source=='FILE'])


def main():
    meta=json.loads((ROOT/'model.json').read_text())
    wear=json.loads((ROOT/'authored-wear.json').read_text())
    assert hashlib.sha256((ROOT/'authored-wear.json').read_bytes()).hexdigest()==meta['authored_wear_sha256']
    for name,digest in wear['images'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'Changed authored texture '+name
    for ext in ['blend','glb']:
        assert hashlib.sha256((ROOT/f'model.{ext}').read_bytes()).hexdigest()==meta[ext+'_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'))
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    check_meshes(meshes,allow_packed_images=True);native,contacts=structure(meshes);materials=material_values(meshes)
    native_textures=texture_evidence()
    native_images=[image for image in bpy.data.images if image.source=='FILE']
    assert {image.name for image in native_images}==set(wear['images'])
    assert all(hashlib.sha256(image.packed_file.data).hexdigest()==wear['images'][image.name] for image in native_images)
    assert len(meshes)==meta['mesh_objects'] and len(materials)==7
    unused={slot.material.name for obj in meshes for slot in obj.material_slots}-materials.keys()
    assert unused=={'RI02 | brown handling stains'},unused  # Former face material is now baked into the authored map.
    root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']==meta['id'] and root['footprint_width']==root['footprint_height']==2
    scene=setup_scene(900,64);bpy.ops.import_scene.gltf(filepath=str(ROOT/'model.glb'))
    imported=[obj for obj in scene.objects if obj.type=='MESH'];check_meshes(imported,allow_packed_images=True)
    imported_textures=texture_evidence()
    assert native_textures['colour_pixels_sha256']==imported_textures['colour_pixels_sha256'],'Authored colour map changed in GLB'
    assert native_textures['roughness_pixels_sha256']==imported_textures['roughness_pixels_sha256'],'Authored roughness changed in GLB'
    exported,imported_contacts=structure(imported);exported_materials=material_values(imported)
    assert len(imported)==len(meshes) and max(abs(a-b) for a,b in zip(native,exported))<.002
    assert materials.keys()==exported_materials.keys()
    for name,values in materials.items():
        other=exported_materials[name]
        assert max(abs(a-b) for a,b in zip(values[0]+values[1:],other[0]+other[1:]))<1/255+.00001,(name,values,other)
    fit_camera(scene,evaluated_points(imported),VIEWS[0][1]);render_to(scene,ROOT/'imported-glb-front-quarter.png')
    report=dict(issue=971,revision=meta['revision'],blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),materials=materials,bounds=native,contact_diagnostics=dict(native=contacts,glb=imported_contacts),
        authored_texture_evidence=dict(native=native_textures,glb=imported_textures),
        checks=['Native/GLB topology, bounds, materials and placement hierarchy','Eight actual cut lower slots',
                'Two measured shallow geometric dents; third authored dent intersects the service-channel cut',
                'Recessed side channel at three heights','Six embedded front pressure faces',
                'Connected evaluated surface-sample contact graph in both formats; not exhaustive solid-contact proof',
                'Actual GLB render with preserved exportable weathering materials'],final_visual_acceptance=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('RIGELLIAN_FILTRATION_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
