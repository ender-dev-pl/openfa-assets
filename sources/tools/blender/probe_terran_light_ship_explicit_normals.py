"""In-memory native corner-normal semantics probe; never saves existing assets."""
import json
from pathlib import Path
import sys
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_terran_light_ship_runtime import REPO, VIEWS, render
from audit_transporter_runtime import sha
from catalogue_rendering import evaluated_points, fit_camera

OUTPUT = REPO / 'docs/assets/reconstruction/evidence/terran-light-ship-explicit-normals'


def main():
    for slug in ['combat-eagle', 'scoutship']:
        source = REPO / 'docs/assets/reconstruction/ships/terran' / slug
        baseline_path = REPO / 'docs/assets/reconstruction/evidence/terran-light-ship-runtime' / slug / 'runtime-audit.json'
        baseline = json.loads(baseline_path.read_text())
        assert baseline['sources'] == {name:sha(source/name) for name in baseline['sources']}
        bpy.ops.wm.open_mainfile(filepath=str(source/'model.blend'))
        meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        points = evaluated_points(meshes)
        cameras = {}
        for name, direction in VIEWS:
            fit_camera(bpy.context.scene, points, direction);cam = bpy.context.scene.camera
            cameras[name] = (cam.location.copy(), cam.rotation_euler.copy(), cam.data.ortho_scale)
        graph = bpy.context.evaluated_depsgraph_get()
        copies = []
        for obj in meshes:
            mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(graph), preserve_all_data_layers=True, depsgraph=graph)
            normals = [tuple(n.vector) for n in mesh.corner_normals]
            copies.append((obj, mesh, normals))
        evidence = {}
        for obj, mesh, normals in copies:
            evidence[obj.name] = dict(vertices=len(mesh.vertices), faces=len(mesh.polygons),
                original_flat_faces=sum(not p.use_smooth for p in mesh.polygons), corners=len(normals))
            obj.modifiers.clear()
            obj.data = mesh
            for face in mesh.polygons: face.use_smooth = True
            mesh.normals_split_custom_set(normals)
            assert mesh.has_custom_normals
        folder = OUTPUT/slug;folder.mkdir(parents=True,exist_ok=True)
        render(folder, 'explicit-native', cameras)
        assert baseline['sources'] == {name:sha(source/name) for name in baseline['sources']}
        report = dict(issue=1102, probe_sha256=sha(Path(__file__)), baseline_sha256=sha(baseline_path),
            sources=baseline['sources'], objects=evidence, source_assets_unchanged=True,
            render_sha256={p.name:sha(p) for p in folder.glob('*.png')},
            scope='Native evaluated geometry copied in memory, all faces smooth with captured native corner vectors assigned explicitly. No asset save/export or artistic acceptance.')
        (folder/'probe.json').write_text(json.dumps(report,indent=2)+'\n')
        print('LIGHT_SHIP_EXPLICIT_NORMAL_PROBE_OK',slug,len(meshes),flush=True)


if __name__ == '__main__': main()
