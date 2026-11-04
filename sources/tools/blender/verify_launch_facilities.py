"""Validate real native/imported launch poses, per-mesh geometry, and clear mouths."""
import argparse
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from launch_facility_recipes import CONFIRMED
from build_launch_facilities import preview_ground
AUDIT=ROOT/'sources/docs/reconstruction/models/launch-facility-animation-audit.json'


def vertices(obj):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluated.to_mesh()
    points=sorted(set(tuple(round(v,4) for v in evaluated.matrix_world @ vertex.co) for vertex in mesh.vertices))
    evaluated.to_mesh_clear()
    return points


def meshes():
    return [obj for obj in bpy.context.scene.objects if obj.type=='MESH' and not obj.get('preview_only')]


def sample(frames):
    states={}
    for frame in frames:
        bpy.context.scene.frame_set(frame)
        states[frame]={obj.name:vertices(obj) for obj in meshes()}
    return states


def hit_height(x,y):
    heights=[]
    for obj in meshes():
        evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()); mesh=evaluated.to_mesh()
        tree=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in mesh.vertices],
                                 [list(p.vertices) for p in mesh.polygons],all_triangles=False)
        hit,normal,index,distance=tree.ray_cast(Vector((x,y,10)),Vector((0,0,-1)),30)
        evaluated.to_mesh_clear()
        if hit is not None: heights.append(hit.z)
    return max(heights,default=-20)


def clear_mouth(meta):
    radius=meta['aperture_radius']*.72
    threshold=meta.get('floor_height',.05)+.015
    samples=[(0,0)]+[(radius*math.cos(i*math.tau/8),radius*math.sin(i*math.tau/8)) for i in range(8)]
    heights=[hit_height(x,y) for x,y in samples]
    # A spindle mouth narrows into its support column. The visible top aperture
    # must be clear above the rim; its centre must stay open down to the floor.
    if meta['key']=='MK11':
        assert heights[0]<=threshold,('Blocked centre',heights)
        assert max(heights)<.98,('Blocked mouth',heights)
    else:
        assert max(heights)<=threshold,(meta['key'],'Blocked open aperture',heights)
    return heights


def verify(record):
    folder=ROOT/'sources/docs/assets/reconstruction/launch-facilities'/record['culture']/record['key'].lower()
    if not folder.exists():
        print('RETAINED_SOURCE',record['key'],flush=True)
        return
    media=ROOT/'gallery/media/docs/assets/reconstruction/launch-facilities'/record['culture']/record['key'].lower()
    meta=json.loads((folder/'model.json').read_text()); frames=[1,16,31,46,61]
    bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'))
    scene=bpy.context.scene; native=sample(frames)
    assert native[1]==native[61],record['key']+' closed cycle differs'
    moving=[name for name in native[1] if native[1][name]!=native[31][name]]
    assert bool(moving)==bool(meta['moving_meshes']),('Missing/unsolicited motion',record['key'])
    scene.frame_set(31);native_heights=clear_mouth(meta)
    for obj in list(scene.objects):
        if obj.type in ['MESH','EMPTY']:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(folder/'model.glb'));scene.render.fps=30
    imported=sample(frames)
    assert all(native[f].keys()==imported[f].keys() for f in frames),record['key']+' mesh populations differ'
    # Export duplicates vertices at UV/normal seams. Compare evaluated world-space
    # position populations rather than an exporter-specific vertex order.
    assert all(len(native[f][n])==len(imported[f][n]) for f in frames for n in native[f]),record['key']+' vertex populations differ'
    error=max(abs(a-b) for f in frames for n in native[f] for v,w in zip(native[f][n],imported[f][n]) for a,b in zip(v,w))
    assert error<=.0003,(record['key'],error)
    scene.frame_set(31);imported_heights=clear_mouth(meta)
    if meta.get('terrain_cutout_fraction'): preview_ground(meta['aperture_radius'])
    scene.render.filepath=str(media/'imported-open.png');bpy.ops.render.render(write_still=True)
    report=dict(id=record['id'],key=record['key'],frames=frames,maximum_vertex_error=error,
                moving_mesh_names=moving,closed_cycle_equal=True,
                native_open_aperture_heights=native_heights,imported_open_aperture_heights=imported_heights,
                permanently_open=meta['fixed_open'])
    (media/'validation.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('LAUNCH_FACILITY_NATIVE_IMPORT_OK',record['key'],error,len(moving),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('keys',nargs='*');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    for record in json.loads(AUDIT.read_text())['records']:
        if record['key'] in (args.keys or CONFIRMED):verify(record)


if __name__=='__main__':main()
