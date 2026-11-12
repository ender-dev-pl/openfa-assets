"""Verify RI01 native/export structure without asserting artistic acceptance."""
import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils import Matrix

sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_assault_fighter import check_meshes
from verify_cannon_equipment import ray
from verify_nuclear_missile import geometry_bounds
from build_openfa_assets import setup_scene
from build_refined_terran import render_to

ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/buildings/rigellian/central-unit'


def structure(meshes):
    bpy.context.view_layer.update()
    root=bpy.data.objects['PlacementRoot']
    assert all(obj.parent==root for obj in meshes)
    assert max(abs(root.matrix_world[r][c]-Matrix.Identity(4)[r][c]) for r in range(4) for c in range(4))<1e-6
    lookup={obj.name:obj for obj in meshes}
    seating=ray(lookup['CPU crown brass seating ring'],(.16,0,5),(0,0,-1))
    socket=ray(lookup['CPU crown solid mounting socket'],(.16,0,5),(0,0,-1))
    assert seating is not None and socket is not None and seating.z-socket.z>.01,'Crown socket and rim must not share coplanar top faces'
    roof=lookup['CPU broad upper saucer']
    floor=ray(roof,(-.55,-.12,4),(0,0,-1))
    surround=ray(roof,(-.83,-.12,4),(0,0,-1))
    assert floor is not None and surround is not None and surround.z-floor.z>.15,'Roof well must be cut into saucer'
    assert ray(lookup['CPU roof well inner sleeve'],(-.55,-.12,4),(0,0,-1)) is None
    sleeve=lookup['CPU roof well inner sleeve'];insert=lookup['CPU roof well recessed floor']
    bottom=ray(insert,(-.55,-.12,0),(0,0,1));top=ray(insert,(-.55,-.12,4),(0,0,-1))
    assert bottom.z<floor.z<top.z,'Well floor must embed into the actual cut bottom'
    wall=ray(roof,(-.55,-.12,2.53),(1,0,0))
    outside=ray(sleeve,(1,-.12,2.53),(-1,0,0))
    assert outside.x>wall.x,'Well sleeve must embed radially into the saucer'
    inside=ray(sleeve,(-.55,-.12,2.47),(1,0,0))
    floor_edge=ray(insert,(1,-.12,2.47),(-1,0,0))
    assert floor_edge.x>inside.x,'Floor must extend into sleeve wall'
    for obj in meshes:
        if not obj.name.startswith('CPU well interior cooling fin'): continue
        x,y,_=obj.matrix_world.translation
        foot=ray(obj,(x,y,0),(0,0,1));support=ray(insert,(x,y,4),(0,0,-1))
        assert foot is not None and support is not None and foot.z<support.z,'Cooling fin must meet floor'
    neck=ray(lookup['CPU neck with actual grille opening'],(0,-2,1.65),(0,1,0))
    assert neck is not None and neck.y>0,'Front grille aperture must penetrate neck shell'
    assert len([obj for obj in meshes if obj.name.startswith('CPU grille horizontal structural fin')])==5
    for name,x,z in [('CPU crown central terminal',0,4),('CPU crown side terminal',-.30,3.8),('CPU crown side terminal.001',.30,3.8)]:
        hit=ray(lookup[name],(x,0,5),(0,0,-1))
        assert hit is not None and hit.z>z
    cap=lookup['CPU pale conformal roof service cap'];top=[];back=[]
    normals=cap.matrix_world.to_3x3().inverted().transposed()
    for face in cap.data.polygons:
        normal=(normals @ face.normal).normalized()
        if abs(normal.z)<.6: continue
        point=cap.matrix_world @ face.center
        skin=ray(roof,(point.x,point.y,4),(0,0,-1))
        assert skin is not None
        (top if normal.z>0 else back).append(point.z-skin.z)
    assert top and back
    assert min(top)>.001 and max(top)<.015,(min(top),max(top))
    assert min(back)>-.025 and max(back)<-.003,(min(back),max(back))
    assert not any(obj.animation_data for obj in meshes)
    bounds=geometry_bounds(meshes)
    assert bounds[0]>=-1.5 and bounds[1]>=-1.5 and bounds[3]<=1.5 and bounds[4]<=1.5
    assert -.001<=bounds[2]<=.001
    return bounds


def main():
    meta=json.loads((ROOT/'model.json').read_text())
    for ext in ['blend','glb']:
        assert hashlib.sha256((ROOT/f'model.{ext}').read_bytes()).hexdigest()==meta[ext+'_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'))
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    check_meshes(meshes);native=structure(meshes)
    root=bpy.data.objects['PlacementRoot']
    assert root['catalogue_id']==meta['id'] and root['footprint_width']==root['footprint_height']==3
    materials={slot.material.name for obj in meshes for slot in obj.material_slots}
    assert len(meshes)==meta['mesh_objects'] and len(materials)==6
    assert bpy.context.scene.render.film_transparent and bpy.context.scene.camera.data.type=='ORTHO'
    camera=bpy.context.scene.camera
    native_camera=(camera.location.copy(),camera.rotation_euler.copy(),camera.data.ortho_scale)
    scene=setup_scene(900,64)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'model.glb'))
    imported=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    check_meshes(imported);exported=structure(imported)
    assert len(imported)==len(meshes)
    assert {slot.material.name for obj in imported for slot in obj.material_slots}==materials
    assert max(abs(a-b) for a,b in zip(native,exported))<.002
    scene.camera.location=native_camera[0];scene.camera.rotation_euler=native_camera[1];scene.camera.data.ortho_scale=native_camera[2]
    render_to(scene,ROOT/'imported-glb-front-quarter.png')
    report=dict(issue=969,revision=meta['revision'],blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        mesh_objects=len(meshes),material_count=len(materials),bounds=native,
        checks=['Native/GLB topology, materials and evaluated vertex bounds','Identity placement root and nominal 3x3 footprint',
                'Cut roof well, open grille shell and three crown terminals','Conformal roof cap with embedded backing',
                'Actual floor/saucer, sleeve/saucer, floor/sleeve and cooling-fin/floor contacts'],
        final_visual_acceptance=False,runtime_placement_calibration=False)
    (ROOT/'technical-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('RIGELLIAN_CPU_NATIVE_GLB_OK',len(meshes),flush=True)


if __name__=='__main__': main()
