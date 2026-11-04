"""In-memory flat-flag experiment; never saves or reexports existing assets."""
import json
from pathlib import Path
import sys
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_terran_light_ship_runtime import REPO, VIEWS, render
from audit_transporter_runtime import sha
from catalogue_rendering import evaluated_points, fit_camera

OUTPUT = REPO / 'docs/assets/reconstruction/evidence/terran-light-ship-normals'


def main():
    for slug in ['combat-eagle', 'scoutship']:
        source = REPO / 'docs/assets/reconstruction/ships/terran' / slug
        baseline_path = REPO / 'docs/assets/reconstruction/evidence/terran-light-ship-runtime' / slug / 'runtime-audit.json'
        baseline = json.loads(baseline_path.read_text())
        assert baseline['sources'] == {name:sha(source/name) for name in baseline['sources']}
        bpy.ops.wm.open_mainfile(filepath=str(source/'model.blend'))
        graph = bpy.context.evaluated_depsgraph_get()
        flat = []
        for obj in bpy.context.scene.objects:
            if obj.type != 'MESH': continue
            evaluated = obj.evaluated_get(graph);mesh = evaluated.to_mesh()
            if all(not f.use_smooth for f in mesh.polygons): flat.append(obj.name)
            evaluated.to_mesh_clear()
        points = evaluated_points([o for o in bpy.context.scene.objects if o.type == 'MESH'])
        cameras = {}
        for name, direction in VIEWS:
            fit_camera(bpy.context.scene, points, direction);cam = bpy.context.scene.camera
            cameras[name] = (cam.location.copy(), cam.rotation_euler.copy(), cam.data.ortho_scale)
        for obj in list(bpy.context.scene.objects):
            if obj.type == 'MESH': bpy.data.objects.remove(obj, do_unlink=True)
        bpy.ops.import_scene.gltf(filepath=str(source/'model.glb'))
        for name in flat:
            for face in bpy.data.objects[name].data.polygons: face.use_smooth = False
        folder = OUTPUT/slug;folder.mkdir(parents=True,exist_ok=True)
        render(folder, 'flat-flag-probe', cameras)
        assert baseline['sources'] == {name:sha(source/name) for name in baseline['sources']}
        report = dict(issue=1102, probe_sha256=sha(Path(__file__)), baseline_sha256=sha(baseline_path),
            sources=baseline['sources'], flat_objects=flat, source_assets_unchanged=True,
            render_sha256={p.name:sha(p) for p in folder.glob('*.png')},
            scope='Only imported meshes corresponding to entirely flat native evaluated surfaces receive flat flags, in memory. Mixed smooth/flat native surfaces are unchanged. No asset correction or acceptance.')
        (folder/'probe.json').write_text(json.dumps(report,indent=2)+'\n')
        print('LIGHT_SHIP_FLAT_PROBE_OK',slug,len(flat),flush=True)


if __name__ == '__main__': main()
