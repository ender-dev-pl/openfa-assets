# SPDX-License-Identifier: MIT
"""Blender smoke proof for unchanged restored finished native/GLB station pairs."""
import hashlib,json,struct,sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
import argparse
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=args.output.resolve();OUT.mkdir(parents=True,exist_ok=True)
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def geometry():
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render]
    assert objects,'Missing station mesh'
    points=[o.matrix_world@Vector(corner) for o in objects for corner in o.bound_box]
    minimum=[min(p[i] for p in points) for i in range(3)];maximum=[max(p[i] for p in points) for i in range(3)]
    triangles=0
    for obj in objects:
        mesh=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh();mesh.calc_loop_triangles();triangles+=len(mesh.loop_triangles);obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
    missing=[]
    for image in bpy.data.images:
        if image.users and image.source=='FILE' and not image.packed_file and image.filepath and not Path(bpy.path.abspath(image.filepath)).is_file():missing.append(image.name)
    assert not missing,('Missing external textures',missing)
    return dict(meshes=len(objects),triangles=triangles,minimum=minimum,maximum=maximum)
def strip_render_metadata(path):
    data=path.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';out=[data[:8]];offset=8
    while offset<len(data):
        length=struct.unpack_from('>I',data,offset)[0];kind=data[offset+4:offset+8];chunk=data[offset:offset+length+12]
        if kind not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'}:out.append(chunk)
        offset+=length+12
    path.write_bytes(b''.join(out))
def render(path,bounds):
    scene=bpy.context.scene
    for obj in list(scene.objects):
        if obj.type in {'LIGHT','CAMERA'}:bpy.data.objects.remove(obj,do_unlink=True)
    scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=True
    scene.render.resolution_x=384;scene.render.resolution_y=384;scene.render.resolution_percentage=100;scene.render.film_transparent=True
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    world=bpy.data.worlds.new('ProofWorld');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.3,.35,.4,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
    center=Vector([(a+b)/2 for a,b in zip(bounds['minimum'],bounds['maximum'])]);extent=max(b-a for a,b in zip(bounds['minimum'],bounds['maximum']))
    camera_data=bpy.data.cameras.new('ProofCamera');camera=bpy.data.objects.new('ProofCamera',camera_data);scene.collection.objects.link(camera);scene.camera=camera;camera.location=center+Vector((1,-1.45,1.05))*extent;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.type='ORTHO';camera_data.ortho_scale=extent*1.5;camera_data.clip_end=extent*50
    for n,(direction,power) in enumerate([((1,-2,3),1500),((-2,-1,1),900),((0,2,2),1200)]):
        data=bpy.data.lights.new('ProofLight'+str(n),'AREA');data.energy=power;data.shape='DISK';data.size=extent*2;light=bpy.data.objects.new(data.name,data);scene.collection.objects.link(light);light.location=center+Vector(direction)*extent;light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);strip_render_metadata(path)
rows=[]
for station in json.loads((ROOT/'project/orbital-station-variants.json').read_text())['stations']:
    pair=station['finished'];native=ROOT/pair['blend'];export=ROOT/pair['glb'];assert sha(native)==pair['blend_sha256'] and sha(export)==pair['glb_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(native));bpy.context.scene.frame_set(1);a=geometry();native_image=OUT/(station['culture']+'-native.png');render(native_image,a)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(export));bpy.context.scene.frame_set(1);b=geometry();glb_image=OUT/(station['culture']+'-glb.png');render(glb_image,b)
    difference=max(abs(x-y) for key in ['minimum','maximum'] for x,y in zip(a[key],b[key]));extent=max(y-x for x,y in zip(a['minimum'],a['maximum']));assert difference<max(.0001,extent*.0001),('Native/import bounds differ',station['id'],difference)
    row=dict(id=station['id'],culture=station['culture'],blend=pair['blend'],glb=pair['glb'],blend_sha256=sha(native),glb_sha256=sha(export),native=a,imported=b,bounds_error=difference,renders={native_image.name:sha(native_image),glb_image.name:sha(glb_image)},scope='Restored exact bytes: native load, independent import, bounds and rendered visibility; no new visual or game integration acceptance')
    rows.append(row);(OUT/'runtime.json').write_text(json.dumps(dict(blender=bpy.app.version_string,models=rows),indent=2)+'\n',encoding='utf-8');print('FINISHED_STATION_RUNTIME_OK',station['culture'],difference,flush=True)
assert len(rows)==6
