"""RI18 candidate: preserve split dome, relieve its seat and support hinge axes."""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import tempfile
import uuid
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).parent))
from build_openfa_assets import cylinder, box
from remaster_rigellian_static import closed, strip_png, fit_camera

FOLDER = ROOT/'sources/objects/rigellian/missile-launcher'
MEDIA = ROOT/'gallery/media/objects/rigellian/missile-launcher'
CYCLE = 'MissileDomeCycle'
STATES = 'MissileDomeDescriptorStates'
TARGETS = ['LaunchLeaf pointed cap -1','LaunchLeaf pointed cap 1']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_clip(name,frame):
    for obj in bpy.context.scene.objects:
        if obj.animation_data:
            obj.animation_data.action = None
            for track in obj.animation_data.nla_tracks:
                track.is_solo = False
                track.mute = track.name != name
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()


def main():
    recipe_path = FOLDER/'recipe.json'
    case = json.loads(recipe_path.read_bytes())
    source = ROOT/case['source']
    assert sha(source) == case['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene = bpy.context.scene
    scene.frame_set(1)
    bpy.context.preferences.filepaths.save_version = 0
    root = bpy.data.objects['PlacementRoot']
    assert max(abs(root.matrix_world[i][j]-(i==j)) for i in range(4) for j in range(4))<1e-6
    original_names = {obj.name for obj in scene.objects if obj.type=='MESH'}
    upper = bpy.data.objects['RI18 stepped green silo casing']
    edited = 0
    for vertex in upper.data.vertices:
        if vertex.co.z > 1.62:
            vertex.co.z = 1.62+(vertex.co.z-1.62)*(.009/.03)
            edited += 1
    assert edited > 0
    upper.data.update()
    # Preserve the established cylindrical mapping after the local seat edit.
    uv = upper.data.uv_layers.active
    for face in upper.data.polygons:
        points = [upper.data.vertices[upper.data.loops[i].vertex_index].co for i in face.loop_indices]
        if max(p.z for p in points)-min(p.z for p in points)<1e-6:
            continue
        for index,point in zip(face.loop_indices,points):
            uv.data[index].uv.y = point.z/3.0
    # Seat the existing low floor into its surrounding original floor ring.
    floor = bpy.data.objects['Recessed launch well floor']
    old_floor_radius = max(math.hypot(v.co.x,v.co.y) for v in floor.data.vertices)
    for vertex in floor.data.vertices:
        vertex.co.x *= .181/old_floor_radius
        vertex.co.y *= .181/old_floor_radius
    floor.data.update()
    # The original bisection creates planar cut faces; give those faces an
    # explicit interior projection while retaining exterior cap UVs.
    for obj in [o for o in scene.objects if o.name in ['Split pointed cap -1','Split pointed cap 1']]:
        layer = obj.data.uv_layers.active
        for face in obj.data.polygons:
            points = [obj.data.vertices[obj.data.loops[i].vertex_index].co for i in face.loop_indices]
            if all(abs(p.x)<1e-6 for p in points):
                for index,point in zip(face.loop_indices,points):
                    layer.data[index].uv = (.5+point.y/.52,(point.z-1.63)/.34)
    scuffs = []
    for obj in scene.objects:
        if obj.type=='MESH' and 'edge scuff' in obj.name:
            bpy.context.view_layer.objects.active = obj
            modifier = obj.modifiers.new('Physical thin abrasion layer','SOLIDIFY')
            modifier.thickness = .0001
            modifier.offset = 0
            bpy.ops.object.modifier_apply(modifier=modifier.name)
            scuffs.append(obj.name)
    assert len(scuffs)==6
    alloy = bpy.data.materials['RI18 | aged bronze foundation']
    support = bpy.data.materials['RI18 | weathered green casing']
    additions = []
    for sign in [-1,1]:
        pin = cylinder(f'RI18 hinge axle {sign}',(sign*.26,0,1.63),.018,.19,alloy,
                       vertices=32,rotation=(math.pi/2,0,0))
        pin.parent = root
        additions.append(pin.name)
        for side in [-1,1]:
            bearing = cylinder(f'RI18 hinge bearing {sign} {side}',(sign*.26,side*.072,1.63),.027,.026,
                               alloy,vertices=32,rotation=(math.pi/2,0,0))
            bearing.parent = root
            bracket = box(f'RI18 hinge root bracket {sign} {side}',(sign*.26,side*.072,1.600),
                          (.048,.030,.060),support,.003)
            bracket.parent = root
            additions.extend([bearing.name,bracket.name])
    # Reuse authored worn maps with explicit per-component coordinates.
    for name in additions:
        obj = bpy.data.objects[name]
        bpy.context.view_layer.objects.active = obj
        for modifier in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        data = obj.data
        while data.uv_layers:
            data.uv_layers.remove(data.uv_layers[0])
        layer = data.uv_layers.new(name='Authored surface wear')
        low = [min(v.co[i] for v in data.vertices) for i in range(3)]
        high = [max(v.co[i] for v in data.vertices) for i in range(3)]
        for face in data.polygons:
            axis = max(range(3),key=lambda i:abs(face.normal[i]))
            a,b = [i for i in range(3) if i != axis]
            for index in face.loop_indices:
                point = data.vertices[data.loops[index].vertex_index].co
                layer.data[index].uv = ((point[a]-low[a])/(high[a]-low[a]),
                                       (point[b]-low[b])/(high[b]-low[b]))
    states = [dict(descriptor=d,clip=STATES,frame=d,time_seconds=d/30,
                   opening_fraction=min(1,(d-2)/14),
                   angle_degrees=110*min(1,(d-2)/14),
                   angle_calibration='Authored monotonic interpretation; original pixels do not establish hinge angles.',
                   lower_shadow_composition_verified=False if d==17 else None)
              for d in range(2,18)]
    for name in TARGETS:
        obj = bpy.data.objects[name]
        assert len(obj.animation_data.nla_tracks)==1
        obj.animation_data.nla_tracks[0].name = CYCLE
        obj.animation_data.nla_tracks[0].strips[0].name = CYCLE
        obj.animation_data.nla_tracks[0].mute = True
        obj.animation_data.action = None
        sign = -1 if name.endswith('-1') else 1
        for state in states:
            obj.rotation_euler = (0,sign*math.radians(state['angle_degrees']),0)
            obj.keyframe_insert(data_path='rotation_euler',frame=state['frame'])
        action = obj.animation_data.action
        action.name = name+' descriptor angles'
        for curve in action.fcurves:
            for point in curve.keyframe_points:
                point.interpolation = 'CONSTANT'
        track = obj.animation_data.nla_tracks.new()
        track.name = STATES
        track.strips.new(STATES,2,action)
        obj.animation_data.action = None
    root['forward_axis'] = 'local -Y'
    root['dorsal_axis'] = 'local +Z'
    root['state_contract'] = case['state_contract']
    meshes = [obj for obj in scene.objects if obj.type=='MESH']
    assert len(additions)==10 and all(closed(obj) for obj in meshes)
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 61
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 32
    FOLDER.mkdir(parents=True,exist_ok=True)
    MEDIA.mkdir(parents=True,exist_ok=True)
    for name in TARGETS:
        for track in bpy.data.objects[name].animation_data.nla_tracks:
            track.mute = False
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH','EMPTY']:
            obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    temporary_root = ROOT/'artifacts/rigellian-remaster-temp'
    temporary_root.mkdir(parents=True,exist_ok=True)
    previous = tempfile.mkdtemp

    def workspace_temp(suffix=None,prefix=None,dir=None):
        parent = Path(dir).resolve() if dir else temporary_root
        assert parent.is_relative_to(ROOT.resolve())
        path = parent/((prefix or 'ri18-')+uuid.uuid4().hex+(suffix or ''))
        path.mkdir()
        return str(path)

    tempfile.mkdtemp = workspace_temp
    try:
        bpy.ops.export_scene.gltf(filepath=str(FOLDER/'model.glb'),export_format='GLB',use_selection=True,
                                 export_apply=True,export_extras=True,export_animations=True,
                                 export_animation_mode='NLA_TRACKS',export_frame_range=True)
    finally:
        tempfile.mkdtemp = previous
    raw = (FOLDER/'model.glb').read_bytes()
    length = struct.unpack_from('<I',raw,12)[0]
    document = json.loads(raw[20:20+length])
    clip = next(c for c in document['animations'] if c['name']==STATES)
    for sampler in clip['samplers']:
        sampler['interpolation'] = 'STEP'
    encoded = json.dumps(document,separators=(',',':')).encode()
    encoded += b' '*(-len(encoded)%4)
    rest = raw[20+length:]
    (FOLDER/'model.glb').write_bytes(struct.pack('<III',0x46546c67,2,20+len(encoded)+len(rest))+
                                    struct.pack('<II',len(encoded),0x4e4f534a)+encoded+rest)
    select_clip(CYCLE,1)
    bpy.ops.wm.save_as_mainfile(filepath=str(FOLDER/'model.blend'),compress=True)
    sys.path.insert(0,str(ROOT/'tools'))
    from publication_support import clean_blend
    path = FOLDER/'model.blend'
    path.write_bytes(clean_blend(path.read_bytes())[0])
    for name,frame in [('front-quarter',1),('half-open',16),('open',31)]:
        select_clip(CYCLE,frame)
        fit_camera((6,-13,8),meshes)
        path = MEDIA/(name+'.png')
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        strip_png(path)
    triangles = 0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        triangles += len(obj.data.loop_triangles)
    meta = dict(issue=253,id=case['id'],name='Missile Launcher',
                recipe=recipe_path.relative_to(ROOT).as_posix(),recipe_sha256=sha(recipe_path),
                mechanism_evidence='sources/docs/reconstruction/models/launch-facility-animation-audit.json',
                mechanism_sha256=sha(ROOT/'sources/docs/reconstruction/models/launch-facility-animation-audit.json'),
                source=case['source'],source_sha256=sha(source),author_sha256=sha(Path(__file__)),
                binaries={k:sha(FOLDER/('model.'+k)) for k in ['blend','glb']},
                footprint=[3,3],definition_class=14,construction_updates=30,
                triangles=triangles,mesh_nodes=len(meshes),
                local_collar_edit=dict(edited_vertices=edited,new_top=1.629,old_top=1.65,
                    method="Proportional compression above 1.62; no collapsed profile faces"),
                low_floor_seat=dict(old_radius=old_floor_radius,new_radius=.181),
                cap_cut_uv='Local planar YZ projection; exterior cap UVs retained',
                added_hinge_parts=additions,hinge_wear='Reused authored bronze/green maps with explicit local planar UVs',
                solidified_cosmetic_scuffs=scuffs,
                preserved_components=sorted(original_names-{'RI18 stepped green silo casing','Recessed launch well floor'}-set(scuffs)),
                animation=dict(mechanism_kind='ri18-supported-dome-v1',cycle_clip=CYCLE,descriptor_clip=STATES,target_nodes=TARGETS,
                               cycle_frames=[1,61],descriptor_frames=[2,17],
                               fps=30,closed_frame=1,open_frame=31,end_frame=61,
                               continuous_timing_recovered=False),states=states,
                delivery_authority='Bound runtime/visual evidence and canonical inventory registration',game_client_integration=False,final_artistic_acceptance=False)
    (FOLDER/'model.json').write_bytes((json.dumps(meta,indent=2)+'\n').encode())
    print('RI18_SUPPORTED_DOME_CANDIDATE',len(meshes),triangles,flush=True)


if __name__=='__main__':
    main()
