"""Evaluate native and independently imported PB26 animation and its clear aperture."""
import json
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
MODEL = ROOT/'sources/docs/assets/reconstruction/buildings/terran/landing-pad'
MEDIA = ROOT/'gallery/media/docs/assets/reconstruction/buildings/terran/landing-pad'


def vertices(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    points = sorted(set(tuple(round(v, 5) for v in evaluated.matrix_world @ vertex.co) for vertex in mesh.vertices))
    evaluated.to_mesh_clear()
    return points


def positions():
    result = {}
    for frame in [1, 16, 31, 46, 61]:
        bpy.context.scene.frame_set(frame)
        result[frame] = {obj.name: vertices(obj)
                         for obj in bpy.context.scene.objects if obj.type == 'MESH'}
    assert result[1].keys() == result[31].keys()
    moving = [name for name in result[1] if result[1][name] != result[31][name]]
    assert len(moving) > 70, len(moving)
    for name in result[1]:
        assert max(abs(a-b) for x,y in zip(result[1][name],result[61][name]) for a,b in zip(x,y)) < .00001, name
        if name not in moving:
            assert result[1][name] == result[16][name] == result[31][name], name
    for name in moving:
        assert all(abs(x) > .885 for x,y,z in result[31][name]), ('Aperture blocked', name)
    return result


def main():
    bpy.ops.wm.open_mainfile(filepath=str(MODEL/'model.blend'))
    scene=bpy.context.scene
    native=positions()
    camera=scene.camera
    camera_data=(camera.matrix_world.copy(),camera.data.ortho_scale)
    for obj in list(scene.objects):
        if obj.type in ['MESH','EMPTY']:
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(MODEL/'model.glb'))
    # glTF animation import preserves time in seconds; the source uses 30fps.
    scene.render.fps=30
    imported=positions()
    assert native.keys()==imported.keys()
    assert all(len(native[f][n]) == len(imported[f][n]) for f in native for n in native[f]), 'Vertex populations differ'
    error=max(abs(a-b) for frame in native for name in native[frame]
              for v,w in zip(native[frame][name],imported[frame][name]) for a,b in zip(v,w))
    assert error < .00003, error
    scene.frame_set(31)
    scene.camera=camera
    camera.matrix_world=camera_data[0]
    camera.data.ortho_scale=camera_data[1]
    scene.render.filepath=str(MEDIA/'imported-open.png')
    bpy.ops.render.render(write_still=True)
    report=dict(source_and_imported_frames=[1,16,31,46,61],maximum_vertex_error=error,
                moving_aperture_clear=True,closed_cycle_equal=True,static_geometry_unchanged=True)
    (MEDIA/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PB26_NATIVE_AND_IMPORT_OK',report,flush=True)


if __name__=='__main__':
    main()


