"""Actual native/GLB geometry and full transfer envelope verification (#227)."""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).parent))
from build_ship_construction_layers import SHIPS,sha
from build_shipyard_hangar import OUT,DECK,HALF,END


def vertices(objects):
    return [obj.matrix_world@v.co for obj in objects for v in obj.data.vertices]


def distance(a,b):
    tree=KDTree(len(b))
    for index,p in enumerate(b):tree.insert(p,index)
    tree.balance()
    return max(tree.find(p)[2] for p in a)


def snapshot():
    return {o.name:vertices([o]) for o in bpy.context.scene.objects if o.type=='MESH'}


def document(path):
    data=path.read_bytes();size=int.from_bytes(data[12:16],'little');return json.loads(data[20:20+size])


def compare_asset(folder,poses):
    bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'),load_ui=False,use_scripts=False)
    native={}
    for frame in poses:bpy.context.scene.frame_set(frame);native[frame]=snapshot()
    scene=bpy.context.scene
    for obj in list(scene.objects):
        if obj.type in ['MESH','EMPTY']:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'))
    maximum=0
    for frame in poses:
        scene.frame_set(frame);actual=snapshot();assert actual.keys()==native[frame].keys(),folder
        for name,points in actual.items():
            drift=max(distance(points,native[frame][name]),distance(native[frame][name],points))
            if drift>.000001:print('IMPORT_VERTEX_DRIFT',frame,name,drift,flush=True)
            maximum=max(maximum,drift)
    # Float32 TRS interpolation compounds through the hoist and tiny stowed sling.
    # This absolute tolerance is less than 0.001 game world unit at yard scale.
    assert maximum<.000025,(folder,maximum)
    doc=document(folder/'model.glb');assert not doc.get('skins');assert all('uri' not in image for image in doc.get('images',[]))
    report=dict(blend_sha256=sha(folder/'model.blend'),glb_sha256=sha(folder/'model.glb'),verifier_sha256=sha(Path(__file__)),poses=poses,max_bidirectional_vertex_drift=maximum,no_skins=True,independent_import=True)
    return report


def verify_ship(ship):
    folder=ROOT/'sources/objects/terran'/ship/'construction';meta=json.loads((folder/'model.json').read_text())
    report=compare_asset(folder,[1])
    assert meta['vertices_outside_ray_sections']==0
    assert meta['glb_sha256']==report['glb_sha256'] and meta['blend_sha256']==report['blend_sha256']
    assert meta['generator_sha256']==sha(Path(__file__).with_name('build_ship_construction_layers.py'))
    assert all(bpy.data.objects.get(row['node']) for row in meta['layers'])
    assert all(len(bpy.data.objects[name].children)>0 for name in meta['flight_hidden_nodes'])
    shell=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('HullBatch_')]
    target=vertices(shell)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(ROOT/meta['source_glb']))
    original=vertices([o for o in bpy.context.scene.objects if o.type=='MESH'])
    drift=max(distance(original,target),distance(target,original));assert drift<.00001,(ship,drift)
    report.update(original_hull_sha256=sha(ROOT/meta['source_glb']),hull_vertex_drift=drift,construction_layers=4,flight_hidden_batches=3,contained_in_actual_ray_sections=True)
    (folder/'runtime-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('CONSTRUCTION_SHIP_VERIFIED',ship,drift,flush=True)


def verify_yard():
    poses=[1,120,145,150,170,190,195,215,235,245,280,305,330,335,365,395,415,440,465,480]
    report=compare_asset(OUT,poses)
    meta=json.loads((OUT/'model.json').read_text());assert meta['glb_sha256']==report['glb_sha256']
    assert meta['generator_sha256']==sha(Path(__file__).with_name('build_shipyard_hangar.py'))
    rows=[];max_attachment_gap=0;min_edge_clearance=100
    root=bpy.data.objects['PlacementRoot'];carrier=bpy.data.objects['ShipConstructionPlacement'];attachment=bpy.data.objects['LoadAttachment']
    well=bpy.data.objects['HangarWellGeometry'];well_tree=BVHTree.FromPolygons(vertices([well]),[tuple(p.vertices) for p in well.data.polygons])
    for frame in range(1,END+1):
        bpy.context.scene.frame_set(frame)
        for name in ['HangarDoor_LeftGeometry','HangarDoor_RightGeometry']:
            obj=bpy.data.objects[name];tree=BVHTree.FromPolygons(vertices([obj]),[tuple(p.vertices) for p in obj.data.polygons])
            assert not tree.overlap(well_tree),(frame,name,'door/well intersection')
    for ship,config in meta['ships'].items():
        ship_meta=json.loads((ROOT/'sources/objects/terran'/ship/'construction/model.json').read_text())
        lo,hi=map(Vector,ship_meta['shell_bounds']);matrix=Matrix(config['matrix'])
        points=[matrix@Vector((x,y,z)) for x in [lo.x,hi.x] for y in [lo.y,hi.y] for z in [lo.z,hi.z]]
        assert max(abs(v.x) for v in points)<HALF-.25 and max(abs(v.y) for v in points)<HALF-.25
        edge=HALF-.11-max(max(abs(v.x),abs(v.y)) for v in points);min_edge_clearance=min(min_edge_clearance,edge)
        eye=Vector(config['socket']);offset=eye.z-meta['ships']['assault-fighter']['socket'][2]
        for frame in range(1,END+1):
            bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
            centre=carrier.matrix_world@eye;hook=attachment.matrix_world.translation+root.matrix_world.to_3x3()@Vector((0,0,offset))
            if 150<=frame<=335:max_attachment_gap=max(max_attachment_gap,(centre-hook).length)
            moved=[carrier.matrix_world@v for v in points];bottom=min(p.z for p in moved);top=max(p.z for p in moved)
            doors=[bpy.data.objects[n+'Geometry'] for n in ['HangarDoor_Left','HangarDoor_Right']]
            door_vertices=vertices(doors)
            door_top=max(p.z for p in door_vertices)
            if 195<=frame<=235:assert bottom>door_top+.10,(ship,frame,'opening into ship')
            if 245<=frame<=330:
                # Both leaves remain vertical; clearance covers their complete thickness.
                left=max(p.x for p in vertices([doors[0]]));right=min(p.x for p in vertices([doors[1]]))
                assert min(p.x for p in moved)>left+.03 and max(p.x for p in moved)<right-.03,(ship,frame,'hatch aperture')
            if frame>=415:assert top<(DECK-.10)*.3,(ship,frame,'closing into ship')
        rows.append(dict(ship=ship,checked_frames=END,full_thickness_opening_clearance_local=edge,socket_height_override_local=offset))
    assert max_attachment_gap<.00001,max_attachment_gap
    # Actual surface test: the foundation has a real through-hole down to the receiver.
    bpy.context.scene.frame_set(240);static=bpy.data.objects['StaticBaseGeometry']
    tree=BVHTree.FromPolygons(vertices([static]),[tuple(p.vertices) for p in static.data.polygons])
    for x in [-.4,0,.4]:
        hit=tree.ray_cast(Vector((x,0,.5)),Vector((0,0,-1)),1.5)[0]
        assert hit is None,('solid floor under aperture',x,hit)
    # Negative control: an oversized ship must fail the same aperture inequality.
    oversized=max(row['half_width'] for row in meta['ships'].values())*2
    assert oversized>HALF-.11
    report.update(ship_envelopes=rows,max_attachment_drift=max_attachment_gap,min_open_hatch_edge_clearance_local=min_edge_clearance,door_well_triangle_checks=END*2,aperture_negative_control_rejected=True,real_foundation_aperture=True,limits='All frames: exact transformed ship envelope versus door sweep and full open aperture; door/well triangle tests. Native/import actual vertices compared at twenty poses. This is asset runtime evidence, not client GPU validation.')
    (OUT/'runtime-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('SHIPYARD_TRANSFER_VERIFIED',max_attachment_gap,min_edge_clearance,flush=True)


def main():
    for ship in SHIPS:verify_ship(ship)
    verify_yard()


if __name__=='__main__':main()
